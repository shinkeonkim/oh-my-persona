'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Round from '@/pageComponents/traffic-game/round/Round';

const TrafficRoundPage = () => {
  const router = useRouter();
  return <Round onBack={() => router.replace('/main')} />;
};

export default TrafficRoundPage;
