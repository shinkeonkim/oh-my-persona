import { cn } from '@/lib/utils';
import React from 'react';

interface ProgressBarProps {
  progress: number;
  type?: 'default' | 'starGame';
}

const ProgressBar = ({ progress, type = 'default' }: ProgressBarProps) => {
  const isStarGame = type === 'starGame';

  return (
    <div
      className={`w-full ${
        isStarGame ? 'max-w-[479px] h-4' : 'max-w-[795px] h-6'
      } bg-progress-bar-bg rounded-full overflow-hidden`}
    >
      <div
        className={`relative h-full rounded-full shadow-md transition-[width] duration-[1000ms] ease-[cubic-bezier(0.25,0.1,0.25,1)]
          ${
            isStarGame
              ? 'bg-gradient-to-r from-[#FFA600] via-[#F68181] to-[#F05E5E] border-4'
              : 'bg-gradient-to-r from-progress-bar-left to-progress-bar-right border-4 border-progress-bar-border'
          }
        `}
        style={
          isStarGame
            ? {
                borderImage: 'linear-gradient(to right, #D87315, #DB4E6C) 1',
                borderStyle: 'solid',
                boxSizing: 'border-box',
                boxShadow: 'inset 0 -6px 5px rgba(180, 32, 32, 0.25)',
                width: `${progress}%`,
              }
            : {
                boxSizing: 'border-box',
                boxShadow: 'inset 0 -6px 5px rgba(180, 32, 32, 0.25)',
                width: `${progress}%`,
              }
        }
      >
        <div
          className={cn(
            'absolute top-0.5 right-4 h-1 rounded-[15px] transition-all duration-500',
            isStarGame ? 'bg-[#F9CB77] opacity-40' : 'bg-white/60 '
          )}
          style={{
            width: progress < 15 ? '20px' : '78px',
          }}
        />

        <div
          className={cn(
            'absolute top-0.5 right-1.5 w-[7px] h-1 rounded-[15px]',
            isStarGame ? 'bg-[#F9CB77] opacity-40' : 'bg-white/60'
          )}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
