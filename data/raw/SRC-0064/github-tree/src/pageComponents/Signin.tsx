import Header from '@/components/common/Header';
import SigninBody from '@/components/signin/SigninBody';
import React from 'react';

const Signin = () => {
  return (
    <div className="flex flex-col items-center justify-center">
      <Header />
      <SigninBody />
    </div>
  );
};

export default Signin;
