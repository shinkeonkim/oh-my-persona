'use client';

import React, { useMemo } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import buttonCircleIcon from '@/assets/icons/button-circle-yellow2.svg';

interface ModalTitleProps {
  children?: React.ReactNode;
  className?: string;
}

const ModalTitle: React.FC<ModalTitleProps> = ({ children, className }) => {
  const borderColor = '#9A5C1A';

  const style = {
    padding: '10px 30px',
    fontSize: '42px',
    borderRadius: '25px',
    borderWidth: 7,
    topColor: '#FFFFFF',
    bottomColor: '#F2B637',
    imageWidth: 21,
    imageHeight: 14,
  };

  const borderLayers = useMemo(() => {
    return [...Array(32)].map((_, i) => {
      const angle = (i * Math.PI * 2) / 32;
      const x = Math.cos(angle) * 3.5;
      const y = Math.sin(angle) * 3.5;
      return { x: x.toFixed(5), y: y.toFixed(5) };
    });
  }, []);

  return (
    <div
      className={cn(
        'relative flex items-center justify-center overflow-visible flex-shrink-0',
        className
      )}
      style={{
        backgroundColor: style.bottomColor,
        border: `${style.borderWidth}px solid ${borderColor}`,
        borderRadius: style.borderRadius,
        padding: style.padding,
        width: 'fit-content',
        minWidth: 'max-content',
      }}
    >
      {/* 좌상단 원형 장식 */}
      <Image
        src={buttonCircleIcon}
        alt="decorative circle"
        className="absolute left-[15px] top-[8px] z-10 pointer-events-none"
        width={style.imageWidth}
        height={style.imageHeight}
        unoptimized
      />

      {/* 실제 콘텐츠 */}
      <span
        className="relative z-30 text-center"
        style={{
          fontFamily: 'NanumSquareRoundExtraBold, sans-serif',
          fontSize: style.fontSize,
          fontStyle: 'normal',
          fontWeight: 800,
          lineHeight: `60px`,
          position: 'relative',
          display: 'inline-block',
          whiteSpace: 'nowrap',
        }}
      >
        {/* 외곽선 레이어 여러 겹 */}
        {borderLayers.map((layer, i) => (
          <span
            key={i}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              color: '#5B3715',
              transform: `translate(${layer.x}px, ${layer.y}px)`,
              zIndex: 1,
              WebkitTextStrokeWidth: 4.5,
              whiteSpace: 'nowrap',
            }}
          >
            {children}
          </span>
        ))}

        {/* 메인 텍스트 */}
        <span
          style={{
            position: 'relative',
            color: '#FBF6ED',
            zIndex: 2,
            whiteSpace: 'nowrap',
          }}
        >
          {children}
        </span>
      </span>
    </div>
  );
};

export default ModalTitle;
