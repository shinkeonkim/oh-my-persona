import api from '../client';

export interface CreateChildRequest {
  name: string;
  birthYear: number;
  gender: 'M' | 'F'; // M: 남자, F: 여자
}

export interface CreateChildResponse {
  id: number;
  name: string;
  birthYear: number;
  gender: 'M' | 'F';
}

// 자녀 등록 API
export const createChildUser = async (data: CreateChildRequest): Promise<CreateChildResponse> => {
  const res = await api.post<CreateChildResponse>('/users/child/', data);
  return res.data;
};

// 자녀 확인 API
export const checkChildUser = async (): Promise<CreateChildResponse> => {
  const res = await api.get<CreateChildResponse>('/users/child/');
  return res.data;
};
