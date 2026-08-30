'use client';

import Image from 'next/image';
import bulb from '@/assets/images/bulb.png';
import offBulb from '@/assets/images/off_bulb.png';

interface BulbImageProps {
  isOn: boolean;
  width?: number;
  height?: number;
}

export default function BulbImage({ isOn, width = 160, height = 160 }: BulbImageProps) {
  return (
    <div className="relative" style={{ width, height }}>
      <Image
        src={bulb}
        alt="On bulb"
        fill
        className={`object-contain transition-opacity duration-700 ease-in-out ${
          isOn ? 'opacity-100' : 'opacity-0'
        }`}
      />
      {/* 꺼진 전구 */}
      <Image
        src={offBulb}
        alt="Off bulb"
        fill
        className={`object-contain transition-opacity duration-700 ease-in-out ${
          isOn ? 'opacity-0' : 'opacity-100'
        }`}
      />
    </div>
  );
}
