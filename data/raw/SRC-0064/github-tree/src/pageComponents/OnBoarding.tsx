'use client';

import RegisteratonBody from '@/components/onBoarding/RegisteratonBody';
import PasswordBody from '@/components/onBoarding/PasswordBody';
import React, { useState } from 'react';
import Header from '@/components/common/Header';

type Step = 'registration' | 'password';

const OnBoarding = () => {
  const [step, setStep] = useState<Step>('registration');

  return (
    <div className="flex flex-col items-center">
      <Header />
      {step === 'registration' ? (
        <RegisteratonBody onNext={() => setStep('password')} />
      ) : (
        <PasswordBody />
      )}
    </div>
  );
};

export default OnBoarding;
