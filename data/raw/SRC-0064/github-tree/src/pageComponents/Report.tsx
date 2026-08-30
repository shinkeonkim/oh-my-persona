'use client';

import Logo from '@/components/common/Logo';
import Image from 'next/image';
import React, { useEffect, useState } from 'react';
import buttonCircleImage from '@/assets/icons/button-circle-yellow2.svg';
import arrowImage from '@/assets/images/arrow.png';
import { Dot } from 'lucide-react';
import SecondaryButton from '@/components/common/SecondaryButton';
import Modal from '@/components/common/Modal';
import { Input } from '@/components/common/Input';
import cancelImage from '@/assets/icons/cancel.svg';
import { useRouter, useSearchParams } from 'next/navigation';

import { sendReportEmail, getReportDetail } from '@/lib/api/report/reportApi';
import type { ReportDetailResponse, GameReport } from '@/lib/api/report/reportApi';

const Report = () => {
  const router = useRouter();
  const params = useSearchParams();

  // 🔥 URL에 BOT_TOKEN이 있는 경우 (PDF 크롤러)
  const BOT_TOKEN = params.get('BOT_TOKEN');

  const [report, setReport] = useState<ReportDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [shareClicked, setShareClicked] = useState(false);
  const [email, setEmail] = useState('');
  const [sending, setSending] = useState(false);
  const [sendModalOpen, setSendModalOpen] = useState(false);

  const getGameName = (gameCode: string) => {
    switch (gameCode) {
      case 'KIDS_TRAFFIC':
        return '꼬마 교통 지킴이';
      case 'BB_STAR':
        return '뿅뿅 아기별';
      default:
        return '게임';
    }
  };

  const getReportName = (gameCode: string) => {
    switch (gameCode) {
      case 'KIDS_TRAFFIC':
        return '충동 조절 점수';
      case 'BB_STAR':
        return '주의력 점수';
      default:
        return '게임';
    }
  };

  // BOT_TOKEN 모드 / 일반 모드 구분
  useEffect(() => {
    const fetchData = async () => {
      if (BOT_TOKEN) {
        // BOT_TOKEN 모드일 때는 sessionStorage 검사 금지!!
        try {
          const detail = await getReportDetail(null, BOT_TOKEN);
          setReport(detail);
        } catch (e) {
          alert('BOT_TOKEN 인증 오류');
          router.push('/main');
          return;
        } finally {
          setLoading(false);
        }
        return;
      }

      // 🔥 일반 사용자 모드
      const stored = sessionStorage.getItem('reportData');
      if (!stored) {
        alert('리포트 데이터가 없습니다. 다시 PIN을 입력해주세요.');
        router.push('/main');
        return;
      }

      setReport(JSON.parse(stored));
      setLoading(false);
    };

    fetchData();
  }, [BOT_TOKEN, router]);

  const handleSendEmail = async () => {
    if (sending) return; // 중복 클릭 방지

    if (!email.trim()) {
      alert('이메일 주소를 입력해주세요.');
      return;
    }

    try {
      setSending(true);
      await sendReportEmail(email);
      setSendModalOpen(true);
      setShareClicked(false);
      setEmail('');
    } catch (err) {
      console.error('❌ 이메일 전송 실패:', err);
      alert('메일 전송 중 오류가 발생했습니다.');
    } finally {
      setSending(false);
    }
  };

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center h-screen text-4xl font-malrang">
        리포트를 불러오는 중입니다...
      </div>
    );

  if (!report) return null;

  // 🔥 BOT_TOKEN 모드일 때 UI 비활성화
  const hideShareButton = Boolean(BOT_TOKEN);
  const hideCloseButton = Boolean(BOT_TOKEN);

  return (
    <div className="flex flex-col min-h-[calc(100vh-40px)] overflow-y-auto scrollbar px-32 max-md:px-20 py-10">
      <Logo className="absolute top-14 left-8" />

      {!hideCloseButton && (
        <Image
          src={cancelImage}
          alt="cancel-button"
          className="absolute top-14 right-8 cursor-pointer hover:scale-105 transition-transform"
          width={60}
          onClick={() => router.push('/main')}
        />
      )}

      {/* Title */}
      <div className="flex-grow pt-8 font-extrabold flex flex-col gap-12">
        <div className="flex flex-col items-center gap-8">
          <span className="relative text-[#63411D] px-8 py-2 bg-[#F2B637] rounded-3xl border-[7px] border-[#9A5C1A] text-[26px]">
            <Image
              src={buttonCircleImage}
              alt="icon"
              width={21}
              height={14}
              className="absolute left-2"
            />
            Report
          </span>
          <div className="flex flex-col items-center gap-6">
            <p className="text-[#353535] text-5xl">AI 기반 집중력 분석 레포트</p>
            <p className="text-[#98816B] text-[26px] text-center">
              게임 결과 데이터를 바탕으로, 아이에게 필요한 집중력 개선 방안을 안내합니다.
            </p>
          </div>
        </div>

        {/* Summary */}
        <div className="flex items-center justify-between w-full h-52 bg-[#FFE3A7] rounded-[48px] border-[8px] border-[#DFB458] pl-20 pr-6 mb-10">
          <div className="max-lg:flex-col max-lg:gap-3">
            <div className="flex gap-3 text-[32px]">
              <p>이름</p>
              <p>{report.child.name}</p>
            </div>
            <div className="flex gap-5 text-[28px]">
              <div className="flex gap-3 max-lg:flex-col max-lg:gap-0">
                <p>나이</p>
                <p>{new Date().getFullYear() - report.child.birthYear}세</p>
              </div>
              <div className="flex gap-3 max-lg:flex-col max-lg:gap-0">
                <p>성별</p>
                <p>{report.child.gender === 'M' ? '남' : '여'}</p>
              </div>
            </div>
          </div>
          <div className="flex items-center justify-around w-3/5 h-36 bg-gradient-to-b from-[#FFF5E3] to-[#FFEED1] rounded-[34px] border-[10px] border-[#DFB458] p-2 max-lg:flex-col">
            <p className="text-4xl max-lg:text-2xl">아이의 집중력 지수</p>
            <p className="text-5xl max-lg:text-3xl">{report.concentrationScore}%</p>
          </div>
        </div>

        {/* 🧩 게임별 리포트 */}
        {report.gameReports.map((game: GameReport) => (
          <div
            key={game.id}
            className="relative w-full bg-[#EFB141] border-[6px] border-[#99622D] rounded-[40px] p-4 mt-10"
          >
            <div className="w-1/3 h-[88px] absolute bg-[#EEB041] border-[6px] border-[#99622D] rounded-[28px] p-2 -top-10 left-10 z-10">
              <div className="absolute bg-[#F9CC7E] w-8 h-[3px] rounded-full top-[2.5px] left-7"></div>
              <div className="flex items-center justify-center w-full h-full bg-[#9D5C15] border-[3px] border-[#90580A] rounded-[18px]">
                <p className="text-white text-[30px] text-center">{getReportName(game.gameCode)}</p>
              </div>
            </div>

            <div className="w-full h-full bg-gradient-to-b from-[#FFF5E3] to-[#FFEED1] rounded-3xl border-[5px] border-[#A66A2F] p-12 font-extrabold flex flex-col justify-around py-16">
              <div className="flex flex-col gap-4">
                <p className="text-[32px]">{getGameName(game.gameCode)}</p>
                <div className="flex flex-col gap-4 text-[26px]">
                  <div className="flex gap-10">
                    <p>최대 라운드 도달율: {game.maxRoundsRatio}%</p>
                    <p>평균 도달 라운드: {game.avgRoundsCount}라운드</p>
                  </div>

                  <div>
                    {game.gameCode === 'KIDS_TRAFFIC' ? (
                      <p>평균 반응 속도: {(game.totalReactionMsAvg / 1000).toFixed(2)}초</p>
                    ) : (
                      <p>오답률: {game.wrongRate}%</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex flex-col gap-4">
                <p className="text-[32px]">AI 기반 분석 및 조언</p>
                {game.advices.length === 0 && (
                  <p className="text-2xl text-gray-600">조언 데이터가 없습니다.</p>
                )}
                {game.advices.map((advice) => (
                  <div key={advice.id} className="flex flex-col text-2xl">
                    <p className="flex items-center">
                      <Dot size={50} />
                      {advice.title}
                    </p>
                    <div className="flex items-center gap-4 pl-4">
                      <Image src={arrowImage} alt="arrow" width={56} height={56} />
                      <p>{advice.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}

        {/* 📧 메일 공유 버튼 — BOT_TOKEN 모드에서는 숨김 */}
        {!hideShareButton && (
          <div className="flex justify-center">
            <SecondaryButton variant="mailShare" onClick={() => setShareClicked(true)}>
              메일로 공유하기
            </SecondaryButton>
          </div>
        )}
      </div>

      {/* 📧 메일 공유 모달 (BOT_TOKEN 모드에서는 숨김) */}
      {shareClicked && !hideShareButton && (
        <Modal
          type="step"
          isCloseBtn
          onClose={() => setShareClicked(false)}
          onCancel={() => setShareClicked(false)}
          onNext={handleSendEmail}
        >
          <div className="flex flex-col items-center gap-6 justify-center h-full py-4">
            <p className="font-malrang text-5xl text-center">
              아이의 집중력 분석 레포트를 메일로 받아보세요.
            </p>
            <div className="flex items-center gap-7 w-full px-5">
              <p
                className="h-[80px] flex items-center px-6 bg-modal-inner-input-border 
                text-4xl font-extrabold rounded-[20px] whitespace-nowrap"
              >
                E-MAIL
              </p>

              <Input
                variant="default"
                placeholder="abc@gmail.com"
                className="
                  h-[80px] 
                  w-full 
                  mx-auto 
                  !border-modal-inner-input-border 
                  !text-3xl 
                  !py-0 
                  !leading-[80px]
                "
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
        </Modal>
      )}

      {sendModalOpen && (
        <Modal type="confirm" isCloseBtn={false} onConfirm={() => setSendModalOpen(false)}>
          <div className="flex flex-col items-center justify-center h-full gap-5">
            <p className="font-malrang text-5xl text-center">메일로 전송이 완료되었습니다.</p>
            <p className="text-2xl font-extrabold text-modal-inner-text">
              최대 5분이 소요될 수 있습니다.
            </p>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Report;
