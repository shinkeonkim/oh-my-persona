import Image from 'next/image';
import React from 'react';
import logoImage from '@/assets/images/bulb.png';
import { cn } from '@/lib/utils';

const Logo = ({ className }: { className?: string }) => {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <p className="font-malrang text-5xl">깜빡이</p>
      <Image src={logoImage} alt="Logo" width={44} height={40} />
    </div>
  );
};

export default Logo;
