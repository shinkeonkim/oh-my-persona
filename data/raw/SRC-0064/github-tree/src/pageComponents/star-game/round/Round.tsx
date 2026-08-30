'use client';

import Image from 'next/image';
import React, { useEffect, useState, useRef, useMemo } from 'react';
import starGameBackgroundImage from '@/assets/images/star-game-backgroundimage.png';
import starGameProgressBarImage from '@/assets/images/progress-bar.png';
import backButton from '@/assets/icons/back.svg';
import star from '@/assets/images/star.png';
import ProgressBar from '@/app/loading/components/ProgressBar';
import { motion, AnimatePresence } from 'framer-motion';
import fingerImage from '@/assets/images/finger.png';
import GameBoard from '@/pageComponents/star-game/round/components/GameBoard';
import ScoreBoard from '@/components/common/ScoreBoard';
import { useRouter } from 'next/navigation';
import { endStarGame, startStarGame } from '@/lib/api/game/star/starApi';

type GameStats = {
  totalClicks: number;
  wrongClicks: number;
  correctClicks: number;
  successRounds: number;
};

const Round = () => {
  const router = useRouter();
  const [phase, setPhase] = useState<'observe' | 'memory'>('observe');

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

  const [overlayStep, setOverlayStep] = useState(0);
  const [gameStarted, setGameStarted] = useState(false);
  const [round, setRound] = useState(1);
  const [score, setScore] = useState(0);

  useEffect(() => {
    setPhase('observe'); // 새로운 라운드 시작 → 다시 인지 단계로 초기화
  }, [round]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const [progress, setProgress] = useState(100);
  const [timeLeft, setTimeLeft] = useState(10);
  const [timerRunning, setTimerRunning] = useState(false);

  // 전체 게임 누적 통계
  const statsRef = useRef<GameStats>({
    totalClicks: 0,
    wrongClicks: 0,
    correctClicks: 0,
    successRounds: 0,
  });

  // 타임오버로 이미 끝났는지 여부 (라운드 클리어 중복처리 방지용)
  const endedRef = useRef(false);

  // 타이머
  useEffect(() => {
    if (!timerRunning) return;

    const totalTime = timeLeft * 1000;
    const tick = 100;
    const step = 100 / (totalTime / tick);

    const interval = setInterval(() => {
      setProgress((p) => {
        if (p <= 0) {
          clearInterval(interval);
          setTimerRunning(false);
          handleTimeOver();
          return 0;
        }
        return p - step;
      });
    }, tick);

    return () => clearInterval(interval);
  }, [timerRunning, timeLeft]);

  // 라운드 시작 시 오버레이
  useEffect(() => {
    setOverlayStep(0);
    setGameStarted(false);
    setTimerRunning(false);
    setProgress(100);
    endedRef.current = false;

    const timers = [
      setTimeout(() => setOverlayStep(1), 1500),
      setTimeout(() => setOverlayStep(2), 3000),
      setTimeout(() => setOverlayStep(3), 4500),
    ];

    return () => timers.forEach(clearTimeout);
  }, [round]);

  const handleGameEnd = async () => {
    if (isSaved) return;

    const sessionId = window.sessionStorage.getItem('gameSessionId');
    if (!sessionId) {
      console.error('❌ sessionId 없음');
      return;
    }

    try {
      const payload = {
        sessionId,
        score: statsRef.current.correctClicks,
        wrongCount: statsRef.current.wrongClicks,
        reactionMsSum: 0,
        roundCount: statsRef.current.successRounds,
        successCount: statsRef.current.correctClicks,
      };

      console.log('[endStarGame] payload:', payload);

      await endStarGame(payload);
      window.sessionStorage.removeItem('gameSessionId');
      setIsSaved(true);
    } catch (error) {
      console.error('❌ 게임 종료 실패:', error);
    }
  };

  // ⏰ 타임오버
  const handleTimeOver = async () => {
    if (endedRef.current) return; // 이미 끝낸 상태라면 중복 처리 방지
    endedRef.current = true;

    setTimerRunning(false);
    setGameStarted(false);

    // 현재 라운드는 실패 → 이전 라운드까지만 성공
    statsRef.current.successRounds = round - 1;

    console.log('⏰ 시간 초과! 누적 통계:', statsRef.current);
    await handleGameEnd();
    setIsModalOpen(true);
  };

  const handleRestart = async () => {
    try {
      setIsModalOpen(false);
      setScore(0);
      setRound(1);
      setOverlayStep(0);
      setProgress(100);
      setTimerRunning(false);
      setIsSaved(false);
      endedRef.current = false;

      statsRef.current = {
        totalClicks: 0,
        wrongClicks: 0,
        correctClicks: 0,
        successRounds: 0,
      };

      window.sessionStorage.removeItem('gameSessionId');

      const res = await startStarGame();
      window.sessionStorage.setItem('gameSessionId', res.sessionId);
    } catch (error) {
      console.error('❌ 다시하기 중 세션 재발급 실패:', error);
      alert('새 게임을 시작할 수 없습니다. 다시 시도해주세요.');
    }
  };

  const overlayText =
    overlayStep === 0
      ? `${round} ROUND`
      : overlayStep === 1
        ? '준비'
        : overlayStep === 2
          ? '시작!'
          : overlayStep === 5
            ? 'ROUND CLEAR!'
            : '';

  const overlayColor = overlayStep === 5 ? '#FFD23C' : '#F6A000';

  return (
    <div className="w-full h-screen relative overflow-hidden">
      {isModalOpen && (
        <div className="absolute inset-0 flex items-center justify-center z-[200] bg-black/60">
          <ScoreBoard
            type="star"
            score={score}
            onClose={() => {
              window.sessionStorage.removeItem('gameSessionId');
              router.push('/main');
            }}
            onRetry={handleRestart}
          />
        </div>
      )}

      <AnimatePresence>
        {overlayStep !== 4 && !isModalOpen && (
          <motion.div
            key={overlayStep}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
            className="absolute inset-0 flex flex-col items-center justify-center font-malrang z-[90] bg-black/60"
          >
            {[0, 1, 2, 5].includes(overlayStep) && (
              <motion.span
                key={overlayText}
                initial={{ scale: 0.7, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6 }}
                className="font-nanum text-[128px] font-extrabold relative inline-block"
                style={{
                  position: 'relative',
                  display: 'inline-block',
                }}
              >
                {/* 보더 효과를 위한 여러 레이어 */}
                {borderLayers.map((layer, i) => {
                  const scale = 7 / 5; // 7px 테두리를 위해 스케일 조정
                  return (
                    <span
                      key={i}
                      style={{
                        position: 'absolute',
                        top: '0',
                        left: '0',
                        color: '#994802',
                        transform: `translate(${(parseFloat(layer.x) * scale).toFixed(5)}px, ${(parseFloat(layer.y) * scale).toFixed(5)}px)`,
                        zIndex: 1,
                        WebkitTextStrokeWidth: 4,
                      }}
                    >
                      {overlayText}
                    </span>
                  );
                })}
                {/* 메인 텍스트 레이어 */}
                <span
                  style={{
                    position: 'relative',
                    background: `linear-gradient(to bottom, ${overlayColor}, #994802)`,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    zIndex: 2,
                  }}
                >
                  {overlayText}
                </span>
              </motion.span>
            )}

            {overlayStep === 3 && (
              <div className="absolute left-1/2 -translate-x-1/2 top-7 z-[50]">
                <div className="flex flex-col items-center gap-3">
                  <p className="font-malrang text-[40px] text-[#FAFAFA] opacity-0">
                    {round}라운드: 인지 단계
                  </p>

                  <div className="relative w-[600px] h-[100px] opacity-0">
                    <Image
                      src={starGameProgressBarImage}
                      alt="progress-bar"
                      width={650}
                      className="z-0"
                    />
                    <div className="absolute inset-0 left-[90px] top-10">
                      <ProgressBar progress={progress} type="starGame" />
                    </div>
                  </div>

                  <div className="flex flex-col items-center pointer-events-none absolute z-50 -right-10 bottom-20">
                    <Image
                      src={fingerImage}
                      alt="finger"
                      width={150}
                      height={150}
                      className="animate-bounce"
                    />
                  </div>

                  <div
                    className="relative w-[616px] h-[450px] rounded-3xl bg-black/10 flex items-center justify-center p-5 cursor-pointer pointer-events-auto"
                    onClick={() => {
                      if (overlayStep === 3) {
                        setOverlayStep(4);
                        setTimeout(() => setGameStarted(true), 800);
                      }
                    }}
                  >
                    <div className="absolute grid grid-cols-3 grid-rows-3 gap-6 gap-x-12">
                      {Array.from({ length: 9 }).map((_, i) => (
                        <Image key={i} src={star} alt={`star-${i}`} width={110} height={110} />
                      ))}
                    </div>
                  </div>

                  <p className="text-[36px] text-[#F3ECCF] mt-2 font-extrabold z-[50] font-nanum whitespace-nowrap">
                    아기별이 등장하는 위치와 순서를 기억해봐!
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <Image
        src={starGameBackgroundImage}
        alt="Star Game Background"
        fill
        style={{ objectFit: 'cover' }}
        priority
      />

      <div className="text-[#F0F0F0] font-malrang absolute flex items-center gap-5 right-10 top-10 z-[60]">
        <p className="text-[40px]">점수</p>
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
                color: '#9F4A11',
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

      <div className="absolute left-1/2 -translate-x-1/2 top-7 z-[50]">
        <div className="flex flex-col items-center gap-3">
          {phase === 'observe' && <p className="text-4xl text-white"> {round}라운드: 인지 단계 </p>}

          {phase === 'memory' && <p className="text-4xl text-white"> {round}라운드: 기억 단계 </p>}

          <div className="relative w-[600px] h-[100px]">
            <Image src={starGameProgressBarImage} alt="progress-bar" width={650} className="z-0" />
            <div className="absolute inset-0 left-[90px] top-10">
              <ProgressBar progress={progress} type="starGame" />
            </div>
          </div>

          <div className="relative w-[616px] h-[450px] rounded-3xl bg-black/10 flex items-center justify-center p-5 z-[50]">
            {gameStarted && (
              <GameBoard
                key={round}
                round={round}
                setScore={setScore}
                onMemoryEnd={() => {
                  const newTime = Math.max(5, 12.5 - round * 0.5);
                  setTimeLeft(newTime);
                  setProgress(100);
                  setTimerRunning(true);
                }}
                // ✅ 클릭 발생할 때마다 통계 누적
                onClickResult={({ isCorrect }) => {
                  statsRef.current.totalClicks += 1;
                  if (isCorrect) statsRef.current.correctClicks += 1;
                  else statsRef.current.wrongClicks += 1;

                  console.log('클릭 통계:', statsRef.current);
                }}
                // ✅ 라운드 클리어 시
                onRoundComplete={async () => {
                  if (endedRef.current) return; // 타임오버로 이미 끝난 상태면 무시
                  endedRef.current = true;

                  setTimerRunning(false);
                  setGameStarted(false);
                  setOverlayStep(5);

                  // 이 라운드까지 성공
                  statsRef.current.successRounds = round;

                  console.log(`🎯 ${round}라운드 클리어! 누적 통계:`, statsRef.current);

                  if (round >= 10) {
                    await handleGameEnd();
                    setTimeout(() => setIsModalOpen(true), 1500);
                    return;
                  }

                  setTimeout(() => {
                    setRound((r) => r + 1);
                  }, 2000);
                }}
                phase={phase}
                onPhaseChange={(newPhase) => setPhase(newPhase)}
              />
            )}
          </div>
        </div>
      </div>

      <div className="absolute top-10 left-16 z-[60] cursor-pointer hover:scale-105 transition-transform">
        <Image
          src={backButton}
          alt="back-button"
          width={120}
          priority
          onClick={() => {
            window.sessionStorage.removeItem('gameSessionId');
            router.push('/main');
          }}
        />
      </div>
    </div>
  );
};

export default Round;
