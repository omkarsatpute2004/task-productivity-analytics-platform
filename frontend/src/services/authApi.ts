import { api } from './api';
import { User } from '../types';

export interface LoginRequest {
  username: string; // Used as email in form
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  department?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    // Post JSON matching backend LoginRequest (email, password)
    const response = await api.post<AuthResponse>('/auth/login', {
      email: credentials.username,
      password: credentials.password,
    });
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};
