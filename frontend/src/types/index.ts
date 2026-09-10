export type UserRole = 'ADMIN' | 'USER';

export interface User {
  id: number;
  name: string;
  email: string;
  department?: string | null;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  user_id: number;
  user_name?: string;
  user?: User;
  category_id: number;
  category_name?: string;
  category?: Category;
  priority: TaskPriority;
  status: TaskStatus;
  deadline?: string | null;
  completed_at?: string | null;
  estimated_hours?: number | null;
  actual_hours?: number | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  user_id: number;
  category_id: number;
  priority: TaskPriority;
  status?: TaskStatus;
  deadline?: string;
  estimated_hours?: number;
  actual_hours?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  user_id?: number;
  category_id?: number;
  priority?: TaskPriority;
  status?: TaskStatus;
  deadline?: string;
  estimated_hours?: number;
  actual_hours?: number;
}

export interface TaskStatusUpdate {
  status: TaskStatus;
}

export interface TaskActivity {
  id: number;
  task_id: number;
  user_id: number;
  user_name?: string;
  activity_type: string;
  old_value?: string | null;
  new_value?: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Analytics Types
export interface AnalyticsSummary {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  in_progress_tasks: number;
  cancelled_tasks: number;
  overdue_tasks: number;
  completion_rate: number;
  on_time_completion_rate: number;
  late_completion_rate: number;
  average_completion_days: number;
  median_completion_days: number;
}

export interface StatusDistribution {
  status: TaskStatus;
  count: number;
  percentage: number;
}

export interface PriorityAnalytics {
  priority: TaskPriority;
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  completion_rate: number;
  late_completion_rate: number;
  average_completion_days: number;
  average_estimated_hours: number;
  average_actual_hours: number;
}

export interface CategoryAnalytics {
  category_id: number;
  category_name: string;
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  late_tasks: number;
  completion_rate: number;
  late_completion_rate: number;
  average_completion_days: number;
  total_estimated_hours: number;
  total_actual_hours: number;
}

export interface UserProductivity {
  user_id: number;
  user_name: string;
  department?: string | null;
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  in_progress_tasks: number;
  overdue_tasks: number;
  completion_rate: number;
  on_time_completion_rate: number;
  late_completion_rate: number;
  average_completion_days: number;
  total_estimated_hours: number;
  total_actual_hours: number;
}

export interface DepartmentAnalytics {
  department: string;
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  overdue_tasks: number;
  average_completion_days: number;
  total_estimated_hours: number;
  total_actual_hours: number;
}

export interface CompletionTrend {
  period: string;
  tasks_created: number;
  tasks_completed: number;
  tasks_overdue: number;
  completion_rate: number;
}

export interface OverdueAnalytics {
  total_overdue: number;
  incomplete_overdue: number;
  completed_late: number;
  overdue_by_priority: { priority: TaskPriority; count: number }[];
  overdue_by_category: { category_name: string; count: number }[];
}

export interface WorkloadAnalytics {
  user_id: number;
  user_name: string;
  total_assigned_tasks: number;
  open_tasks: number;
  high_priority_open_tasks: number;
  critical_priority_open_tasks: number;
  overdue_open_tasks: number;
  completion_rate: number;
}

export interface DescriptiveStats {
  count: number;
  mean: number;
  median: number;
  std: number;
  min: number;
  max: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
}

export interface EstimationAnalytics {
  total_estimated_hours: number;
  total_actual_hours: number;
  average_estimated_hours: number;
  average_actual_hours: number;
  total_estimation_error: number;
  average_estimation_error: number;
  average_estimation_error_percentage: number;
  underestimated_tasks_count: number;
  overestimated_tasks_count: number;
  statistics?: {
    estimated_hours: DescriptiveStats;
    actual_hours: DescriptiveStats;
    estimation_error: DescriptiveStats;
    correlations: Record<string, number | null>;
    outliers: {
      estimated_hours: { outlier_count: number; outliers: number[] };
      actual_hours: { outlier_count: number; outliers: number[] };
    };
  };
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Machine Learning Types
export interface OverduePredictionRequest {
  priority: TaskPriority;
  category_id: number;
  user_id: number;
  estimated_hours: number;
  deadline?: string | null;
}

export interface OverduePredictionResponse {
  late_probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  model_version: string;
  explanation: string;
}

export interface CompletionTimePredictionRequest {
  priority: TaskPriority;
  category_id: number;
  user_id: number;
  estimated_hours: number;
}

export interface CompletionTimePredictionResponse {
  predicted_completion_days: number;
  model_version: string;
  explanation: string;
}

export interface ModelInfoResponse {
  classification_model: Record<string, any>;
  regression_model: Record<string, any>;
  dataset_summary: Record<string, any>;
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
}

export interface FeatureImportanceResponse {
  classification_importance: FeatureImportanceItem[];
  regression_importance: FeatureImportanceItem[];
}

