import { api } from './api';
import {
  OverduePredictionRequest,
  OverduePredictionResponse,
  CompletionTimePredictionRequest,
  CompletionTimePredictionResponse,
  ModelInfoResponse,
  FeatureImportanceResponse
} from '../types';

export const mlApi = {
  predictOverdue: async (data: OverduePredictionRequest): Promise<OverduePredictionResponse> => {
    const response = await api.post<OverduePredictionResponse>('/ml/predict-overdue', data);
    return response.data;
  },

  predictCompletionTime: async (data: CompletionTimePredictionRequest): Promise<CompletionTimePredictionResponse> => {
    const response = await api.post<CompletionTimePredictionResponse>('/ml/predict-completion-time', data);
    return response.data;
  },

  getModelInfo: async (): Promise<ModelInfoResponse> => {
    const response = await api.get<ModelInfoResponse>('/ml/model-info');
    return response.data;
  },

  getFeatureImportance: async (): Promise<FeatureImportanceResponse> => {
    const response = await api.get<FeatureImportanceResponse>('/ml/feature-importance');
    return response.data;
  },

  checkHealth: async (): Promise<{ status: string; models_loaded: boolean }> => {
    const response = await api.get<{ status: string; models_loaded: boolean }>('/ml/health');
    return response.data;
  }
};
