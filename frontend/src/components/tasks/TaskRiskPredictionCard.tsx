import React, { useEffect, useState } from 'react';
import { Sparkles, AlertTriangle, CheckCircle, Clock, ShieldAlert, RefreshCw, Info } from 'lucide-react';
import { Task, OverduePredictionResponse, CompletionTimePredictionResponse } from '../../types';
import { mlApi } from '../../services/mlApi';
import { Spinner } from '../common/Spinner';

interface TaskRiskPredictionCardProps {
  task: Task;
}

export const TaskRiskPredictionCard: React.FC<TaskRiskPredictionCardProps> = ({ task }) => {
  const [overduePred, setOverduePred] = useState<OverduePredictionResponse | null>(null);
  const [completionPred, setCompletionPred] = useState<CompletionTimePredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPredictions = async () => {
    if (!task) return;
    setIsLoading(true);
    setError(null);

    try {
      const estimatedHours = task.estimated_hours ?? 0;
      
      const [overdueRes, completionRes] = await Promise.all([
        mlApi.predictOverdue({
          priority: task.priority,
          category_id: task.category_id,
          user_id: task.user_id,
          estimated_hours: estimatedHours,
          deadline: task.deadline || null
        }),
        mlApi.predictCompletionTime({
          priority: task.priority,
          category_id: task.category_id,
          user_id: task.user_id,
          estimated_hours: estimatedHours
        })
      ]);

      setOverduePred(overdueRes);
      setCompletionPred(completionRes);
    } catch (err: any) {
      console.error('Failed to fetch ML predictions:', err);
      setError(err?.response?.data?.detail || 'Failed to load predictive analytics for this task.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, [task.id, task.priority, task.category_id, task.user_id, task.estimated_hours, task.deadline]);

  const getRiskBadge = (level?: string) => {
    switch (level) {
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-bold rounded-full bg-rose-100 text-rose-800 border border-rose-300">
            <ShieldAlert className="w-3.5 h-3.5" />
            HIGH RISK
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-bold rounded-full bg-amber-100 text-amber-800 border border-amber-300">
            <AlertTriangle className="w-3.5 h-3.5" />
            MEDIUM RISK
          </span>
        );
      case 'LOW':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle className="w-3.5 h-3.5" />
            LOW RISK
          </span>
        );
    }
  };

  const getRiskBorder = (level?: string) => {
    switch (level) {
      case 'HIGH':
        return 'border-rose-200 bg-rose-50/40';
      case 'MEDIUM':
        return 'border-amber-200 bg-amber-50/40';
      case 'LOW':
      default:
        return 'border-emerald-200 bg-emerald-50/40';
    }
  };

  return (
    <div className={`p-6 rounded-xl border ${overduePred ? getRiskBorder(overduePred.risk_level) : 'border-purple-100 bg-purple-50/30'} shadow-xs space-y-4`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-200/80">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-purple-600 text-white rounded-lg shadow-xs">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              AI Task Predictive Intelligence
            </h3>
            <p className="text-[11px] text-gray-500">
              Machine Learning estimates based on historical task performance & workload attributes
            </p>
          </div>
        </div>

        <button
          onClick={fetchPredictions}
          disabled={isLoading}
          title="Recalculate predictions"
          className="p-1.5 text-gray-400 hover:text-purple-600 hover:bg-purple-100/50 rounded-lg transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Task Status Notice for Completed / Cancelled */}
      {task.status === 'COMPLETED' && (
        <div className="p-2.5 bg-emerald-100/70 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center gap-2 font-medium">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          Task is already completed. Predictive metrics reflect pre-completion risk evaluation.
        </div>
      )}

      {task.status === 'CANCELLED' && (
        <div className="p-2.5 bg-gray-100 border border-gray-200 rounded-lg text-xs text-gray-600 flex items-center gap-2 font-medium">
          <Info className="w-4 h-4 text-gray-500 shrink-0" />
          Task is cancelled. Predictions are archived for reference.
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-6 gap-2 text-xs text-purple-700 font-medium">
          <Spinner size="sm" />
          Calculating machine learning predictions...
        </div>
      )}

      {/* Error State */}
      {!isLoading && error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={fetchPredictions}
            className="text-xs font-semibold text-rose-800 underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Prediction Cards Content */}
      {!isLoading && !error && overduePred && completionPred && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Risk & Overdue Probability */}
            <div className="p-4 bg-white rounded-lg border border-gray-200/90 shadow-2xs space-y-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 block">
                Overdue Risk Status
              </span>
              <div className="flex items-center justify-between">
                <div>
                  {getRiskBadge(overduePred.risk_level)}
                </div>
                <div className="text-right">
                  <div className="text-xl font-black text-gray-900">
                    {(overduePred.late_probability * 100).toFixed(1)}%
                  </div>
                  <span className="text-[11px] font-medium text-gray-500">Late Probability</span>
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden mt-1">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    overduePred.risk_level === 'HIGH'
                      ? 'bg-rose-500'
                      : overduePred.risk_level === 'MEDIUM'
                      ? 'bg-amber-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(5, overduePred.late_probability * 100))}%` }}
                />
              </div>
            </div>

            {/* Completion Time Duration */}
            <div className="p-4 bg-white rounded-lg border border-gray-200/90 shadow-2xs space-y-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 block">
                Predicted Completion Time
              </span>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-full text-xs font-semibold border border-indigo-200">
                  <Clock className="w-3.5 h-3.5" />
                  Estimated Duration
                </div>
                <div className="text-right">
                  <div className="text-xl font-black text-gray-900">
                    {completionPred.predicted_completion_days.toFixed(1)} <span className="text-sm font-semibold text-gray-600">days</span>
                  </div>
                  <span className="text-[11px] font-medium text-gray-500">
                    (~{(completionPred.predicted_completion_days * 24).toFixed(0)} hrs execution)
                  </span>
                </div>
              </div>

              <div className="text-[11px] text-gray-500 pt-1">
                Compared to {task.estimated_hours ?? 0} estimated planned hours.
              </div>
            </div>
          </div>

          {/* Model Explanation Disclaimer Notice */}
          <div className="flex items-start gap-2 p-3 bg-purple-50/60 rounded-lg border border-purple-100 text-[11px] text-purple-900 leading-normal">
            <Info className="w-4 h-4 text-purple-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">Disclaimer: </span>
              {overduePred.explanation} Model-based prediction, not a guarantee. (Model: {overduePred.model_version})
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
