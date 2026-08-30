import Image from 'next/image';
import React from 'react';
import character from '@/assets/images/character.png';

const Header = () => {
  return (
    <header className="flex flex-col items-center w-full">
      <div className="flex items-center justify-center mt-[30px] mb-[54px] gap-4">
        <h1 className="text-[85.3px] font-malrang">깜빡이</h1>
        <Image src={character} alt="character" width={83} height={70} />
      </div>
    </header>
  );
};

export default Header;
