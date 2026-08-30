'use client';

import React, { useState } from 'react';
import PrimaryButton from '../common/PrimaryButton';
import { Input } from '../common/Input';
import { createChildUser } from '@/lib/api/auth/childApi';

interface RegisteratonBodyProps {
  onNext?: () => void;
}

const RegisteratonBody: React.FC<RegisteratonBodyProps> = ({ onNext }) => {
  const [childName, setChildName] = useState('');
  const [isBirthComplete, setIsBirthComplete] = useState(false);
  const [birth, setBirth] = useState('');
  const [gender, setGender] = useState<'M' | 'F' | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const isConfirmDisabled = !childName.trim() || !isBirthComplete;

  const handleConfirm = async () => {
    try {
      setLoading(true);
      await createChildUser({
        name: childName,
        birthYear: parseInt(birth.split('-')[0], 10),
        gender: gender ?? 'M',
      });
      onNext?.();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-[690px]">
      <h2 className="mb-[54px] text-[26px] font-nanum font-extrabold text-[#53514F]">
        아이 정보를 알려주세요
      </h2>

      <div className="flex flex-col ">
        <Input
          label="아이 이름"
          variant="text"
          value={childName}
          onChange={(e) => setChildName(e.target.value)}
        />

        <Input
          label="아이 생년/월"
          variant="birth"
          onBirthComplete={setIsBirthComplete}
          onBirthChange={setBirth}
        />

        <Input label="아이 성별(선택)" variant="gender" onGenderChange={setGender} />
      </div>

      <div className="flex justify-end gap-[26px] mt-[14px]">
        <PrimaryButton variant="xs" color="gray">
          취소
        </PrimaryButton>
        <PrimaryButton
          variant="xs"
          color="orange"
          disabled={isConfirmDisabled || loading}
          onClick={handleConfirm}
        >
          {loading ? '등록 중...' : '확인'}
        </PrimaryButton>
      </div>
    </div>
  );
};

export default RegisteratonBody;
