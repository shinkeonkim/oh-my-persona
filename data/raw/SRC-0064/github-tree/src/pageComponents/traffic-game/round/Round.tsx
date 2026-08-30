'use client';

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import PrimaryButton from '@/components/common/PrimaryButton';
import trafficBackground from '@/assets/images/traffic-background.png';
import trafficLightRed from '@/assets/images/traffic-light-red.png';
import trafficLightGreen from '@/assets/images/traffic-light-green.png';
import carImage from '@/assets/images/car.png';
import gasGaugeImage from '@/assets/images/gas.png';
import backImg from '@/assets/icons/back.svg';
import ScoreBoard from '@/components/common/ScoreBoard';
import { finishTrafficGame, startTrafficGame } from '@/lib/api/game/traffic';

const ROUND_CONFIG = [
  { round: 1, changeCount: 5, interval: 4000 },
  { round: 2, changeCount: 5, interval: 3800 },
  { round: 3, changeCount: 5, interval: 3500 },
  { round: 4, changeCount: 5, interval: 3200 },
  { round: 5, changeCount: 5, interval: 3000 },
  { round: 6, changeCount: 5, interval: 2700 },
  { round: 7, changeCount: 5, interval: 2500 },
  { round: 8, changeCount: 5, interval: 2200 },
  { round: 9, changeCount: 5, interval: 2000 },
  { round: 10, changeCount: 5, interval: 1800 },
] as const;

interface RoundProps {
  onBack?: () => void;
}

interface RoundDetail {
  round_number: number;
  score: number;
  wrong_count: number;
  reaction_ms_sum: number;
  is_success: boolean;
  time_limit_exceeded: boolean;
}

