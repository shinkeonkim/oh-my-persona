'use client';

import React, { useEffect } from 'react';
import { cn } from '@/lib/utils';

type ToastVariant = 'success' | 'error';

interface ToastProps {
  message: string;
  isOpen: boolean;
  variant?: ToastVariant;
  duration?: number;
  onClose?: () => void;
}

const Toast: React.FC<ToastProps> = ({
  message,
  isOpen,
  variant = 'success',
  duration = 3000,
  onClose,
}) => {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    if (!onClose) {
      return;
    }

    const timer = window.setTimeout(onClose, duration);
    return () => window.clearTimeout(timer);
  }, [isOpen, duration, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed left-1/2 top-[40px] z-50 flex -translate-x-1/2 items-center justify-center rounded-[30px] border-[6px] border-[#68482A] bg-white px-12 py-6 shadow-lg">
      <p
        className={cn(
          'text-2xl font-extrabold',
          variant === 'success' ? 'text-[#3D7F0B]' : 'text-[#CE2D2D]'
        )}
      >
        {message}
      </p>
    </div>
  );
};

export default Toast;
