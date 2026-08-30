// src/lib/api/report/reportApi.ts
import { api } from '@/lib/api/client';

// 🧩 아이 정보
export interface ChildInfo {
  id: number;
  name: string;
  birthYear: number;
  gender: 'M' | 'F';
}

// 🧩 조언
export interface Advice {
  id: number;
  title: string;
  description: string;
  createdAt: string;
}

// 🧩 게임 리포트
export interface GameReport {
  id: number;
  gameName: string;
  gameCode: string;
  lastReflectedSessionId: string;
  isUpToDate: boolean;
  totalPlaysCount: number;
  totalPlayRoundsCount: number;
  maxRoundsCount: number;
  totalReactionMsSum: number;
  totalPlayActionsCount: number;
  totalSuccessCount: number;
  totalWrongCount: number;
  totalReactionMsAvg: number;
  wrongRate: number;
  avgRoundsCount: number;
  maxRoundsRatio: number;
  advices: Advice[];
  createdAt: string;
  updatedAt: string;
}

// 🧩 리포트 상세 응답
export interface ReportDetailResponse {
  id: number;
  child: ChildInfo;
  concentrationScore: number;
  gameReports: GameReport[];
  createdAt: string;
  updatedAt: string;
}

export const getReportDetail = async (
  pin?: string | null,
  botToken?: string | null
): Promise<ReportDetailResponse> => {
  const headers = botToken ? { 'X-BOT-TOKEN': botToken } : {};

  const body = pin ? { pin } : {};

  const { data } = await api.post('/reports/', body, { headers });

  return data;
};

export interface ReportStatusResponse {
  status: 'generating' | 'completed' | 'error' | 'no_games_played';
  reportId?: number;
  message?: string;
}

export const getReportStatus = async (): Promise<ReportStatusResponse> => {
  const { data } = await api.post('/reports/status/');
  return data;
};

export const pollReportStatus = async (
  intervalMs = 3000,
  maxAttempts = 20
): Promise<ReportStatusResponse> => {
  let attempt = 0;

  while (attempt < maxAttempts) {
    attempt++;

    const data = await getReportStatus();

    // 완료 or 에러 or 플레이 안 함 → 즉시 종료
    if (
      data.status === 'completed' ||
      data.status === 'error' ||
      data.status === 'no_games_played'
    ) {
      return data;
    }

    // generating이면 계속 기다리기 (폴링 지속)
    if (data.status === 'generating') {
      console.log(`⏳ 폴링 중... (${attempt})`);
      await new Promise((res) => setTimeout(res, intervalMs));
      continue;
    }

    await new Promise((res) => setTimeout(res, intervalMs));
  }

  throw new Error('리포트 생성 상태 확인 시간 초과');
};

export const sendReportEmail = async (email: string): Promise<void> => {
  await api.post('/reports/email/', { email });
};
