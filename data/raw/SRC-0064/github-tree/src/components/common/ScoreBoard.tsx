'use client';

import Image from 'next/image';
import React, { useEffect, useState } from 'react';
import scoreBoardImage from '@/assets/images/score-board.png';
import star from '@/assets/images/score-board-star.png';
import traffic from '@/assets/images/score-board-traffic.png';
import cancelIcon from '@/assets/icons/cancel.svg';
import PrimaryButton from './PrimaryButton';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';

const STAR_COMMENTS = [
  '우리 친구는 정말 신중한 탐험대원이야. 천천히 하나씩 확인하는 모습에서 굉장히 믿음직스러웠어.',
  '별들이 엄청 복잡하게 깜빡였는데도 끝까지 눈을 떼지 않고 집중하는 모습이 정말 멋졌어. 별들을 구해줘서 고마워!',
  '너의 기억력은 우주만큼 넓은가 봐! 다음에는 더 멋진 은하수를 찾아보자!',
  '대단해! 아무나 성공할 수 없는 어려운 미션인데 완벽하게 해냈어!',
  '우리가 찾은 별들이 반짝이는 모습을 상상해 봐!',
  '최고의 집중력으로 임무를 완수해 줘서 고마워!',
];

const TRAFFIC_COMMENTS = [
  '최고의 집중력으로 임무를 완수해 줘서 고마워!',
  '오늘 교통지킴이 임무 완수! 규칙을 지키는 능력은 우리 친구가 세상에서 가장 멋진 사람이 되도록 도와줄 거야.',
  '빨간불에서 꾹 참고 멈추는 모습은 정말 최고였어. 규칙을 지키는 책임감 칭찬해!',
  '멈추려고 노력했던 그 순간을 똑똑히 봤어. 그 마음가짐이 정말로 멋졌어!',
  '초록불이 켜지자마자 쏜살같이 출발 버튼을 눌렀네! 빠르게 행동하는 너의 민첩함 대단한걸?',
  '너는 상황이 바뀌어도 침착하게 해내는 유연한 두뇌를 가졌구나!',
];

type scoreBoardProps = {
  type: 'star' | 'traffic';
  score: number;
  onClose: () => void;
  onRetry: () => void;
};

const ScoreBoard = ({ type, score, onClose, onRetry }: scoreBoardProps) => {
  const router = useRouter();
  const [comment, setComment] = useState('');
  const [description, setDescription] = useState({
    title: '',
    subtitle: '',
    image: star,
  });

  useEffect(() => {
    if (type === 'star') {
      setDescription({
        title: '내가 구한 아기별',
        subtitle: '우주 탐험대 ‘별똥이’의 한마디',
        image: star,
      });
      const randomIndex = Math.floor(Math.random() * STAR_COMMENTS.length);
      setComment(STAR_COMMENTS[randomIndex]);
    } else {
      setDescription({
        title: '내가 지킨 교통질서',
        subtitle: '교통지킴이 ‘신호등’의 한마디',
        image: traffic,
      });
      const randomIndex = Math.floor(Math.random() * TRAFFIC_COMMENTS.length);
      setComment(TRAFFIC_COMMENTS[randomIndex]);
    }
  }, [type, score]);

  return (
    <div className="relative w-[1100px] h-[580px] bg-[#9D5C15] px-10 py-8 rounded-[56px] border-[15px] border-[#6C3F05]">
      {/* 상단 이미지 */}
      <Image
        src={scoreBoardImage}
        alt="Score Board"
        width={270}
        className="absolute -top-20 z-50 left-1/2 -translate-x-1/2"
      />
      <Image
        src={cancelIcon}
        alt="cancel icon"
        width={73}
        className="absolute -right-7 -top-10 cursor-pointer hover:scale-105 transition-transform"
        onClick={onClose}
      />

      {/* 하단 장식 */}
      <div className="absolute w-[378px] h-3.5 rounded-full bottom-2 left-20 bg-[#B56F21]" />
      <div className="absolute w-[47px] h-3.5 rounded-full bottom-2 left-[470px] bg-[#B56F21]" />

      {/* 내부 박스 */}
      <div className="relative w-full h-full bg-gradient-to-b from-[#FFCA57] to-[#F7A304] rounded-[33px] border-[11px] border-[#804B07]">
        {/* 장식 */}
        <div className="absolute bg-[#F5B53C] w-[150px] h-1.5 rounded-r-full top-10 left-0" />
        <div className="absolute bg-[#F5B53C] w-[100px] h-1.5 rounded-r-full top-14 left-0" />

        <div className="absolute bg-[#FFB428] w-[170px] h-1.5 rounded-l-full bottom-14 right-0" />
        <div className="absolute bg-[#FFB428] w-[100px] h-1.5 rounded-l-full bottom-10 right-0" />

        <div className="absolute bg-[#FFB428] w-[170px] h-1.5 rounded-full bottom-14 left-20" />
        <div className="absolute bg-[#FFB428] w-[100px] h-1.5 rounded-full bottom-10 left-12" />

        {/* 내용 */}
        <div className="flex flex-col items-center justify-center h-full gap-5 mt-5">
          <p className="text-[32px]">
            {description.title} <span className="text-5xl">{score}</span>개
          </p>

          <div className="relative w-[75%] h-[200px] bg-[#FFEECF] rounded-[34px] border-[10px] border-[#D18800] flex flex-col items-center pt-5 px-24 gap-4">
            <Image
              src={description.image}
              alt="score-icon"
              className={cn(
                'absolute -left-28',
                description.image === traffic && 'top-10 -left-32'
              )}
              width={219}
            />
            <span className="px-5 py-2 bg-[#9D5C15] text-[#F8F8F8] rounded-[15px] text-[24px]">
              {description.subtitle}
            </span>
            <p className="text-[#6D441B] text-[20px] text-center min-h-[60px]">{comment || ' '}</p>
          </div>

          <div className="flex gap-5">
            <PrimaryButton onClick={() => router.push('/main')} variant="md" color="yellow">
              홈으로
            </PrimaryButton>
            <PrimaryButton onClick={onRetry} variant="md" color="green">
              다시하기
            </PrimaryButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreBoard;
