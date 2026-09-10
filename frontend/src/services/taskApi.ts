import { api } from './api';
import { Task, TaskCreate, TaskUpdate, TaskStatusUpdate, TaskActivity, PaginatedResponse } from '../types';

export interface TaskQueryParams {
  search?: string;
  status?: string;
  priority?: string;
  category_id?: number;
  user_id?: number;
  start_date?: string;
  end_date?: string;
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export const taskApi = {
  getTasks: async (params?: TaskQueryParams): Promise<PaginatedResponse<Task>> => {
    const response = await api.get<PaginatedResponse<Task>>('/tasks', { params });
    return response.data;
  },

  getTask: async (id: number): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  createTask: async (data: TaskCreate): Promise<Task> => {
    const response = await api.post<Task>('/tasks', data);
    return response.data;
  },

  updateTask: async (id: number, data: TaskUpdate): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${id}`, data);
    return response.data;
  },

  deleteTask: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  updateTaskStatus: async (id: number, data: TaskStatusUpdate): Promise<Task> => {
    const response = await api.patch<Task>(`/tasks/${id}/status`, data);
    return response.data;
  },

  getTaskActivity: async (id: number): Promise<TaskActivity[]> => {
    const response = await api.get<TaskActivity[]>(`/tasks/${id}/activity`);
    return response.data;
  },
};
