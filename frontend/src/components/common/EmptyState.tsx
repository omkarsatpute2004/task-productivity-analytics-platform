import React, { ReactNode } from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  description = 'There are no data records matching your current filter criteria.',
  icon,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-gray-100 my-4">
      <div className="p-3 bg-gray-50 rounded-full text-gray-400 mb-3">
        {icon || <Inbox className="w-8 h-8" />}
      </div>
      <h3 className="text-base font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-xs text-gray-500 max-w-sm mb-4">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
};
