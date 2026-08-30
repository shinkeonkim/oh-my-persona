'use client';

import React from 'react';
import Image from 'next/image';
import nextImage from '@/assets/icons/next.svg';
import { cn } from '@/lib/utils';

type DescriptionProps = {
  children: React.ReactNode;
  title: string;
  onClickNext: () => void;
  className?: string;
};

const Description = ({ children, title, onClickNext, className }: DescriptionProps) => {
  return (
    <div
      className={cn(
        'relative bg-[#EFB141] rounded-[36px] border-[6.5px] border-[#99622D] p-4',
        className
      )}
    >
      {/* 제목 */}
      <div className="absolute -top-12 left-15 z-10">
        <div className="relative bg-[#EEB041] py-[13px] px-[15px] rounded-[33px] border-[6px] border-[#99622D]">
          <div className="absolute top-1 left-8 bg-[#F9CC7E] w-[45px] h-[4px] rounded-full"></div>
          <div className="font-nanum rounded-[19px] px-[35px] py-[11px] bg-[#9D5C15] text-[34px] text-[#FBF6ED]">
            <p>{title}</p>
          </div>
        </div>
      </div>

      <div className="absolute top-1 left-1/2 -translate-x-1/2 bg-[#F9CC7E] w-[426px] h-[5px] rounded-full"></div>
      <div className="relative bg-[#F8E29B] pl-[63px] pr-[84px] pt-[58px] pb-[52px] rounded-[24px] border-[6.5px] border-[#99622D]">
        <p className="no-wrap font-nanum text-[30px] font-black text-[#443A26]">{children}</p>
        <button onClick={onClickNext}>
          <Image
            src={nextImage}
            alt="next"
            className="absolute bottom-[33px] right-[56px] hover:scale-105 transition-transform"
            width={60}
            height={60}
          />
        </button>
      </div>
    </div>
  );
};

export default Description;
