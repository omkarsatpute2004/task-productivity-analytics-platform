import React, { useState, useEffect, useCallback } from 'react';
import {
  CheckSquare,
  CheckCircle2,
  Clock,
  AlertTriangle,
  BarChart3,
  TrendingUp,
  Award,
  Timer
} from 'lucide-react';
import { analyticsApi, AnalyticsQueryParams } from '../services/analyticsApi';
import { userApi } from '../services/userApi';
import { categoryApi } from '../services/categoryApi';
import {
  AnalyticsSummary,
  StatusDistribution,
  PriorityAnalytics,
  CategoryAnalytics,
  UserProductivity,
  CompletionTrend,
  OverdueAnalytics,
  EstimationAnalytics,
  User,
  Category
} from '../types';
import { KPICard } from '../components/analytics/KPICard';
import {
  StatusDistributionChart,
  PriorityChart,
  CompletionTrendChart,
  CategoryChart,
  UserProductivityTable,
  OverdueChart,
  EstimationChart
} from '../components/analytics/AnalyticsCharts';
import { AnalyticsFilters } from '../components/analytics/AnalyticsFilters';
import { Spinner, CardSkeleton } from '../components/common/Spinner';

export const Dashboard: React.FC = () => {
  const [filters, setFilters] = useState<AnalyticsQueryParams>({
    interval: 'monthly',
  });
  const [users, setUsers] = useState<User[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [statusDist, setStatusDist] = useState<StatusDistribution[]>([]);
  const [priorityData, setPriorityData] = useState<PriorityAnalytics[]>([]);
  const [categoryData, setCategoryData] = useState<CategoryAnalytics[]>([]);
  const [userData, setUserData] = useState<UserProductivity[]>([]);
  const [trendData, setTrendData] = useState<CompletionTrend[]>([]);
  const [overdueData, setOverdueData] = useState<OverdueAnalytics | null>(null);
  const [estimationData, setEstimationData] = useState<EstimationAnalytics | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  // Load dropdown lists once
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const [uRes, cRes] = await Promise.all([
          userApi.getUsers({ limit: 100 }),
          categoryApi.getCategories(),
        ]);
        setUsers(uRes.items);
        setCategories(cRes.items);
      } catch (err) {
        console.error('Failed to load filter metadata:', err);
      }
    };
    loadMetadata();
  }, []);

  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [
        sumRes,
        statusRes,
        prioRes,
        catRes,
        userRes,
        trendRes,
        overdueRes,
        estRes,
      ] = await Promise.all([
        analyticsApi.getSummary(filters),
        analyticsApi.getStatusDistribution(filters),
        analyticsApi.getPriorityAnalysis(filters),
        analyticsApi.getCategoryAnalysis(filters),
        analyticsApi.getUserProductivity(filters),
        analyticsApi.getCompletionTrend(filters),
        analyticsApi.getOverdueAnalysis(filters),
        analyticsApi.getEstimationAnalysis(filters),
      ]);

      setSummary(sumRes);
      setStatusDist(statusRes);
      setPriorityData(prioRes);
      setCategoryData(catRes);
      setUserData(userRes);
      setTrendData(trendRes);
      setOverdueData(overdueRes);
      setEstimationData(estRes);
    } catch (err) {
      console.error('Failed to fetch analytics dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">
            Productivity Analytics Dashboard
          </h2>
          <p className="text-xs text-gray-500">
            Real-time analytics engine metrics from PostgreSQL database
          </p>
        </div>
      </div>

      {/* Global Analytics Filters */}
      <AnalyticsFilters
        users={users}
        categories={categories}
        filters={filters as any}
        onChange={(newFilters) => setFilters(newFilters)}
        onReset={() => setFilters({ interval: 'monthly' })}
      />

      {/* Top 8 KPI Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : summary ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Total Tasks"
            value={summary.total_tasks}
            subtitle="System task volume"
            icon={<CheckSquare className="w-5 h-5" />}
            color="blue"
          />
          <KPICard
            title="Completed Tasks"
            value={summary.completed_tasks}
            subtitle={`${summary.completion_rate}% overall completion`}
            icon={<CheckCircle2 className="w-5 h-5" />}
            color="emerald"
          />
          <KPICard
            title="Pending Tasks"
            value={summary.pending_tasks}
            subtitle="To Do status count"
            icon={<Clock className="w-5 h-5" />}
            color="amber"
          />
          <KPICard
            title="Overdue Tasks"
            value={summary.overdue_tasks}
            subtitle="Incomplete & late completion"
            icon={<AlertTriangle className="w-5 h-5" />}
            color="rose"
          />
          <KPICard
            title="Completion Rate"
            value={`${summary.completion_rate}%`}
            subtitle="Completed / Total ratio"
            icon={<TrendingUp className="w-5 h-5" />}
            color="indigo"
          />
          <KPICard
            title="On-Time Rate"
            value={`${summary.on_time_completion_rate}%`}
            subtitle="Completed on or before deadline"
            icon={<Award className="w-5 h-5" />}
            color="emerald"
          />
          <KPICard
            title="Late Completion Rate"
            value={`${summary.late_completion_rate}%`}
            subtitle="Completed after deadline"
            icon={<Timer className="w-5 h-5" />}
            color="amber"
          />
          <KPICard
            title="Avg Completion Time"
            value={`${summary.average_completion_days} d`}
            subtitle={`Median: ${summary.median_completion_days} days`}
            icon={<BarChart3 className="w-5 h-5" />}
            color="purple"
          />
        </div>
      ) : null}

      {/* Charts Grid */}
      {isLoading ? (
        <div className="flex justify-center p-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Row 1: Status Distribution & Priority Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <StatusDistributionChart data={statusDist} />
            <PriorityChart data={priorityData} />
          </div>

          {/* Row 2: Completion Trend Time-Series */}
          <CompletionTrendChart data={trendData} />

          {/* Row 3: Category Analysis & Overdue Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CategoryChart data={categoryData} />
            {overdueData && <OverdueChart data={overdueData} />}
          </div>

          {/* Row 4: Estimated vs Actual Hours */}
          {estimationData && <EstimationChart data={estimationData} />}

          {/* Row 5: Neutral User Productivity Table */}
          <UserProductivityTable data={userData} />
        </div>
      )}
    </div>
  );
};
