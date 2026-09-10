import React from 'react';
import { History, CheckCircle2, Clock, FileEdit, PlusCircle } from 'lucide-react';
import { TaskActivity } from '../../types';

interface TaskActivityTimelineProps {
  activities: TaskActivity[];
}

export const TaskActivityTimeline: React.FC<TaskActivityTimelineProps> = ({ activities }) => {
  if (!activities || activities.length === 0) {
    return (
      <div className="p-6 bg-white rounded-xl border border-gray-100 text-center text-xs text-gray-500">
        No activity records logged for this task yet.
      </div>
    );
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'TASK_CREATED':
        return <PlusCircle className="w-4 h-4 text-blue-600" />;
      case 'STATUS_CHANGED':
      case 'TASK_COMPLETED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
      case 'TASK_UPDATED':
        return <FileEdit className="w-4 h-4 text-indigo-600" />;
      default:
        return <History className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-xs">
      <div className="flex items-center gap-2 mb-6 text-sm font-semibold text-gray-900 border-b border-gray-100 pb-3">
        <History className="w-4 h-4 text-blue-600" />
        Activity Timeline & Audit History
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200">
        {activities.map((act) => (
          <div key={act.id} className="relative flex items-start gap-4">
            <div className="absolute -left-6 top-0.5 p-1 bg-white border border-gray-200 rounded-full shadow-xs">
              {getActivityIcon(act.activity_type)}
            </div>

            <div className="flex-1 bg-gray-50/70 p-3 rounded-lg border border-gray-100 text-xs">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-semibold text-gray-900">
                  {act.user_name || `User #${act.user_id}`}
                </span>
                <span className="text-[11px] text-gray-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(act.created_at).toLocaleString()}
                </span>
              </div>

              <p className="text-gray-700">
                Action: <span className="font-medium text-blue-700">{act.activity_type}</span>
              </p>

              {(act.old_value || act.new_value) && (
                <div className="mt-2 pt-2 border-t border-gray-200/60 flex items-center gap-2 text-[11px] text-gray-600">
                  {act.old_value && (
                    <span className="line-through text-gray-400">
                      {act.old_value}
                    </span>
                  )}
                  {act.old_value && act.new_value && (
                    <span className="text-gray-400">→</span>
                  )}
                  {act.new_value && (
                    <span className="font-semibold text-emerald-700">
                      {act.new_value}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
