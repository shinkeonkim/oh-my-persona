import { useState } from 'react';
import { type GameEvent } from '@/game/types';
import { useGame } from '@/game/GameContext';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import HornetDefenseGame from './HornetDefenseGame';

interface Props {
  event: GameEvent;
  onClose: () => void;
}

const eventMeta: Record<string, { icon: string; title: string; color: string }> = {
  swarming: { icon: '🐝', title: '분봉 발생!', color: 'border-warning/40 bg-warning/8' },
  hornet_attack: { icon: '🐝🔴', title: '말벌 습격!', color: 'border-danger/40 bg-danger/8' },
  hornet_scout: { icon: '⚠️', title: '정찰 말벌 발견!', color: 'border-warning/40 bg-warning/8' },
  laying_worker: { icon: '🥚', title: '동봉산란!', color: 'border-danger/40 bg-danger/8' },
  queen_aging: { icon: '👑', title: '여왕 노화!', color: 'border-primary/40 bg-primary/8' },
};

export default function EventModal({ event, onClose }: Props) {
  const { doResolveSwarm, doResolveHornet, doResolveQueenAging, doResolveLayingWorker, state } = useGame();
  const [showMiniGame, setShowMiniGame] = useState(false);

  if (!state) return null;

  const hive = state.hives.find(h => h.id === event.hiveId);
  const hasTrap = hive?.hasHornetTrap ?? false;
  const meta = eventMeta[event.type] || { icon: '📋', title: '알림', color: 'border-border/60' };

  const isHornet = event.type === 'hornet_scout' || event.type === 'hornet_attack';

  const handleMiniGameComplete = (result: { killed: number; total: number; success: boolean }) => {
    setShowMiniGame(false);
    if (result.success) {
      doResolveHornet(event.id, 'kill');
    } else {
      doResolveHornet(event.id, 'ignore');
    }
    onClose();
  };

  // Show mini-game
  if (showMiniGame && isHornet) {
    return (
      <HornetDefenseGame
        mode={event.type === 'hornet_scout' ? 'scout' : 'attack'}
        hasTrap={hasTrap}
        onComplete={handleMiniGameComplete}
      />
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      className="fixed inset-0 z-[60] flex items-center justify-center bg-foreground/40 backdrop-blur-sm p-4" onClick={onClose}>
      <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 350 }}
        onClick={e => e.stopPropagation()}
        className="game-panel w-full max-w-sm p-0 overflow-hidden">

        {/* Header */}
        <div className={`px-5 pt-5 pb-3 border-b-2 ${meta.color}`}>
          <div className="flex justify-between items-start">
            <h2 className="font-serif text-lg font-bold text-foreground flex items-center gap-2">
              <span className="text-2xl">{meta.icon}</span> {meta.title}
            </h2>
            <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-secondary/60 transition-colors border border-border/40">
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
          <p className="text-xs text-muted-foreground mt-1 font-medium">📍 {event.hiveName}</p>
        </div>

        <div className="p-5 space-y-3">
          {event.type === 'swarming' && (
            <>
              <p className="text-xs text-foreground leading-relaxed">
                벌통에서 분봉이 일어나려 합니다! 분봉군이 근처 나뭇가지에 모여있습니다.
                포획하면 무료로 새 봉군을 얻을 수 있지만, 실패하면 벌의 50%를 잃습니다.
              </p>
              <div className="space-y-2 pt-1">
                <EventBtn onClick={() => { doResolveSwarm(event.id, 'capture'); onClose(); }}
                  label="🎯 분봉 포획 시도" primary />
                <EventBtn onClick={() => { doResolveSwarm(event.id, 'ignore'); onClose(); }}
                  label="방치 (벌 50% 손실)" />
              </div>
            </>
          )}

          {event.type === 'hornet_scout' && (
            <>
              <p className="text-xs text-foreground leading-relaxed">
                정찰 말벌이 벌통 주변을 배회하고 있습니다. 직접 잡으면 집단 습격을 예방할 수 있습니다!
              </p>
              <div className="space-y-2 pt-1">
                <EventBtn onClick={() => setShowMiniGame(true)}
                  label="⚔️ 직접 포살하기!" primary animated />
                <EventBtn onClick={() => { doResolveHornet(event.id, 'ignore'); onClose(); }}
                  label="무시 (습격 위험!)" />
              </div>
            </>
          )}

          {event.type === 'hornet_attack' && (
            <>
              <p className="text-xs text-foreground leading-relaxed">
                🚨 장수말벌이 벌통을 습격 중입니다! 직접 방어하여 말벌을 잡으세요!
              </p>
              <div className="space-y-2 pt-1">
                <EventBtn onClick={() => setShowMiniGame(true)}
                  label="⚔️ 직접 방어하기!" danger animated />
                {hasTrap && (
                  <EventBtn onClick={() => { doResolveHornet(event.id, 'trap'); onClose(); }}
                    label="🪤 트랩으로 자동 방어 (소량 피해)" warning />
                )}
                <EventBtn onClick={() => { doResolveHornet(event.id, 'ignore'); onClose(); }}
                  label="방치 (대규모 피해!)" />
              </div>
            </>
          )}

          {event.type === 'laying_worker' && (
            <>
              <p className="text-xs text-foreground leading-relaxed">
                🥚 여왕이 없는 상태에서 일벌이 산란을 시작했습니다! 수벌만 생산되어 봉군이 급속히 약화됩니다.
              </p>
              <div className="space-y-2 pt-1">
                <EventBtn onClick={() => { doResolveLayingWorker(event.hiveId, 'merge'); onClose(); }}
                  label="🔄 합봉 (가장 안전)" primary />
                <EventBtn onClick={() => { doResolveLayingWorker(event.hiveId, 'buy_queen'); onClose(); }}
                  label="👑 새 여왕 구입 (200💰)" />
                <EventBtn onClick={() => { doResolveLayingWorker(event.hiveId, 'introduce_larva'); onClose(); }}
                  label="🥚 유충 도입 (무료, 60%)" />
                <EventBtn onClick={() => { doResolveLayingWorker(event.hiveId, 'abandon'); onClose(); }}
                  label="방치 (봉군 소멸)" danger />
              </div>
            </>
          )}

          {event.type === 'queen_aging' && (
            <>
              <p className="text-xs text-foreground leading-relaxed">
                👑 {event.hiveName}의 여왕이 노화되고 있습니다. 산란력과 페로몬이 약해지면 분봉 위험이 높아집니다.
              </p>
              <div className="space-y-2 pt-1">
                <EventBtn onClick={() => { doResolveQueenAging(event.id, 'replace'); onClose(); }}
                  label="👑 여왕 교체 (200💰)" primary />
                <EventBtn onClick={() => { doResolveQueenAging(event.id, 'ignore'); onClose(); }}
                  label="나중에 결정" />
              </div>
            </>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

function EventBtn({ onClick, label, primary, danger, warning, animated }: {
  onClick: () => void; label: string; primary?: boolean; danger?: boolean; warning?: boolean; animated?: boolean;
}) {
  const base = 'w-full py-2.5 rounded-xl font-bold text-sm transition-all';
  const pulse = animated ? 'animate-pulse' : '';

  if (primary) return (
    <button onClick={onClick} className={`${base} game-btn honey-gradient text-primary-foreground ${pulse}`}>
      {label}
    </button>
  );
  if (danger) return (
    <button onClick={onClick} className={`${base} game-btn-danger bg-danger text-primary-foreground ${pulse}`}>
      {label}
    </button>
  );
  if (warning) return (
    <button onClick={onClick} className={`${base} border-2 border-warning/40 text-foreground hover:bg-warning/10`}>
      {label}
    </button>
  );
  return (
    <button onClick={onClick} className={`${base} border-2 border-border/60 text-muted-foreground hover:bg-secondary`}>
      {label}
    </button>
  );
}
