import api from '@/lib/api/client';

export interface LogoutResponse {
  detail: string;
}

export const logout = async (): Promise<LogoutResponse> => {
  if (typeof window === 'undefined') {
    throw new Error('브라우저 환경이 아닙니다.');
  }

  const refreshToken = window.sessionStorage.getItem('refreshToken');
  if (!refreshToken) {
    throw new Error('Refresh token이 없습니다.');
  }

  // refresh token을 요청 본문에 포함
  const body = new URLSearchParams();
  body.append('refresh', refreshToken);

  const { data } = await api.post<LogoutResponse>('/users/logout/', body, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return data;
};
