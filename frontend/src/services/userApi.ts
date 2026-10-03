import { api } from './api';
import { User, PaginatedResponse } from '../types';

export interface UserQueryParams {
  search?: string;
  department?: string;
  role?: string;
  page?: number;
  limit?: number;
}

export interface UserUpdatePayload {
  name?: string;
  email?: string;
  department?: string;
  password?: string;
}

export const userApi = {
  getUsers: async (params?: UserQueryParams): Promise<PaginatedResponse<User>> => {
    const response = await api.get<PaginatedResponse<User>>('/users', { params });
    return response.data;
  },

  getAssignableUsers: async (params?: UserQueryParams): Promise<PaginatedResponse<User>> => {
    const response = await api.get<PaginatedResponse<User>>('/users/assignable', { params });
    return response.data;
  },

  getUser: async (id: number): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  updateUser: async (id: number, data: UserUpdatePayload): Promise<User> => {
    const response = await api.put<User>(`/users/${id}`, data);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`);
  },
};
