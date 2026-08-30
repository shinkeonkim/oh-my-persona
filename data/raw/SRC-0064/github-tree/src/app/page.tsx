'use client';
import BaseButton from '@/components/common/BaseButton';
import BulbImage from '@/components/images/BulbImage';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  
  return (
    <main className="h-[calc(100vh-40px)] flex flex-col">
      <div className="flex flex-col items-center justify-center flex-1 gap-[117px]">
        <div className="flex flex-col items-center">
          <div className="flex flex-col-reverse items-center md:gap-6 md:flex-row md:justify-center">
            <p className="text-[100px] md:text-[140px] font-malrang">깜빡이</p>
            <BulbImage isOn={true} width={120} height={120} />
          </div>

          <p className="text-[32px] max-md:text-[25px] font-malrang">보호자와 함께 플레이하세요!</p>
        </div>

        <BaseButton variant="md" onClick={() => router.push('/signin')}>시작하기</BaseButton>
      </div>
    </main>
  );
}
