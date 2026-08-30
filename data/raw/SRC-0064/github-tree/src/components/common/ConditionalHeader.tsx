'use client';

import React from 'react';
import { usePathname } from 'next/navigation';

const HIDDEN_PATH_PREFIXES = ['/game'];

const ConditionalHeader = () => {
  const pathname = usePathname();

  if (pathname && HIDDEN_PATH_PREFIXES.some((prefix) => pathname.startsWith(prefix))) {
    return null;
  }

  return <header className="h-10 w-full bg-background-header" />;
};

export default ConditionalHeader;
