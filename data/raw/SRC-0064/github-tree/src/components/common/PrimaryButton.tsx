'use client';

import React, { useMemo } from 'react';
import Image from 'next/image';
import { PrimaryButtonProps } from '@/types/common/button';
import { cn } from '@/lib/utils';
import buttonCircleIcon from '@/assets/icons/button-circle.svg';
import buttonCircleIconGray from '@/assets/icons/button-circle-dark.svg';
import buttonCircleIconGreen from '@/assets/icons/button-circle-green.svg';
import buttonCircleIconRed from '@/assets/icons/button-circle-red.svg';
import buttonCircleIconYellow from '@/assets/icons/button-circle-yellow.svg';

const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  children,
  onClick,
  variant = 'md',
  color = 'orange',
  disabled = false,
  className,
}) => {
  const colorStyles = {
    orange: {
      topColor: '#FB9A10',
      bottomColor: '#FB870A',
      borderColor: '#A4570C',
      icon: buttonCircleIcon,
    },
    gray: {
      topColor: '#CECCCA',
      bottomColor: '#E9E9E9',
      borderColor: '#6B6764',
      icon: buttonCircleIconGray,
    },
    green: {
      topColor: '#8ADC18',
      bottomColor: '#54C600',
      borderColor: '#0D4300',
      icon: buttonCircleIconGreen,
    },
    red: {
      topColor: '#F54905',
      bottomColor: '#F51E00',
      borderColor: '#781009',
      icon: buttonCircleIconRed,
    },
    yellow: {
      topColor: '#FFCC23',
      bottomColor: '#FFB316',
      borderColor: '#7F4F1A',
      icon: buttonCircleIconYellow,
    },
  };

  // variant별 스타일 정의
  const variantStyles = {
    xs: {
      fontSize: '26px',
      borderRadius: '25px',
      borderWidth: 6,
      contentWidth: 119,
      contentHeight: 66,
      imageWidth: 15,
      imageHeight: 11,
      imageTop: '7px',
      imageLeft: '15px',
      textStrokeWidth: 3,
    },
    sm: {
      fontSize: '34px',
      borderRadius: '34px',
      borderWidth: 6,
      contentWidth: 154,
      contentHeight: 79,
      imageWidth: 18,
      imageHeight: 13,
      imageLeft: '17px',
      imageTop: '7px',
      textStrokeWidth: 3.5,
    },
    md: {
      fontSize: '34px',
      borderRadius: '34px',
      borderWidth: 7,
      contentWidth: 203,
      contentHeight: 79,
      imageWidth: 18,
      imageHeight: 13,
      imageLeft: '17px',
      imageTop: '7px',
      textStrokeWidth: 4.5,
    },
    lg: {
      fontSize: '53.5px',
      borderRadius: '50px',
      borderWidth: 9,
      contentWidth: 246,
      contentHeight: 136,
      imageWidth: 28,
      imageHeight: 21,
      imageLeft: '27px',
      imageTop: '11px',
      textStrokeWidth: 5.5,
    },
  };

  const currentVariant = variantStyles[variant];
  const currentColor = colorStyles[color];

  // hydration 에러 방지
  const borderLayers = useMemo(() => {
    return [...Array(32)].map((_, i) => {
      const angle = (i * Math.PI * 2) / 32;
      const x = Math.cos(angle) * 3.5;
      const y = Math.sin(angle) * 3.5;
      return {
        x: x.toFixed(5),
        y: y.toFixed(5),
      };
    });
  }, []);

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
        backgroundColor: currentColor.bottomColor,
        border: `${currentVariant.borderWidth}px solid ${currentColor.borderColor}`,
        borderRadius: currentVariant.borderRadius,
        width: `${currentVariant.contentWidth + currentVariant.borderWidth * 2}px`,
        height: `${currentVariant.contentHeight + currentVariant.borderWidth * 2}px`,
      }}
    >
      <Image
        src={currentColor.icon}
        alt="button circle icon"
        className="absolute z-10 pointer-events-none"
        style={{
          left: currentVariant.imageLeft,
          top: currentVariant.imageTop,
        }}
        width={currentVariant.imageWidth}
        height={currentVariant.imageHeight}
        unoptimized
      />
      <div
        className="absolute inset-0 clip-button-curve"
        style={{
          backgroundColor: currentColor.topColor,
        }}
      />
      {disabled && <div className="absolute inset-0 z-100 bg-[#00000033]" />}
      <span
        className="relative z-30 text-center"
        style={{
          fontFamily: 'NanumSquareRoundExtraBold, sans-serif',
          fontSize: currentVariant.fontSize,
          fontStyle: 'normal',
          fontWeight: 800,
          lineHeight: 'normal',
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
              color: currentColor.borderColor,
              transform: `translate(${layer.x}px, ${layer.y}px)`,
              zIndex: 1,
              WebkitTextStrokeWidth: currentVariant.textStrokeWidth,
            }}
          >
            {children}
          </span>
        ))}
        {/* 메인 텍스트 레이어 */}
        <span
          style={{
            position: 'relative',
            color: '#FBF6ED',
            zIndex: 2,
          }}
        >
          {children}
        </span>
      </span>
    </button>
  );
};

export default PrimaryButton;
