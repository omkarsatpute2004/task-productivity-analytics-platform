import { api } from './api';
import { Category, PaginatedResponse } from '../types';

export interface CategoryCreatePayload {
  name: string;
  description?: string;
}

export interface CategoryUpdatePayload {
  name?: string;
  description?: string;
}

export const categoryApi = {
  getCategories: async (search?: string): Promise<PaginatedResponse<Category>> => {
    const response = await api.get<Category[]>('/categories');
    let items = response.data;
    if (search) {
      items = items.filter(
        (c) =>
          c.name.toLowerCase().includes(search.toLowerCase()) ||
          (c.description && c.description.toLowerCase().includes(search.toLowerCase()))
      );
    }
    return {
      items,
      total: items.length,
      page: 1,
      limit: 100,
      pages: 1,
    };
  },

  getCategory: async (id: number): Promise<Category> => {
    const response = await api.get<Category>(`/categories/${id}`);
    return response.data;
  },

  createCategory: async (data: CategoryCreatePayload): Promise<Category> => {
    const response = await api.post<Category>('/categories', data);
    return response.data;
  },

  updateCategory: async (id: number, data: CategoryUpdatePayload): Promise<Category> => {
    const response = await api.put<Category>(`/categories/${id}`, data);
    return response.data;
  },

  deleteCategory: async (id: number): Promise<void> => {
    await api.delete(`/categories/${id}`);
  },
};
