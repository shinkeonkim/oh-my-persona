'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import PrimaryButton from '../common/PrimaryButton';
import { Input } from '../common/Input';
import Modal from '../common/Modal';
import { setReportPin } from '@/lib/api/auth/passwordApi';

type ModalType = 'success' | 'error' | null;

const PasswordBody = () => {
  const router = useRouter();
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [modalType, setModalType] = useState<ModalType>(null);
  const [isTouched, setIsTouched] = useState(false);

  const PASSWORD_GUIDE_MESSAGE = '비밀번호는 숫자 4~6자리로 입력해 주세요.';

  const isPasswordValid = useMemo(() => /^\d{4,6}$/.test(password), [password]);

  const isConfirmDisabled = !isPasswordValid || loading;

  const handleConfirm = async () => {
    if (!isPasswordValid) {
      return;
    }

    try {
      setLoading(true);
      const res = await setReportPin({ pin: password });

      console.log('📦 Response:', res);

      if (res.isSuccess) {
        console.log('비밀번호 설정 완료 ✅');
        setModalType('success');
      } else {
        console.warn('⚠️ 비밀번호 설정 실패:', res);
        setModalType('error');
      }
    } catch (error) {
      console.error('❌ 비밀번호 설정 실패:', error);
      setModalType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleModalConfirm = () => {
    if (modalType === 'success') {
      setModalType(null);
      router.push('/start');
    } else {
      setModalType(null);
    }
  };

  return (
    <>
      <div className="flex flex-col items-center">
        <h2 className="text-[26px] mb-[94px] font-nanum font-extrabold text-[#53514F]">
          아이의 학습 결과를 확인할 수 있는 레포트용 비밀번호를 설정해 주세요.
        </h2>

        <div className="flex justify-center mb-[54px]">
          <Input
            label="비밀번호 4~6자리"
            variant="password"
            type="password"
            value={password}
            onChange={(e) => {
              if (!isTouched) {
                setIsTouched(true);
              }

              const nextValue = e.target.value.slice(0, 6);
              setPassword(nextValue);
            }}
            error={isTouched && !isPasswordValid}
            errorText={isTouched && !isPasswordValid ? PASSWORD_GUIDE_MESSAGE : undefined}
            helperText={!isTouched ? PASSWORD_GUIDE_MESSAGE : undefined}
          />
        </div>

        <div className="flex justify-center">
          <PrimaryButton
            variant="xs"
            color="orange"
            disabled={isConfirmDisabled}
            onClick={handleConfirm}
          >
            {loading ? '등록 중...' : '완료'}
          </PrimaryButton>
        </div>
      </div>

      {/* ✅ 모달 */}
      {modalType && (
        <Modal type="confirm" onConfirm={handleModalConfirm}>
          <div className="flex h-full items-center justify-center">
            {modalType === 'success' ? (
              <p className="font-malrang text-5xl text-[#68482A]">아이 등록이 완료되었습니다.</p>
            ) : (
              <p className="font-malrang text-4xl text-[#C0392B] text-center">
                비밀번호 설정에 실패했습니다.
                <br />
                다시 시도해주세요.
              </p>
            )}
          </div>
        </Modal>
      )}
    </>
  );
};

export default PasswordBody;
