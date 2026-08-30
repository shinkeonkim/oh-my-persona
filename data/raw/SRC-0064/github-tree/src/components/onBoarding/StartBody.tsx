'use client';

import Image from 'next/image';
import React from 'react';
import { useRouter } from 'next/navigation';
import startBodyImage from '@/assets/images/logo-light.png';
import PrimaryButton from '../common/PrimaryButton';

const StartBody = () => {
  const router = useRouter();
  return (
    <div className="flex flex-col items-center">
      <Image src={startBodyImage} alt="start body" width={216} height={180} />
      <p className="text-[32px] mt-[48px] mb-[50px] font-nanum font-extrabold text-[#40362B]">
        이제 집중력 전구를 깜빡 켜볼까요?
      </p>
      <PrimaryButton variant="md" color="orange" onClick={() => router.push('/main')}>
        시작하기
      </PrimaryButton>
    </div>
  );
};

export default StartBody;
