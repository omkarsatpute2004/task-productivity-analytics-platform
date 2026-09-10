import React from 'react';
import { TaskPriority, TaskStatus } from '../../types';

interface PriorityBadgeProps {
  priority: TaskPriority;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority }) => {
  const styles: Record<TaskPriority, string> = {
    LOW: 'bg-slate-100 text-slate-700 border-slate-200',
    MEDIUM: 'bg-blue-50 text-blue-700 border-blue-200',
    HIGH: 'bg-amber-50 text-amber-800 border-amber-200',
    CRITICAL: 'bg-rose-50 text-rose-800 border-rose-200 font-semibold',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[priority]}`}>
      {priority}
    </span>
  );
};

interface StatusBadgeProps {
  status: TaskStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const styles: Record<TaskStatus, { label: string; class: string }> = {
    TODO: { label: 'To Do', class: 'bg-gray-100 text-gray-700 border-gray-200' },
    IN_PROGRESS: { label: 'In Progress', class: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
    COMPLETED: { label: 'Completed', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    CANCELLED: { label: 'Cancelled', class: 'bg-rose-50 text-rose-600 border-rose-200' },
  };

  const item = styles[status] || { label: status, class: 'bg-gray-100 text-gray-700' };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${item.class}`}>
      {item.label}
    </span>
  );
};

interface DeadlineBadgeProps {
  deadline?: string | null;
  status: TaskStatus;
  completedAt?: string | null;
}

export const DeadlineBadge: React.FC<DeadlineBadgeProps> = ({ deadline, status, completedAt }) => {
  if (!deadline) {
    return <span className="text-gray-400 text-xs">No deadline</span>;
  }

  const deadlineDate = new Date(deadline);
  const now = new Date();
  const formattedDate = deadlineDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });

  if (status === 'COMPLETED' && completedAt) {
    const completedDate = new Date(completedAt);
    if (completedDate > deadlineDate) {
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
          Completed Late ({formattedDate})
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
        Completed On-Time ({formattedDate})
      </span>
    );
  }

  if (status !== 'COMPLETED' && status !== 'CANCELLED' && now > deadlineDate) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
        OVERDUE ({formattedDate})
      </span>
    );
  }

  return <span className="text-xs text-gray-600">{formattedDate}</span>;
};
