'use client';

import React from 'react';
import Image from 'next/image';
import { ButtonProps } from '@/types/common/button';
import { cn } from '@/lib/utils';
import buttonCircleIcon from '@/assets/icons/button-circle.svg';

const BaseButton: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'md',
  disabled = false,
  className,
}) => {
  const borderColor = '#A4570C';

  const variantStyles = {
    md: {
      padding: '21px 63px',
      fontSize: '46px',
      borderRadius: '33px',
      borderWidth: 10.35,
      contentWidth: 282,
      topColor: '#FB9A10',
      bottomColor: '#FB870A',
      imageWidth: 32,
      imageHeight: 24,
    },
    lg: {
      padding: '22px 270px',
      fontSize: '36px',
      borderRadius: '30px',
      borderWidth: 8,
      contentWidth: 676,
      topColor: '#FEAC07',
      bottomColor: '#FE9704',
      imageWidth: 25,
      imageHeight: 19,
    },
  };

  const currentVariant = variantStyles[variant];

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'relative flex items-center justify-center overflow-hidden transition-all duration-200',
        'disabled:cursor-not-allowed',
        'hover:scale-[1.02] active:scale-[0.98] disabled:hover:scale-100 disabled:active:scale-100',
        'flex-shrink-0',
        className
      )}
      style={{
        backgroundColor: currentVariant.bottomColor,
        border: `${currentVariant.borderWidth}px solid ${borderColor}`,
        borderRadius: currentVariant.borderRadius,
        padding: currentVariant.padding,
        width: `${currentVariant.contentWidth + currentVariant.borderWidth * 2}px`,
      }}
    >
      <Image
        src={buttonCircleIcon}
        alt="button circle icon"
        className="absolute left-[37px] top-[15px] z-10 pointer-events-none"
        width={currentVariant.imageWidth}
        height={currentVariant.imageHeight}
        unoptimized
      />
      <div
        className="absolute inset-0 clip-button-curve"
        style={{
          backgroundColor: currentVariant.topColor,
        }}
      />
      {disabled && <div className="absolute inset-0 z-20 bg-[#00000033]" />}
      <span
        className="font-malrang relative z-30 text-[#68482A] leading-[130%] tracking-[0.92px]"
        style={{
          fontSize: currentVariant.fontSize,
        }}
      >
        {children}
      </span>
    </button>
  );
};

export default BaseButton;
