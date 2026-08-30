import Header from '@/components/common/Header';
import SignupBody from '@/components/signup/SignupBody';
import React from 'react';

const Signup = () => {
  return (
    <div className="flex flex-col items-center justify-center">
      <Header />
      <SignupBody />
    </div>
  );
};

export default Signup;
