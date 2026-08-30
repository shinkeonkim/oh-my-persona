'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import star from '@/assets/images/star.png';

interface GameBoardProps {
  round: number;
  setScore: React.Dispatch<React.SetStateAction<number>>;
  onRoundComplete: () => void;
  onMemoryEnd: () => void;
  onClickResult: (result: { isCorrect: boolean }) => void;
  phase: 'observe' | 'memory';
  onPhaseChange: (phase: 'observe' | 'memory') => void;
}

export default function GameBoard({
  round,
  setScore,
  onRoundComplete,
  onMemoryEnd,
  onClickResult,
  phase,
  onPhaseChange,
}: GameBoardProps) {
  const [sequence, setSequence] = useState<number[]>([]);
  const [userInput, setUserInput] = useState<number[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeStar, setActiveStar] = useState<number | null>(null);
  const [poppedStars, setPoppedStars] = useState<number[]>([]);
  const [wrongIndex, setWrongIndex] = useState<number | null>(null);
  const [shake, setShake] = useState(false);

  useEffect(() => {
    startRound();
  }, []);

  function generateSequence(length: number) {
    const arr = Array.from({ length: 9 }, (_, i) => i);
    const shuffled = arr.sort(() => Math.random() - 0.5);
    return shuffled.slice(0, length);
  }

  async function playSequence(seq: number[]) {
    setIsPlaying(true);
    for (const idx of seq) {
      setActiveStar(idx);
      await new Promise((res) => setTimeout(res, 600));
      setActiveStar(null);
      await new Promise((res) => setTimeout(res, 300));
    }
    setIsPlaying(false);
    onMemoryEnd();
    onPhaseChange('memory');
  }

  function startRound() {
    const seq = generateSequence(round + 2);
    setSequence(seq);
    setUserInput([]);
    setPoppedStars([]);
    playSequence(seq);
  }

  function handleStarClick(index: number) {
    if (isPlaying) return;

    const expected = sequence[userInput.length];

    // 클릭 한 번 발생 → 부모에 통계 전송
    if (index !== expected) {
      onClickResult({ isCorrect: false });

      setWrongIndex(index);
      setShake(true);
      setTimeout(() => {
        setWrongIndex(null);
        setShake(false);
      }, 300);
      return;
    }

    // 정답 클릭
    onClickResult({ isCorrect: true });

    setUserInput((prev) => [...prev, index]);
    setScore((prev) => prev + 1);
    setPoppedStars((prev) => [...prev, index]);

    // 시퀀스 전체 성공
    if (userInput.length + 1 === sequence.length) {
      setTimeout(() => onRoundComplete(), 1000);
    }
  }

  return (
    <div
      className={`absolute inset-0 flex flex-col items-center justify-center transition-transform duration-200 ${
        shake ? 'animate-shake' : ''
      }`}
    >
      <div className="grid grid-cols-3 gap-6 gap-x-12">
        {Array.from({ length: 9 }).map((_, i) => (
          <div
            key={i}
            onClick={() => handleStarClick(i)}
            className={`transition-all cursor-pointer relative ${
              activeStar === i
                ? 'scale-110 brightness-125'
                : wrongIndex === i
                  ? 'bg-red-500/40 rounded-full scale-110'
                  : ''
            }`}
          >
            <div
              className={`transition-all duration-500 ${
                poppedStars.includes(i) ? 'opacity-0 scale-150 blur-md' : 'opacity-100 scale-100'
              }`}
            >
              <Image src={star} alt={`star-${i}`} width={110} height={110} />
            </div>
          </div>
        ))}
      </div>

      <style jsx global>{`
        @keyframes shake {
          0%,
          100% {
            transform: translate(0);
          }
          25% {
            transform: translate(-10px, 0);
          }
          50% {
            transform: translate(10px, 0);
          }
          75% {
            transform: translate(-10px, 0);
          }
        }
        .animate-shake {
          animation: shake 0.3s ease-in-out;
        }
      `}</style>
    </div>
  );
}
