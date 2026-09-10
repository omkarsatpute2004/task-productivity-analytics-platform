import { api } from './api';
import {
  AnalyticsSummary,
  StatusDistribution,
  PriorityAnalytics,
  CategoryAnalytics,
  UserProductivity,
  DepartmentAnalytics,
  CompletionTrend,
  OverdueAnalytics,
  WorkloadAnalytics,
  EstimationAnalytics
} from '../types';

export interface AnalyticsQueryParams {
  start_date?: string;
  end_date?: string;
  user_id?: number;
  department?: string;
  category_id?: number;
  interval?: 'daily' | 'weekly' | 'monthly';
}

export const analyticsApi = {
  getSummary: async (params?: AnalyticsQueryParams): Promise<AnalyticsSummary> => {
    const response = await api.get<AnalyticsSummary>('/analytics/summary', { params });
    return response.data;
  },

  getStatusDistribution: async (params?: AnalyticsQueryParams): Promise<StatusDistribution[]> => {
    const response = await api.get<StatusDistribution[]>('/analytics/status-distribution', { params });
    return response.data;
  },

  getPriorityAnalysis: async (params?: AnalyticsQueryParams): Promise<PriorityAnalytics[]> => {
    const response = await api.get<PriorityAnalytics[]>('/analytics/priority', { params });
    return response.data;
  },

  getCategoryAnalysis: async (params?: AnalyticsQueryParams): Promise<CategoryAnalytics[]> => {
    const response = await api.get<CategoryAnalytics[]>('/analytics/categories', { params });
    return response.data;
  },

  getUserProductivity: async (params?: AnalyticsQueryParams): Promise<UserProductivity[]> => {
    const response = await api.get<UserProductivity[]>('/analytics/users', { params });
    return response.data;
  },

  getDepartmentAnalysis: async (): Promise<DepartmentAnalytics[]> => {
    const response = await api.get<DepartmentAnalytics[]>('/analytics/departments');
    return response.data;
  },

  getCompletionTrend: async (params?: AnalyticsQueryParams): Promise<CompletionTrend[]> => {
    const response = await api.get<CompletionTrend[]>('/analytics/completion-trend', { params });
    return response.data;
  },

  getOverdueAnalysis: async (params?: AnalyticsQueryParams): Promise<OverdueAnalytics> => {
    const response = await api.get<OverdueAnalytics>('/analytics/overdue', { params });
    return response.data;
  },

  getWorkloadAnalysis: async (params?: AnalyticsQueryParams): Promise<WorkloadAnalytics[]> => {
    const response = await api.get<WorkloadAnalytics[]>('/analytics/workload', { params });
    return response.data;
  },

  getEstimationAnalysis: async (params?: AnalyticsQueryParams): Promise<EstimationAnalytics> => {
    const response = await api.get<EstimationAnalytics>('/analytics/estimation', { params });
    return response.data;
  },
};
