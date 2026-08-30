'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '../common/Input';
import BaseButton from '../common/BaseButton';
import { checkUsername } from '@/lib/api/auth/checkUsername';
import { signup } from '@/lib/api/auth/signup';
import {
  PASSWORD_MIN_LENGTH,
  PASSWORD_VALIDATION_MESSAGE,
  USERNAME_MIN_LENGTH,
  USERNAME_VALIDATION_MESSAGE,
} from '@/lib/constants/auth';

const SignupBody = () => {
  const [username, setUsername] = useState('');
  const [usernameMessage, setUsernameMessage] = useState('');
  const [isUsernameError, setIsUsernameError] = useState(false);
  const [isUsernameChecking, setIsUsernameChecking] = useState(false);
  const [isUsernameAvailable, setIsUsernameAvailable] = useState(false);

  const [password, setPassword] = useState('');
  const [isPasswordTouched, setIsPasswordTouched] = useState(false);
  const [formMessage, setFormMessage] = useState('');
  const [isFormError, setIsFormError] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const router = useRouter();

  const isUsernameFormatValid = useMemo(() => {
    if (!username) {
      return false;
    }

    const trimmed = username.trim();

    if (trimmed.length < USERNAME_MIN_LENGTH) {
      return false;
    }

    const hasLetter = /[A-Za-z]/.test(trimmed);
    const hasNumber = /[0-9]/.test(trimmed);

    return hasLetter && hasNumber;
  }, [username]);

  const isPasswordValid = useMemo(() => {
    if (!password) {
      return false;
    }

    const hasLetter = /[A-Za-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);

    return password.length >= PASSWORD_MIN_LENGTH && hasLetter && hasNumber;
  }, [password]);

  const handleUsernameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(event.target.value);
    setIsUsernameAvailable(false);
    setIsUsernameError(false);
    setUsernameMessage('');
    setFormMessage('');
    setIsFormError(false);
  };

  const handleCheckUsername = async () => {
    if (!isUsernameFormatValid) {
      setIsUsernameError(true);
      setUsernameMessage(USERNAME_VALIDATION_MESSAGE);
      return;
    }

    setIsUsernameChecking(true);
    setIsUsernameAvailable(false);
    setIsUsernameError(false);
    setUsernameMessage('');

    try {
      const response = await checkUsername(username.trim());

      if (response.exists) {
        setIsUsernameError(true);
        setUsernameMessage('이미 사용 중인 아이디예요.');
        setIsUsernameAvailable(false);
      } else {
        setIsUsernameAvailable(true);
        setUsernameMessage('사용 가능한 아이디입니다.');
      }
    } catch (error) {
      console.error('아이디 중복 확인 중 오류가 발생했어요.', error);
      setIsUsernameError(true);
      setUsernameMessage('아이디 중복 확인 중 문제가 발생했어요. 잠시 후 다시 시도해 주세요.');
      setIsUsernameAvailable(false);
    } finally {
      setIsUsernameChecking(false);
    }
  };

  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!isPasswordTouched) {
      setIsPasswordTouched(true);
    }

    setPassword(event.target.value);
  };

  const handleRegister = async () => {
    if (!isUsernameAvailable || !isPasswordValid) {
      return;
    }

    setIsRegistering(true);
    setFormMessage('');
    setIsFormError(false);

    try {
      await signup({
        username: username.trim(),
        password1: password,
        password2: password,
      });

      if (typeof window !== 'undefined') {
        window.sessionStorage.setItem(
          'signinToast',
          JSON.stringify({
            message: '회원가입이 완료되었어요. 로그인해 주세요!',
            variant: 'success',
          })
        );
      }

      router.push('/signin');
    } catch (error) {
      console.error('회원가입 중 오류가 발생했어요.', error);
      setFormMessage('회원가입 중 문제가 발생했어요. 잠시 후 다시 시도해 주세요.');
      setIsFormError(true);
    } finally {
      setIsRegistering(false);
    }
  };

  const isSignupDisabled = !(isUsernameAvailable && isPasswordValid) || isRegistering;

  const passwordErrorText =
    isPasswordTouched && !isPasswordValid ? PASSWORD_VALIDATION_MESSAGE : undefined;

  return (
    <div className="flex flex-col">
      <div className="flex flex-col gap-[20px] mb-[60px]">
        <div className="flex flex-col gap-4">
          <div className="flex items-start gap-6">
            <Input
              placeholder="아이디 입력 (영문, 숫자 포함 4자리 이상)"
              value={username}
              onChange={handleUsernameChange}
              error={isUsernameError}
              errorText={isUsernameError ? usernameMessage : undefined}
              helperText={!isUsernameError ? usernameMessage : undefined}
              helperTextVariant={!isUsernameError && usernameMessage ? 'success' : 'default'}
            />
            <button
              type="button"
              onClick={handleCheckUsername}
              disabled={isUsernameChecking}
              className="cursor-pointer font-extrabold px-[24.5px] py-[26px] rounded-[24px] text-xl whitespace-nowrap transition disabled:cursor-not-allowed"
              style={{
                backgroundColor: isUsernameAvailable ? '#D1F1B2' : '#E7E1D7',
                color: isUsernameAvailable ? '#3D7F0B' : '#BAAB96',
              }}
            >
              {isUsernameChecking ? '확인중...' : '중복확인'}
            </button>
          </div>
        </div>
        <Input
          placeholder="비밀번호 입력 (영문, 숫자 포함 8자리 이상)"
          type="password"
          value={password}
          onChange={handlePasswordChange}
          error={!!passwordErrorText && isPasswordTouched}
          errorText={passwordErrorText}
        />
      </div>
      <BaseButton variant="lg" disabled={isSignupDisabled} onClick={handleRegister}>
        회원가입
      </BaseButton>
      <div className="text-center text-xl font-bold mb-[10px] mt-[10px]">
        {formMessage ? (
          <span className={isFormError ? 'text-[#CE2D2D]' : 'text-[#3D7F0B]'}>{formMessage}</span>
        ) : (
          <span className="text-transparent">placeholder</span>
        )}
      </div>
      <a
        href="/signin"
        className="text-center underline font-bold decoration-1 underline-offset-7 text-xl text-[#D3770E]"
      >
        이미 계정이 있으신가요?
      </a>
    </div>
  );
};

export default SignupBody;
