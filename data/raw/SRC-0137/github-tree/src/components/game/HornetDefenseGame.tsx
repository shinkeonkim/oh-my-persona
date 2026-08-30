import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface HornetTarget {
  id: number;
  x: number;
  y: number;
  speed: number;
  angle: number;
  size: number;
  hit: boolean;
  spawnedAt: number;
}

interface Props {
  /** 'scout' = easier (1-2 hornets), 'attack' = harder (5-8 hornets) */
  mode: 'scout' | 'attack';
  /** Has trap equipped? Slows hornets */
  hasTrap: boolean;
  onComplete: (result: { killed: number; total: number; success: boolean }) => void;
}

const GAME_DURATION_MS = 6000; // 6 seconds
const SPAWN_INTERVAL_MS = 800;

export default function HornetDefenseGame({ mode, hasTrap, onComplete }: Props) {
  const [hornets, setHornets] = useState<HornetTarget[]>([]);
  const [killed, setKilled] = useState(0);
  const [timeLeft, setTimeLeft] = useState(GAME_DURATION_MS);
  const [started, setStarted] = useState(false);
  const [finished, setFinished] = useState(false);
  const [combo, setCombo] = useState(0);
  const [showCombo, setShowCombo] = useState(false);
  const [ripples, setRipples] = useState<{ id: number; x: number; y: number }[]>([]);
  const totalSpawned = useRef(0);
  const targetCount = mode === 'scout' ? 3 : 8;
  const containerRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<number>();
  const startTimeRef = useRef(0);
  const lastSpawnRef = useRef(0);
  const idCounter = useRef(0);

  const spawnHornet = useCallback(() => {
    const side = Math.floor(Math.random() * 4); // 0=top,1=right,2=bottom,3=left
    let x: number, y: number, angle: number;
    switch (side) {
      case 0: x = Math.random() * 100; y = -5; angle = 90 + (Math.random() - 0.5) * 60; break;
      case 1: x = 105; y = Math.random() * 100; angle = 180 + (Math.random() - 0.5) * 60; break;
      case 2: x = Math.random() * 100; y = 105; angle = 270 + (Math.random() - 0.5) * 60; break;
      default: x = -5; y = Math.random() * 100; angle = 0 + (Math.random() - 0.5) * 60; break;
    }
    const baseSpeed = mode === 'scout' ? 12 : 18;
    const speed = (baseSpeed + Math.random() * 10) * (hasTrap ? 0.6 : 1);
    const newHornet: HornetTarget = {
      id: idCounter.current++,
      x, y, speed, angle,
      size: mode === 'scout' ? 44 : 36,
      hit: false,
      spawnedAt: performance.now(),
    };
    totalSpawned.current += 1;
    setHornets(prev => [...prev, newHornet]);
  }, [mode, hasTrap]);

  const startGame = useCallback(() => {
    setStarted(true);
    startTimeRef.current = performance.now();
    lastSpawnRef.current = performance.now();
    spawnHornet();
  }, [spawnHornet]);

  // Game loop
  useEffect(() => {
    if (!started || finished) return;

    const loop = () => {
      const now = performance.now();
      const elapsed = now - startTimeRef.current;
      const remaining = Math.max(0, GAME_DURATION_MS - elapsed);
      setTimeLeft(remaining);

      // Spawn new hornets
      if (now - lastSpawnRef.current > SPAWN_INTERVAL_MS && totalSpawned.current < targetCount) {
        lastSpawnRef.current = now;
        spawnHornet();
      }

      // Move hornets
      setHornets(prev => prev.map(h => {
        if (h.hit) return h;
        const dt = 0.016; // ~60fps
        const rad = (h.angle * Math.PI) / 180;
        const wobble = Math.sin(now / 300 + h.id * 2) * 1.5;
        return {
          ...h,
          x: h.x + Math.cos(rad) * h.speed * dt + wobble * dt,
          y: h.y + Math.sin(rad) * h.speed * dt,
        };
      }).filter(h => {
        if (h.hit) return true; // keep for animation
        return h.x > -15 && h.x < 115 && h.y > -15 && h.y < 115;
      }));

      if (remaining <= 0) {
        setFinished(true);
        return;
      }
      frameRef.current = requestAnimationFrame(loop);
    };

    frameRef.current = requestAnimationFrame(loop);
    return () => { if (frameRef.current) cancelAnimationFrame(frameRef.current); };
  }, [started, finished, spawnHornet, targetCount]);

  // Report result
  useEffect(() => {
    if (!finished) return;
    const timer = setTimeout(() => {
      const total = totalSpawned.current;
      const success = mode === 'scout' ? killed >= 1 : killed >= Math.ceil(total * 0.5);
      onComplete({ killed, total, success });
    }, 1500);
    return () => clearTimeout(timer);
  }, [finished, killed, mode, onComplete]);

  const handleTap = useCallback((hornetId: number) => {
    setHornets(prev => prev.map(h =>
      h.id === hornetId && !h.hit ? { ...h, hit: true } : h
    ));
    setKilled(k => k + 1);
    setCombo(c => {
      const next = c + 1;
      if (next >= 3) { setShowCombo(true); setTimeout(() => setShowCombo(false), 600); }
      return next;
    });
  }, []);

  const handleMiss = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    setCombo(0);
    // Ripple effect
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const clientX = 'touches' in e ? e.touches[0]?.clientX || 0 : e.clientX;
      const clientY = 'touches' in e ? e.touches[0]?.clientY || 0 : e.clientY;
      const x = clientX - rect.left;
      const y = clientY - rect.top;
      const id = Date.now();
      setRipples(prev => [...prev, { id, x, y }]);
      setTimeout(() => setRipples(prev => prev.filter(r => r.id !== id)), 500);
    }
  }, []);

  const timerPercent = (timeLeft / GAME_DURATION_MS) * 100;

  // Intro screen
  if (!started) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        className="fixed inset-0 z-[70] flex items-center justify-center bg-foreground/50 backdrop-blur-sm p-4">
        <motion.div initial={{ scale: 0.8 }} animate={{ scale: 1 }}
          className="game-panel w-full max-w-sm p-6 text-center">
          <div className="text-5xl mb-3 animate-float">
            {mode === 'scout' ? '⚠️' : '🚨'}
          </div>
          <h2 className="font-serif text-xl font-bold text-foreground mb-2">
            {mode === 'scout' ? '정찰 말벌 발견!' : '말벌 습격!'}
          </h2>
          <p className="text-xs text-muted-foreground mb-1 leading-relaxed">
            {mode === 'scout'
              ? '화면에 나타나는 정찰 말벌을 탭하여 포살하세요!'
              : '장수말벌 무리가 습격 중! 최대한 많이 잡으세요!'}
          </p>
          <div className="flex items-center justify-center gap-3 my-3 text-xs text-foreground">
            <span className="px-2 py-1 rounded-lg bg-secondary border border-border">⏱ {GAME_DURATION_MS / 1000}초</span>
            <span className="px-2 py-1 rounded-lg bg-secondary border border-border">🐝 {targetCount}마리</span>
            {hasTrap && <span className="px-2 py-1 rounded-lg bg-warning/15 border border-warning/30">🪤 트랩 감속</span>}
          </div>
          <button onClick={startGame}
            className="game-btn w-full py-3 honey-gradient text-primary-foreground text-base mt-2">
            ⚔️ 방어 시작!
          </button>
        </motion.div>
      </motion.div>
    );
  }

  // Result screen
  if (finished) {
    const total = totalSpawned.current;
    const success = mode === 'scout' ? killed >= 1 : killed >= Math.ceil(total * 0.5);
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        className="fixed inset-0 z-[70] flex items-center justify-center bg-foreground/50 backdrop-blur-sm p-4">
        <motion.div initial={{ scale: 0.5, rotate: -5 }} animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', damping: 15 }}
          className="game-panel w-full max-w-sm p-6 text-center">
          <div className="text-5xl mb-3">{success ? '🎉' : '😰'}</div>
          <h2 className="font-serif text-xl font-bold text-foreground mb-2">
            {success ? '방어 성공!' : '방어 실패...'}
          </h2>
          <div className="flex justify-center gap-4 mb-3 text-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">{killed}</div>
              <div className="text-[10px] text-muted-foreground">포살</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-muted-foreground">{total - killed}</div>
              <div className="text-[10px] text-muted-foreground">놓침</div>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">결과를 적용하는 중...</p>
        </motion.div>
      </motion.div>
    );
  }

  // Active game screen
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      className="fixed inset-0 z-[70] bg-foreground/60 backdrop-blur-sm"
    >
      {/* Timer bar */}
      <div className="absolute top-0 left-0 right-0 h-2 bg-secondary z-[80]">
        <motion.div
          className={`h-full transition-all duration-100 ${timerPercent > 30 ? 'bg-primary' : 'bg-danger'}`}
          style={{ width: `${timerPercent}%` }}
        />
      </div>

      {/* HUD */}
      <div className="absolute top-4 left-0 right-0 z-[80] flex justify-center gap-4 pointer-events-none">
        <div className="px-3 py-1.5 rounded-xl bg-card/90 border-2 border-border text-sm font-bold text-foreground">
          💀 {killed}/{targetCount}
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-card/90 border-2 border-border text-sm font-bold text-foreground">
          ⏱ {(timeLeft / 1000).toFixed(1)}s
        </div>
      </div>

      {/* Combo indicator */}
      <AnimatePresence>
        {showCombo && combo >= 3 && (
          <motion.div
            key="combo"
            initial={{ scale: 0, y: 20 }}
            animate={{ scale: 1.2, y: 0 }}
            exit={{ scale: 0, opacity: 0 }}
            className="absolute top-16 left-1/2 -translate-x-1/2 z-[80] px-4 py-1.5 rounded-xl bg-warning text-foreground font-bold text-sm pointer-events-none"
          >
            🔥 {combo}x 콤보!
          </motion.div>
        )}
      </AnimatePresence>

      {/* Game field */}
      <div ref={containerRef} className="absolute inset-0 overflow-hidden"
        onMouseDown={handleMiss}
        onTouchStart={handleMiss}
      >
        {/* Miss ripples */}
        <AnimatePresence>
          {ripples.map(r => (
            <motion.div
              key={r.id}
              initial={{ scale: 0, opacity: 0.6 }}
              animate={{ scale: 2, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="absolute w-12 h-12 rounded-full border-2 border-danger/50 pointer-events-none"
              style={{ left: r.x - 24, top: r.y - 24 }}
            />
          ))}
        </AnimatePresence>

        {/* Hornets */}
        <AnimatePresence>
          {hornets.map(h => (
            <motion.button
              key={h.id}
              initial={{ scale: 0 }}
              animate={h.hit ? { scale: 1.5, opacity: 0, rotate: 180 } : { scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={h.hit ? { duration: 0.3 } : { duration: 0.15 }}
              onMouseDown={(e) => { e.stopPropagation(); if (!h.hit) handleTap(h.id); }}
              onTouchStart={(e) => { e.stopPropagation(); if (!h.hit) handleTap(h.id); }}
              className="absolute cursor-pointer select-none active:scale-90 transition-transform z-[75]"
              style={{
                left: `${h.x}%`,
                top: `${h.y}%`,
                width: h.size,
                height: h.size,
                transform: 'translate(-50%, -50%)',
              }}
            >
              <span className="text-3xl drop-shadow-lg" style={{ fontSize: h.size }}>
                {h.hit ? '💥' : '🐝'}
              </span>
            </motion.button>
          ))}
        </AnimatePresence>
      </div>

      {/* Instruction */}
      <div className="absolute bottom-8 left-0 right-0 text-center pointer-events-none z-[80]">
        <span className="px-4 py-2 rounded-xl bg-card/80 border border-border text-xs text-muted-foreground font-medium">
          말벌을 탭하여 잡으세요! 🎯
        </span>
      </div>
    </motion.div>
  );
}
