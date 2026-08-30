'use client';

import Logo from '@/components/common/Logo';
import React, { useState } from 'react';
import star from '@/assets/images/main-star.png';
import traffic from '@/assets/images/main-traffic.png';
import Image from 'next/image';
import PrimaryButton from '@/components/common/PrimaryButton';
import Modal from '@/components/common/Modal';
import ModalTitle from '@/components/common/ModalTitle';
import { Input } from '@/components/common/Input';
import SecondaryButton from '@/components/common/SecondaryButton';
import { useRouter } from 'next/navigation';
import { getReportDetail, pollReportStatus } from '@/lib/api/report/reportApi';
import { logout } from '@/lib/api/auth/logout';
import { AxiosError } from 'axios';

interface ReportErrorResponse {
  errorCode?: string;
}

type ModalState = null | { type: 'pin' } | { type: 'message'; text: string } | { type: 'effect' };

const Main = () => {
  const [modal, setModal] = useState<ModalState>(null);
  const [pin, setPin] = useState('');
  const router = useRouter();
  const [isEffectModalOpen, setIsEffectModalOpen] = useState(false);

  const closeModal = () => {
    setModal(null);
  };

  const handleSubmitPin = async () => {
    if (!pin.trim()) {
      setModal({ type: 'message', text: 'PIN 번호를 입력해주세요.' });
      return;
    }

    try {
      setModal({ type: 'message', text: '로딩 중...' });

      const status = await pollReportStatus();
      console.log(status);

      if (status.status === 'no_games_played') {
        setPin('');
        setModal({ type: 'message', text: '각 게임을 1번 이상 플레이 해주세요!' });
        return;
      }

      if (!status || status.status !== 'completed') {
        setModal({ type: 'message', text: '레포트 생성 중 오류가 발생했습니다.' });
        return;
      }

      const detail = await getReportDetail(pin);
      sessionStorage.setItem('reportData', JSON.stringify(detail));
      router.push('/report');
    } catch (error) {
      const err = error as AxiosError<ReportErrorResponse>;
      const data = err.response?.data;

      if (data?.errorCode === 'COMMON_422') {
        setPin('');
        setModal({ type: 'message', text: 'PIN 번호가 틀렸습니다.' });
        return;
      }

      setModal({ type: 'message', text: '오류가 발생했습니다.' });
    }
  };

  return (
    <div className="flex flex-col min-h-[calc(100vh-40px)]">
      <Logo className="absolute top-14 left-8" />

      {/* 메인 영역 */}
      <div className="flex-grow px-20 pt-10 items-center flex gap-20 justify-center max-md:flex-col max-md:pt-32 max-md:pb-10 max-md:gap-10">
        <div className="flex flex-col items-center gap-5">
          <Image
            src={star}
            alt="Star"
            width={436}
            height={340}
            className="border-[18px] border-background-header rounded-[75px] hover:scale-105 transition-transform"
          />
          <PrimaryButton onClick={() => router.push('/game/star')}>시작하기</PrimaryButton>
        </div>

        <div className="flex flex-col items-center gap-5">
          <Image
            src={traffic}
            alt="Traffic"
            width={436}
            height={340}
            className="border-[18px] border-background-header rounded-[75px] hover:scale-105 transition-transform"
          />
          <PrimaryButton onClick={() => router.push('/game/traffic')}>시작하기</PrimaryButton>
        </div>
      </div>

      <footer className="relative h-[108px] w-full bg-background-header flex justify-end items-center px-5 md:px-10">
        <div>
          <div className="absolute bg-main-footer-glow w-[200px] h-1.5 rounded-full bottom-20 left-0"></div>
          <div className="absolute bg-main-footer-glow w-[140px] h-1.5 rounded-full bottom-16 left-10"></div>
          <div className="absolute bg-main-footer-glow w-[250px] h-1.5 rounded-full bottom-2 left-50"></div>
          <div className="absolute bg-main-footer-glow w-[205px] h-1.5 rounded-full bottom-10 left-120"></div>
          <div className="absolute bg-main-footer-glow w-[120px] h-1.5 rounded-full bottom-14 left-120"></div>
          <div className="absolute bg-main-footer-glow w-[100px] h-1.5 rounded-full bottom-3 right-0"></div>
          <div className="absolute bg-main-footer-glow w-[200px] h-1.5 rounded-full bottom-6 right-0"></div>
          <div className="absolute bg-main-footer-glow w-[200px] h-1.5 rounded-full bottom-20 right-10"></div>
        </div>
        <div className="flex gap-3">
          <SecondaryButton variant="focusResult" onClick={() => setModal({ type: 'pin' })}>
            집중력 학습 결과
          </SecondaryButton>

          <SecondaryButton variant="learningEffect" onClick={() => setIsEffectModalOpen(true)}>
            교육적 효과
          </SecondaryButton>

          <SecondaryButton
            variant="logout"
            onClick={async () => {
              try {
                await logout();
              } finally {
                if (typeof window !== 'undefined') window.sessionStorage.clear();
                router.push('/signin');
              }
            }}
          >
            로그아웃
          </SecondaryButton>
        </div>
      </footer>

      {/* 단일 모달 */}
      {modal && (
        <Modal
          type="confirm"
          size={modal.type === 'effect' ? 'large' : 'default'}
          isCloseBtn={true}
          onClose={closeModal}
          onConfirm={() => {
            if (modal.type === 'pin') handleSubmitPin();
            else closeModal();
          }}
        >
          {/* PIN 입력 모드 */}
          {modal.type === 'pin' && (
            <div className="flex flex-col items-center justify-center gap-5 h-[250px]">
              <p className="font-malrang text-5xl">비밀번호를 입력해주세요.</p>
              <p className="text-2xl font-extrabold text-modal-inner-text">
                레포트는 각 게임을 1번 이상 플레이 시 생성됩니다.
              </p>
              <Input
                variant="password"
                placeholder="비밀번호 입력"
                className="w-full mx-auto !border-modal-inner-input-border"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
              />
            </div>
          )}

          {/* 메시지 모드 */}
          {modal.type === 'message' && (
            <div className="flex items-center justify-center h-full">
              <p className="font-malrang text-5xl text-center whitespace-pre-line">{modal.text}</p>
            </div>
          )}
        </Modal>
      )}

      {isEffectModalOpen && (
        <Modal
          size="large"
          type="confirm"
          isCloseBtn={true}
          onConfirm={() => setIsEffectModalOpen(false)}
          onClose={() => setIsEffectModalOpen(false)}
        >
          <div className="flex flex-col items-start gap-5 h-[350px] overflow-y-auto scroll-bar">
            <div className="flex flex-col gap-5">
              <ModalTitle>뿅뿅 아기별</ModalTitle>
              <ul className="list-disc list-inside px-2 text-2xl font-extrabold space-y-3">
                <li>
                  이 게임은 정보를 잠시 동안 머릿속에 유지하고 조작하는 능력, 즉 작업 기억력을
                  직접적으로 훈련합니다.
                </li>
                <li>
                  작업 기억력은 학습 능력과 주의력 유지의 근간이 되는 핵심 인지 기능입니다. 순서
                  기억 훈련과 유사한 N-back 훈련을 포함한 작업 기억 훈련 프로그램이 아동의 유동
                  지능(Fluid Intelligence)과 주의력 통제 능력(Attention Control)을 향상시킨다는
                  연구가 다수 발표되었습니다. (Jaeggi et al., 2008)
                </li>
              </ul>
            </div>
            <div className="flex flex-col gap-5">
              <ModalTitle>꼬마 교통 지킴이</ModalTitle>
              <ul className="list-disc list-inside pl-2 text-2xl font-extrabold space-y-3">
                <li>
                  ‘꼬마 신호등 지킴이’의 핵심은 ‘빨간불’이 들어왔을 때, 이미 자동적으로 형성된
                  ‘움직이려는 반응(Go)’을 의도적으로 억제하는 능력을 훈련하는 것입니다.
                </li>
                <li>
                  Go/No-Go 과제는 인지 심리학 및 신경 과학 분야에서 충동성과 반응 억제 조절을
                  측정하는 표준 방법으로 널리 사용됩니다.
                </li>
                <li>
                  따라서 이 게임은 아동의 충동적인 행동 경향을 정량적인 실수율 데이터로 측정하고,
                  지속적인 훈련을 통해 자기 통제력을 향상시키는 데 도움을 줄 수 있습니다.
                </li>
              </ul>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Main;
