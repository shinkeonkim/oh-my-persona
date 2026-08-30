import { api } from '@/lib/api/client';

export interface StarGameStartResponse {
  // 게임 시작 응답
  sessionId: string;
  gameCode: string;
  startedAt: string; // ISO8601 UTC 형식
  status: 'STARTED' | 'IN_PROGRESS' | 'ENDED';
}

// 게임 종료 요청
export interface StarGameEndRequest {
  sessionId: string;
  score: number; // 총 점수
  wrongCount?: number; // 틀린 개수 (optional)
  reactionMsSum?: number; // 반응시간 총합 (ms)
  roundCount?: number; // 전체 라운드 수
  successCount?: number; // 성공한 라운드 수
  meta?: string; // meta (JSON 문자열 형태)
}

export interface StarGameEndResponse {
  sessionId: string;
  status: 'FINISHED' | 'SAVED' | 'ERROR';
  message?: string;
}

// 아기별 게임 시작 API
export const startStarGame = async (): Promise<StarGameStartResponse> => {
  const { data } = await api.post<StarGameStartResponse>('/games/bb-star/start/', {});
  return data;
};

// 아기별 게임 종료 API
export const endStarGame = async (payload: StarGameEndRequest): Promise<StarGameEndResponse> => {
  const body = {
    ...payload,
    meta: typeof payload.meta === 'object' ? JSON.stringify(payload.meta) : (payload.meta ?? '{}'),
  };

  console.log('📤 [endStarGame] request body:', body);

  const { data } = await api.post<StarGameEndResponse>('/games/bb-star/finish/', body);
  return data;
};
