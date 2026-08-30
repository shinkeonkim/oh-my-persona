import api from '@/lib/api/client';

export interface CheckUsernameResponse {
  exists: boolean;
}

export const checkUsername = async (username: string): Promise<CheckUsernameResponse> => {
  const { data } = await api.get<CheckUsernameResponse>('/users/check-username/', {
    params: { username },
  });

  return data;
};
