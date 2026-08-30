'use client';

import React, { forwardRef, useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { DropdownSelect } from '@/components/ui/dropdown-select';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
  variant?: 'default' | 'birth' | 'text' | 'gender' | 'password';
  label?: string;
  required?: boolean;
  error?: boolean;
  errorText?: string;
  helperText?: string;
  helperTextVariant?: 'default' | 'success' | 'error';
  onBirthComplete?: (isComplete: boolean) => void;
  onBirthChange?: (birth: string) => void;
  onGenderChange?: (gender: 'M' | 'F') => void;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      variant = 'default',
      label,
      required,
      error,
      errorText,
      helperText,
      helperTextVariant = 'default',
      onBirthComplete,
      onBirthChange,
      onGenderChange,
      ...props
    },
    ref
  ) => {
    const [gender, setGender] = useState<'male' | 'female' | null>(null);
    const [year, setYear] = useState('');
    const [month, setMonth] = useState('');

    useEffect(() => {
      if (variant === 'birth' && onBirthComplete) {
        const complete = !!(year && month);
        onBirthComplete(complete);
        if (complete && onBirthChange) {
          const birthValue = `${year.replace('년', '')}-${month.replace('월', '').padStart(2, '0')}`;
          onBirthChange(birthValue);
        }
      }
    }, [year, month, variant, onBirthComplete, onBirthChange]);

    // 년 / 월 옵션
    const startYear = 1990;
    const endYear = 2022;
    const years = Array.from({ length: endYear - startYear + 1 }, (_, i) => `${endYear - i}년`);
    const months = Array.from({ length: 12 }, (_, i) => `${i + 1}월`);

    const baseClass = cn(
      'flex font-bold justify-between items-center gap-2 rounded-3xl border-[7px] bg-input-bg px-7.5 py-3 transition h-[78px]',
      error ? 'border-error-text' : 'border-input-border'
    );

    const renderContent = () => {
      switch (variant) {
        case 'birth':
          return (
            <div className="flex gap-4 ml-auto">
              <DropdownSelect
                label="년"
                options={years}
                value={year}
                onChange={(val: string) => setYear(val)}
                placeholder="년도"
              />
              <DropdownSelect
                label="월"
                options={months}
                value={month}
                onChange={(val: string) => setMonth(val)}
                placeholder="월"
              />
            </div>
          );

        case 'text':
          return (
            <input
              ref={ref}
              {...props}
              className={cn(
                'flex-1 bg-transparent outline-none text-input-text placeholder:text-placeholder-text text-right',
                error && 'text-error-text placeholder:text-error-text'
              )}
            />
          );

        case 'gender':
          return (
            <div className={cn('flex gap-4 ml-auto', error && 'text-error-text')}>
              <div className="flex gap-1.5 items-center">
                <button
                  type="button"
                  className={cn(
                    'w-[22px] h-[22px] rounded-full border flex items-center justify-center',
                    gender === 'male'
                      ? error
                        ? 'bg-error-text border-none'
                        : 'bg-button-text border-none'
                      : 'border-[#BDBDBD]'
                  )}
                  onClick={() => {
                    setGender('male');
                    onGenderChange?.('M');
                  }}
                >
                  <div
                    className={cn(
                      'w-2 h-2 rounded-full bg-input-bg',
                      gender === 'male' ? 'block' : 'hidden'
                    )}
                  />
                </button>
                <p>남자</p>
              </div>

              <div className="flex gap-1.5 items-center">
                <button
                  type="button"
                  className={cn(
                    'w-[22px] h-[22px] rounded-full border flex items-center justify-center',
                    gender === 'female'
                      ? error
                        ? 'bg-error-text border-none'
                        : 'bg-button-text border-none'
                      : 'border-[#BDBDBD]'
                  )}
                  onClick={() => {
                    setGender('female');
                    onGenderChange?.('F');
                  }}
                >
                  <div
                    className={cn(
                      'w-2 h-2 rounded-full bg-input-bg',
                      gender === 'female' ? 'block' : 'hidden'
                    )}
                  />
                </button>
                <p>여자</p>
              </div>
            </div>
          );

        case 'password':
          return (
            <input
              ref={ref}
              {...props}
              className={cn(
                'flex-1 bg-transparent outline-none text-input-text placeholder:text-placeholder-text text-right',
                error && 'text-error-text placeholder:text-error-text'
              )}
            />
          );

        default:
          return (
            <input
              ref={ref}
              {...props}
              className={cn(
                'flex-1 bg-transparent outline-none text-input-text placeholder:text-placeholder-text',
                error && 'text-error-text placeholder:text-error-text'
              )}
            />
          );
      }
    };

    const messageText = errorText ?? helperText ?? '';
    const messageVariant = errorText ? 'error' : helperTextVariant;

    return (
      <div className="w-full flex flex-col gap-1 text-xl">
        <div className={cn(baseClass, className)}>
          {label && (
            <label
              className={cn(
                'text-placeholder-text shrink-0 flex items-center gap-1',
                error && 'text-error-text'
              )}
            >
              {label}
              {required && <span className="text-error-text text-lg">*</span>}
            </label>
          )}
          {renderContent()}
        </div>

        {/* 메시지 영역 */}
        {messageText && (
          <p
            className={cn(
              'ml-4 mt-1 text-sm leading-none font-bold',
              messageVariant === 'error' && 'text-error-text',
              messageVariant === 'success' && 'text-[#3D7F0B]',
              messageVariant === 'default' && 'text-placeholder-text'
            )}
          >
            {messageText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
