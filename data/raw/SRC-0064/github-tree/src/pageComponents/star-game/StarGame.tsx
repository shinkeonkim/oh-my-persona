'use client';

import Image from 'next/image';
import React, { useState } from 'react';
import starGameBackgroundImage from '@/assets/images/star-game-backgroundimage.png';
import starGameCharacter from '@/assets/images/star-game-character.png';
import Description from '@/components/trafficGame/Description';
import backButton from '@/assets/icons/back.svg';
import { useRouter } from 'next/navigation';
import { startStarGame } from '@/lib/api/game/star/starApi';

const StarGame = () => {
  const [state, setState] = useState(0); // description state
  const [loading, setLoading] = useState(false);
  const descriptions = [
    '작은 별들이 우주에서 길을 잃었어! 작은 별들이 제자리로 찾아갈 수 있도록 도움이 필요해.',
    '별들이 깜빡이는 위치를 기억해서 순서대로 입력하면 별들이 제자리를 찾아가 별자리가 될 수 있어.',
    '나와 함께 우주탐험대가 되어 작은 별들을 구출해 주겠니?',
  ];

  const handleNext = async () => {
    // 아직 설명이 남았으면 다음으로 넘기기
    if (state < descriptions.length - 1) {
      setState(state + 1);
      return;
    }

    // 마지막 설명이면 게임 시작 API 호출
    try {
      setLoading(true);
      const res = await startStarGame();

      console.log('🎮 게임 세션 시작:', res);

      // 세션 ID 저장 (다음 라운드 페이지에서 필요할 수 있음)
      if (typeof window !== 'undefined') {
        window.sessionStorage.setItem('gameSessionId', res.sessionId);
      }

      // 라운드 페이지로 이동
      router.push('/game/star/round');
    } catch (error) {
      console.error('❌ 게임 시작 실패:', error);
      alert('게임을 시작하는 데 실패했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  const router = useRouter();

  return (
    <div className="w-full h-screen">
      <div className="absolute top-10 left-16 z-50 cursor-pointer hover:scale-105 transition-transform">
        <Image
          src={backButton}
          alt="back-button"
          width={120}
          priority
          onClick={() => {
            router.push('/main');
          }}
        />
      </div>

      {/* 배경 이미지 */}
      <Image
        src={starGameBackgroundImage}
        alt="Star Game Background"
        fill
        style={{ objectFit: 'cover' }}
        priority
      />

      <div className="absolute -top-12 left-1/3">
        <Image
          src={starGameCharacter}
          alt="Star Game Character"
          width={650}
          height={200}
          priority
        />
      </div>

      <div className="w-full px-29 absolute bottom-[70px]">
        <Description title="별똥이" onClickNext={handleNext}>
          {descriptions[state]}
        </Description>
      </div>
    </div>
  );
};

export default StarGame;
