import api from '@/lib/api/client';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: string;
}

export const signin = async (payload: LoginRequest): Promise<LoginResponse> => {
  const body = new URLSearchParams();
  body.append('username', payload.username);
  body.append('password', payload.password);

  const { data } = await api.post<LoginResponse>('/users/login/', body, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  return data;
};
