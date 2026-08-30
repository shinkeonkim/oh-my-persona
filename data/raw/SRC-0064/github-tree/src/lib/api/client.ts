import axios, { AxiosInstance } from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!baseURL) {
  console.error('NEXT_PUBLIC_API_BASE_URL 환경 변수가 설정되지 않았습니다.');
}

export const api: AxiosInstance = axios.create({
  baseURL: `${baseURL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// 토큰 자동 포함 (인증이 필요 없는 엔드포인트 제외)
api.interceptors.request.use(
  (config) => {
    // 로그인/회원가입/아이디 중복 확인 엔드포인트는 토큰이 필요 없음
    const url = config.url ?? '';
    const isAuthEndpoint =
      url.includes('/login/') || url.includes('/registration/') || url.includes('/check-username/');

    if (typeof window !== 'undefined' && !isAuthEndpoint) {
      const token = window.sessionStorage.getItem('accessToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
