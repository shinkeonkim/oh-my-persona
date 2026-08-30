import api from '@/lib/api/client';

export interface TrafficGameStartResponse {
  sessionId: string;
  gameCode: string;
  startedAt: string;
  status: string;
}

export interface TrafficGameFinishRequest {
  sessionId: string;
  score: number;
  wrongCount?: number;
  reactionMsSum?: number;
  roundCount?: number;
  successCount?: number;
  meta?: Record<string, unknown>;
}

export interface TrafficGameFinishResponse {
  sessionId: string;
  gameCode: string;
  score: number;
  wrongCount: number;
  reactionMsSum?: number;
  roundCount: number;
  successCount: number;
  meta?: Record<string, unknown>;
}

export const startTrafficGame = async (): Promise<TrafficGameStartResponse> => {
  const { data } = await api.post<TrafficGameStartResponse>('/games/kids-traffic/start/');

  return data;
};

export const finishTrafficGame = async (
  payload: TrafficGameFinishRequest
): Promise<TrafficGameFinishResponse> => {
  const body = new URLSearchParams();
  body.append('sessionId', payload.sessionId);
  body.append('score', String(payload.score));

  if (typeof payload.wrongCount === 'number') {
    body.append('wrongCount', String(payload.wrongCount));
  }

  if (typeof payload.reactionMsSum === 'number') {
    body.append('reactionMsSum', String(payload.reactionMsSum));
  }

  if (typeof payload.roundCount === 'number') {
    body.append('roundCount', String(payload.roundCount));
  }

  if (typeof payload.successCount === 'number') {
    body.append('successCount', String(payload.successCount));
  }

  if (payload.meta) {
    body.append('meta', JSON.stringify(payload.meta));
  }

  const { data } = await api.post<TrafficGameFinishResponse>('/games/kids-traffic/finish/', body, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  return data;
};
