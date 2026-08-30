import api from '../client';

export interface SetPasswordRequest {
  pin: string;
}

export interface SetPasswordResponse {
  isSuccess: boolean;
  message: string;
}

// 비밀번호 등록 API
export const setReportPin = async (data: SetPasswordRequest): Promise<SetPasswordResponse> => {
  const res = await api.post<SetPasswordResponse>('/reports/set-report-pin/', data);
  return res.data;
};