const Round: React.FC<RoundProps> = ({ onBack }) => {
  const router = useRouter();

  // 둥근 테두리를 위한 레이어 생성 (버튼과 동일한 방식)
  const borderLayers = useMemo(() => {
    return [...Array(32)].map((_, i) => {
      const angle = (i * Math.PI * 2) / 32;
      const x = Math.cos(angle) * 5;
      const y = Math.sin(angle) * 5;
      return {
        x: x.toFixed(5),
        y: y.toFixed(5),
      };
    });
  }, []);

  const [roundIndex, setRoundIndex] = useState(0);
  const [overlayStep, setOverlayStep] = useState<'round' | 'ready' | 'start' | 'none'>('round');
  const [score, setScore] = useState(0);
  const [failCount, setFailCount] = useState(0);
  const [lightState, setLightState] = useState<'red' | 'green'>('red');
  const [buttonsDisabled, setButtonsDisabled] = useState(true);
  const [, setChangeCount] = useState(0);
  const [isCarMoving, setIsCarMoving] = useState(false);
  const [isGameOver, setIsGameOver] = useState(false);
  const [resetKey, setResetKey] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [totalWrongCount, setTotalWrongCount] = useState(0);
  const [completedRounds, setCompletedRounds] = useState(0);
  const [totalReactionMs, setTotalReactionMs] = useState(0);
  const [roundDetails, setRoundDetails] = useState<RoundDetail[]>([]);
  const cycleRespondedRef = useRef(false);
  const finishRequestedRef = useRef(false);
  const lastSignalChangeTimeRef = useRef<number | null>(null);
  const roundScoreRef = useRef(0);
  const roundWrongCountRef = useRef(0);
  const roundReactionMsRef = useRef(0);
  const roundTimeLimitExceededRef = useRef(false);
  const hasFlushedCurrentRoundRef = useRef(false);
  const sessionInitializedRef = useRef(false);

  const currentRound = useMemo(
    () => ROUND_CONFIG[Math.min(roundIndex, ROUND_CONFIG.length - 1)],
    [roundIndex]
  );
  const isLastRound = roundIndex >= ROUND_CONFIG.length - 1;

  useEffect(() => {
    cycleRespondedRef.current = false;
    lastSignalChangeTimeRef.current = null;
    setOverlayStep('round');
    setButtonsDisabled(true);
    setLightState('red');
    setIsCarMoving(false);
    roundScoreRef.current = 0;
    roundWrongCountRef.current = 0;
    roundReactionMsRef.current = 0;
    roundTimeLimitExceededRef.current = false;
    hasFlushedCurrentRoundRef.current = false;

    const timers = [
      setTimeout(() => setOverlayStep('ready'), 800),
      setTimeout(() => setOverlayStep('start'), 1600),
      setTimeout(() => {
        setOverlayStep('none');
        setButtonsDisabled(false);
        setLightState('green');
        setIsCarMoving(false);
        cycleRespondedRef.current = false;
        lastSignalChangeTimeRef.current = performance.now();
      }, 2400),
    ];

    return () => timers.forEach(clearTimeout);
  }, [roundIndex, resetKey]);

  const flushCurrentRound = useCallback(
    (isSuccess: boolean) => {
      if (hasFlushedCurrentRoundRef.current) {
        return;
      }

      const detail: RoundDetail = {
        round_number: roundIndex + 1,
        score: roundScoreRef.current,
        wrong_count: roundWrongCountRef.current,
        reaction_ms_sum: roundReactionMsRef.current,
        is_success: isSuccess,
        time_limit_exceeded: roundTimeLimitExceededRef.current,
      };

      setRoundDetails((prev) => [...prev, detail]);

      if (isSuccess) {
        setCompletedRounds((prev) => prev + 1);
      }

      hasFlushedCurrentRoundRef.current = true;
    },
    [roundIndex]
  );

  const registerFail = useCallback(
    (options?: { timeLimitExceeded?: boolean }) => {
      setTotalWrongCount((prev) => prev + 1);
      roundWrongCountRef.current += 1;
      if (options?.timeLimitExceeded) {
        roundTimeLimitExceededRef.current = true;
      }
      setFailCount((prev) => {
        const next = Math.min(prev + 1, 3);
        if (next >= 3) {
          flushCurrentRound(false);
          setButtonsDisabled(true);
          setIsGameOver(true);
          setIsCarMoving(false);
          setOverlayStep('none');
        }
        return next;
      });
    },
    [flushCurrentRound]
  );

  const advanceRound = useCallback(() => {
    if (hasFlushedCurrentRoundRef.current) {
      return;
    }

    flushCurrentRound(true);
    if (isLastRound) {
      setOverlayStep('none');
      setButtonsDisabled(true);
      setIsCarMoving(false);
      setIsGameOver(true);
      return;
    }
    setRoundIndex((prev) => prev + 1);
    setFailCount(0);
    setChangeCount(0);
    cycleRespondedRef.current = false;
    setIsCarMoving(true);
  }, [flushCurrentRound, isLastRound]);

  const handleGreen = () => {
    if (buttonsDisabled) return;
    if (lightState !== 'green') {
      registerFail();
      return;
    }
    if (cycleRespondedRef.current) return;
    cycleRespondedRef.current = true;
    const now = performance.now();
    if (lastSignalChangeTimeRef.current != null) {
      const reaction = Math.max(0, Math.round(now - lastSignalChangeTimeRef.current));
      setTotalReactionMs((prev) => prev + reaction);
      roundReactionMsRef.current += reaction;
    }
    roundScoreRef.current += 1;
    setScore((prev) => prev + 1);
    setIsCarMoving(true);
  };

  const handleRed = () => {
    if (buttonsDisabled) return;
    if (lightState !== 'red') {
      registerFail();
      return;
    }
    if (cycleRespondedRef.current) return;
    cycleRespondedRef.current = true;
    const now = performance.now();
    if (lastSignalChangeTimeRef.current != null) {
      const reaction = Math.max(0, Math.round(now - lastSignalChangeTimeRef.current));
      setTotalReactionMs((prev) => prev + reaction);
      roundReactionMsRef.current += reaction;
    }
    roundScoreRef.current += 1;
    setScore((prev) => prev + 1);
    setIsCarMoving(false);
  };

  const handleSignalChange = useCallback(() => {
    if (!cycleRespondedRef.current) {
      registerFail({ timeLimitExceeded: true });
    }
    cycleRespondedRef.current = false;

    const nextState = lightState === 'red' ? 'green' : 'red';
    setLightState(nextState);
    setIsCarMoving(nextState === 'red');
    lastSignalChangeTimeRef.current = performance.now();

    setChangeCount((prev) => {
      const next = prev + 1;
      if (next >= currentRound.changeCount) {
        advanceRound();
        return 0;
      }
      return next;
    });
  }, [advanceRound, currentRound.changeCount, registerFail, lightState]);

  const handleRestart = useCallback(async () => {
    // 재시작 전에 현재 세션이 있으면 종료
    const currentSessionId = sessionId;
    if (currentSessionId && !finishRequestedRef.current) {
      finishRequestedRef.current = true;
      try {
        await finishTrafficGame({
          sessionId: currentSessionId,
          score,
          wrongCount: totalWrongCount,
          roundCount: roundDetails.length,
          successCount: completedRounds,
          reactionMsSum: Math.round(totalReactionMs),
          meta: {
            round_details: roundDetails,
          },
        });
      } catch (error) {
        // 이전 게임 세션 종료 실패는 무시
      }
    }

    setScore(0);
    setFailCount(0);
    setRoundIndex(0);
    setChangeCount(0);
    setLightState('red');
    setButtonsDisabled(true);
    setOverlayStep('round');
    setIsCarMoving(true);
    setIsGameOver(false);
    setSessionId(null);
    setTotalWrongCount(0);
    setCompletedRounds(0);
    setTotalReactionMs(0);
    setRoundDetails([]);
    cycleRespondedRef.current = false;
    finishRequestedRef.current = false;
    lastSignalChangeTimeRef.current = null;
    roundScoreRef.current = 0;
    roundWrongCountRef.current = 0;
    roundReactionMsRef.current = 0;
    roundTimeLimitExceededRef.current = false;
    hasFlushedCurrentRoundRef.current = false;
    sessionInitializedRef.current = false; // 재시작 시 초기화 플래그도 리셋
    setResetKey((prev) => prev + 1);
  }, [completedRounds, roundDetails, score, sessionId, totalReactionMs, totalWrongCount]);

  useEffect(() => {
    if (overlayStep !== 'none' || failCount >= 3 || isGameOver) {
      return;
    }

    const intervalId = setInterval(() => {
      if (!buttonsDisabled) {
        handleSignalChange();
      }
    }, currentRound.interval);

    return () => {
      clearInterval(intervalId);
    };
  }, [
    overlayStep,
    failCount,
    buttonsDisabled,
    currentRound.interval,
    handleSignalChange,
    isGameOver,
  ]);

  const initializeSession = useCallback(async () => {
    if (sessionId || sessionInitializedRef.current) {
      return;
    }

    sessionInitializedRef.current = true;

    try {
      const response = await startTrafficGame();
      const nextSessionId = response.sessionId ?? null;
      setSessionId(nextSessionId);
      finishRequestedRef.current = false;
    } catch (error) {
      sessionInitializedRef.current = false; // 실패 시 다시 시도할 수 있도록
      if (
        error &&
        typeof error === 'object' &&
        'response' in error &&
        error.response &&
        typeof error.response === 'object' &&
        'status' in error.response &&
        error.response.status === 404
      ) {
        const errorResponse = error.response as { data?: { message?: string } };
        const errorMessage =
          errorResponse.data?.message ||
          '게임을 시작할 수 없어요. 게임이 활성화되어 있는지, 또는 자녀 정보가 등록되어 있는지 확인해 주세요.';
        alert(errorMessage);
      }
      setSessionId(null);
    }
  }, [sessionId]);

  useEffect(() => {
    initializeSession();
  }, [initializeSession, resetKey]);

  useEffect(() => {
    if (!isGameOver || !sessionId || finishRequestedRef.current) {
      return;
    }

    finishRequestedRef.current = true;

    const submitResult = async () => {
      try {
        await finishTrafficGame({
          sessionId,
          score,
          wrongCount: totalWrongCount,
          roundCount: roundDetails.length,
          successCount: completedRounds,
          reactionMsSum: Math.round(totalReactionMs),
          meta: {
            round_details: roundDetails,
          },
        });
      } catch (error) {
        // 게임 세션 종료 실패는 무시
      }
    };

    void submitResult();
  }, [
    completedRounds,
    isGameOver,
    roundDetails,
    score,
    sessionId,
    totalReactionMs,
    totalWrongCount,
  ]);

  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      {isGameOver && (
        <div className="absolute inset-0 z-[300] flex items-center justify-center bg-black/60">
          <ScoreBoard
            type="traffic"
            score={score}
            onClose={() => router.push('/main')}
            onRetry={handleRestart}
          />
        </div>
      )}
      <AnimatePresence>
        {overlayStep !== 'none' && (
          <motion.div
            key={overlayStep}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 z-[200] flex items-center justify-center bg-black/40"
          >
            <span
              className="font-nanum text-[120px] relative inline-block"
              style={{
                position: 'relative',
                display: 'inline-block',
              }}
            >
              {/* 보더 효과를 위한 여러 레이어 */}
              {borderLayers.map((layer, i) => {
                const scale = 8 / 5; // 8px 테두리를 위해 스케일 조정
                return (
                  <span
                    key={i}
                    style={{
                      position: 'absolute',
                      top: '0',
                      left: '0',
                      color: '#7F4B1F',
                      transform: `translate(${(parseFloat(layer.x) * scale).toFixed(5)}px, ${(parseFloat(layer.y) * scale).toFixed(5)}px)`,
                      zIndex: 1,
                      WebkitTextStrokeWidth: 4,
                    }}
                  >
                    {overlayStep === 'round' && `${currentRound.round} 라운드`}
                    {overlayStep === 'ready' && '준비'}
                    {overlayStep === 'start' && '시작!'}
                  </span>
                );
              })}
              {/* 메인 텍스트 레이어 */}
              <span
                style={{
                  position: 'relative',
                  background: 'linear-gradient(180deg, #FFD359 0%, #FF9F1A 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  zIndex: 2,
                }}
              >
                {overlayStep === 'round' && `${currentRound.round} 라운드`}
                {overlayStep === 'ready' && '준비'}
                {overlayStep === 'start' && '시작!'}
              </span>
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      <Image src={trafficBackground} alt="교통 게임 배경" fill priority className="object-cover" />

      {onBack && (
        <button
          type="button"
          onClick={onBack}
          className="absolute left-[80px] top-[50px] z-20 transition-transform hover:scale-105 active:scale-95"
        >
          <Image src={backImg} alt="뒤로가기" width={120} height={120} priority />
        </button>
      )}

      <div className="absolute top-[64px] right-[100px] flex items-center gap-[26px]">
        <p className="font-malrangiche text-[30px] text-[#333333]">점수</p>
        <span
          className="font-sdsamliphopangche text-[64px] relative inline-block"
          style={{
            position: 'relative',
            display: 'inline-block',
          }}
        >
          {/* 보더 효과를 위한 여러 레이어 */}
          {borderLayers.map((layer, i) => (
            <span
              key={i}
              style={{
                position: 'absolute',
                top: '0',
                left: '0',
                color: '#7F4F1A',
                transform: `translate(${layer.x}px, ${layer.y}px)`,
                zIndex: 1,
                WebkitTextStrokeWidth: 3,
              }}
            >
              {score}
            </span>
          ))}
          {/* 메인 텍스트 레이어 */}
          <span
            style={{
              position: 'relative',
              color: '#FFC738',
              zIndex: 2,
            }}
          >
            {score}
          </span>
        </span>
      </div>

      <div className="absolute top-[100px] left-[250px] flex items-center gap-[18px]">
        <div className="flex items-center gap-2">
          {Array.from({ length: 3 }).map((_, idx) => (
            <div
              key={idx}
              className={`h-6 w-12 rounded-full border-[4px] border-[#7F4F1A] ${
                idx < failCount ? 'bg-[#E05B4E]' : 'bg-[#FFE6B8]'
              }`}
            />
          ))}
        </div>
      </div>

      <Image
        className="absolute top-[140px] right-0"
        src={lightState === 'green' ? trafficLightGreen : trafficLightRed}
        alt={`신호등_${lightState}`}
        width={788}
        height={150}
      />
      <div className="absolute top-[54px] left-1/2 -translate-x-1/2">
        <p className="font-malrangiche text-[40px] text-white">{currentRound.round} 라운드</p>
      </div>

      <motion.div
        className="absolute bottom-[110px] left-1/2 -translate-x-1/2"
        animate={
          isCarMoving && failCount < 3
            ? {
                x: [0, 12, 0, -8, 0],
                y: [0, -25, -5, -38, 0],
                scale: [0.96, 0.88, 0.84, 0.88, 0.96],
                transition: {
                  duration: currentRound.interval / 1000,
                  repeat: Infinity,
                  repeatType: 'loop',
                  ease: 'easeInOut',
                },
              }
            : {
                x: 0,
                y: 0,
                scale: 1.06,
                transition: { duration: 0.55, ease: 'easeOut' },
              }
        }
      >
        <div className="relative">
          <Image src={carImage} alt="자동차" width={410} height={350} priority />
          {isCarMoving && failCount < 3 && (
            <motion.div
              className="absolute -right-10 bottom-12"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{
                opacity: 1,
                scale: [1, 1.08, 0.96, 1.08, 1],
              }}
              transition={{
                duration: 1.6,
                repeat: Infinity,
                repeatType: 'loop',
                ease: 'easeInOut',
              }}
            >
              <Image src={gasGaugeImage} alt="연료 게이지" width={150} height={120} priority />
            </motion.div>
          )}
        </div>
      </motion.div>

      <div className="absolute bottom-[75px] left-1/2 flex w-full max-w-[1200px] -translate-x-1/2 justify-between px-[100px]">
        <PrimaryButton variant="lg" color="red" disabled={buttonsDisabled} onClick={handleRed}>
          멈춰!
        </PrimaryButton>
        <PrimaryButton variant="lg" color="green" disabled={buttonsDisabled} onClick={handleGreen}>
          달려!
        </PrimaryButton>
      </div>
    </div>
  );
};

export default Round;
