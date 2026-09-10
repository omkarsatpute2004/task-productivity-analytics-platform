import React, { useState, useEffect, useCallback } from 'react';
import { analyticsApi, AnalyticsQueryParams } from '../services/analyticsApi';
import { mlApi } from '../services/mlApi';
import { userApi } from '../services/userApi';
import { categoryApi } from '../services/categoryApi';
import {
  AnalyticsSummary,
  CategoryAnalytics,
  UserProductivity,
  EstimationAnalytics,
  FeatureImportanceResponse,
  User,
  Category
} from '../types';
import { AnalyticsFilters } from '../components/analytics/AnalyticsFilters';
import { KPICard } from '../components/analytics/KPICard';
import { UserProductivityTable, CategoryChart, EstimationChart } from '../components/analytics/AnalyticsCharts';
import { Spinner, CardSkeleton } from '../components/common/Spinner';
import { Calculator, Activity, AlertCircle, Sparkles, Brain } from 'lucide-react';


export const Analytics: React.FC = () => {
  const [filters, setFilters] = useState<AnalyticsQueryParams>({
    interval: 'monthly',
  });
  const [users, setUsers] = useState<User[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [categoryData, setCategoryData] = useState<CategoryAnalytics[]>([]);
  const [userData, setUserData] = useState<UserProductivity[]>([]);
  const [estimationData, setEstimationData] = useState<EstimationAnalytics | null>(null);
  const [featureImportance, setFeatureImportance] = useState<FeatureImportanceResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const [uRes, cRes, featRes] = await Promise.all([
          userApi.getUsers({ limit: 100 }),
          categoryApi.getCategories(),
          mlApi.getFeatureImportance().catch(() => null),
        ]);
        setUsers(uRes.items);
        setCategories(cRes.items);
        if (featRes) setFeatureImportance(featRes);
      } catch (err) {
        console.error('Failed to load filter metadata:', err);
      }
    };
    loadMetadata();
  }, []);


  const fetchAnalytics = useCallback(async () => {
    setIsLoading(true);
    try {
      const [sumRes, catRes, userRes, estRes] = await Promise.all([
        analyticsApi.getSummary(filters),
        analyticsApi.getCategoryAnalysis(filters),
        analyticsApi.getUserProductivity(filters),
        analyticsApi.getEstimationAnalysis(filters),
      ]);
      setSummary(sumRes);
      setCategoryData(catRes);
      setUserData(userRes);
      setEstimationData(estRes);
    } catch (err) {
      console.error('Failed to fetch analytics metrics:', err);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const stats = estimationData?.statistics;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">Dedicated Analytics & Insights</h2>
        <p className="text-xs text-gray-500">
          Statistical calculations, percentiles, Pearson correlations, and IQR outlier analysis
        </p>
      </div>

      <AnalyticsFilters
        users={users}
        categories={categories}
        filters={filters as any}
        onChange={(newFilters) => setFilters(newFilters)}
        onReset={() => setFilters({ interval: 'monthly' })}
      />

      {isLoading ? (
        <div className="flex justify-center p-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top Summary */}
          {summary && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <KPICard title="Total System Tasks" value={summary.total_tasks} color="blue" />
              <KPICard title="Completion Rate" value={`${summary.completion_rate}%`} color="emerald" />
              <KPICard title="On-Time Completion Rate" value={`${summary.on_time_completion_rate}%`} color="indigo" />
              <KPICard title="Avg Completion Time" value={`${summary.average_completion_days} d`} color="purple" />
            </div>
          )}

          {/* Statistical Metrics Section */}
          {stats && (
            <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-xs space-y-4">
              <div className="flex items-center gap-2 border-b border-gray-100 pb-3 text-sm font-semibold text-gray-900">
                <Calculator className="w-4 h-4 text-indigo-600" />
                Descriptive Statistics & Percentiles (P25 - P90)
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                {/* Estimated Hours Stats */}
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-100 space-y-2">
                  <span className="font-semibold text-gray-900 block border-b pb-1">Estimated Hours Stats</span>
                  <div className="flex justify-between"><span>Mean:</span> <span className="font-semibold">{stats.estimated_hours.mean} hrs</span></div>
                  <div className="flex justify-between"><span>Median (P50):</span> <span className="font-semibold">{stats.estimated_hours.median} hrs</span></div>
                  <div className="flex justify-between"><span>Std Dev:</span> <span className="font-semibold">{stats.estimated_hours.std}</span></div>
                  <div className="flex justify-between"><span>P25 - P75 (IQR):</span> <span className="font-semibold">{stats.estimated_hours.p25} - {stats.estimated_hours.p75}</span></div>
                  <div className="flex justify-between"><span>P90 Percentile:</span> <span className="font-semibold">{stats.estimated_hours.p90} hrs</span></div>
                </div>

                {/* Actual Hours Stats */}
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-100 space-y-2">
                  <span className="font-semibold text-gray-900 block border-b pb-1">Actual Hours Stats</span>
                  <div className="flex justify-between"><span>Mean:</span> <span className="font-semibold">{stats.actual_hours.mean} hrs</span></div>
                  <div className="flex justify-between"><span>Median (P50):</span> <span className="font-semibold">{stats.actual_hours.median} hrs</span></div>
                  <div className="flex justify-between"><span>Std Dev:</span> <span className="font-semibold">{stats.actual_hours.std}</span></div>
                  <div className="flex justify-between"><span>P25 - P75 (IQR):</span> <span className="font-semibold">{stats.actual_hours.p25} - {stats.actual_hours.p75}</span></div>
                  <div className="flex justify-between"><span>P90 Percentile:</span> <span className="font-semibold">{stats.actual_hours.p90} hrs</span></div>
                </div>

                {/* Estimation Error & Pearson Correlations */}
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-100 space-y-2">
                  <span className="font-semibold text-gray-900 block border-b pb-1">Correlations & Outliers</span>
                  <div className="flex justify-between">
                    <span>Est vs Act Correlation:</span>
                    <span className="font-semibold text-blue-700">
                      {stats.correlations.estimated_vs_actual_hours ?? 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Est Hours Outliers (IQR):</span>
                    <span className="font-semibold text-amber-700">
                      {stats.outliers.estimated_hours.outlier_count} detected
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Act Hours Outliers (IQR):</span>
                    <span className="font-semibold text-amber-700">
                      {stats.outliers.actual_hours.outlier_count} detected
                    </span>
                  </div>
                  <div className="flex justify-between pt-1 border-t">
                    <span>Avg Error %:</span>
                    <span className="font-semibold text-emerald-700">
                      {estimationData.average_estimation_error_percentage}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Machine Learning Feature Importance Section */}
          {featureImportance && (
            <div className="bg-white p-6 rounded-xl border border-purple-100 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-purple-100 pb-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-gray-900">
                  <div className="p-1 bg-purple-600 text-white rounded-md">
                    <Brain className="w-4 h-4" />
                  </div>
                  Factors Used by the Machine Learning Models (Feature Importance)
                </div>
                <span className="text-[11px] font-medium text-purple-700 bg-purple-50 px-2.5 py-0.5 rounded-full border border-purple-200">
                  scikit-learn RandomForest
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                {/* Overdue Classification Factors */}
                <div className="space-y-3 p-4 bg-purple-50/40 rounded-lg border border-purple-100">
                  <span className="font-bold text-purple-950 block">
                    Overdue Risk Classifier Key Factors
                  </span>
                  <div className="space-y-2">
                    {featureImportance.classification_importance.map((item) => (
                      <div key={item.feature} className="space-y-1">
                        <div className="flex justify-between font-medium text-gray-700">
                          <span className="capitalize">{item.feature.replace(/_/g, ' ')}</span>
                          <span className="font-semibold text-purple-900">{(item.importance * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-purple-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-purple-600 h-1.5 rounded-full"
                            style={{ width: `${Math.max(3, item.importance * 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Completion Duration Regression Factors */}
                <div className="space-y-3 p-4 bg-indigo-50/40 rounded-lg border border-indigo-100">
                  <span className="font-bold text-indigo-950 block">
                    Completion Duration Regressor Key Factors
                  </span>
                  <div className="space-y-2">
                    {featureImportance.regression_importance.map((item) => (
                      <div key={item.feature} className="space-y-1">
                        <div className="flex justify-between font-medium text-gray-700">
                          <span className="capitalize">{item.feature.replace(/_/g, ' ')}</span>
                          <span className="font-semibold text-indigo-900">{(item.importance * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-indigo-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-indigo-600 h-1.5 rounded-full"
                            style={{ width: `${Math.max(3, item.importance * 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}


          {/* Charts & Supporting Tables */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CategoryChart data={categoryData} />
            {estimationData && <EstimationChart data={estimationData} />}
          </div>

          <UserProductivityTable data={userData} />
        </div>
      )}
    </div>
  );
};
