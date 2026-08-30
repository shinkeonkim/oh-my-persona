'use client';

import * as React from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DropdownSelectProps {
  label?: string;
  value?: string;
  options: string[];
  onChange?: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export const DropdownSelect: React.FC<DropdownSelectProps> = ({
  value,
  options,
  onChange,
  placeholder = '선택',
  className,
}) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className={cn(
          'flex items-center justify-around gap-2 min-w-[70px] bg-transparent outline-none text-input-text',
          className
        )}
      >
        <span>{value || placeholder}</span>
        <ChevronDown className="w-4 h-4 opacity-70" />
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="bg-input-bg shadow-md rounded-xl p-1 h-40 overflow-y-auto text-input-text font-bold border-input-border"
      >
        {options.map((opt) => (
          <DropdownMenuItem
            key={opt}
            onSelect={() => onChange?.(opt)}
            className="cursor-pointer hover:bg-input-border px-3 py-2 rounded-xl text-md"
          >
            {opt}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
