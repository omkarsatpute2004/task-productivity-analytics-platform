import React from 'react';
import { Search, Filter, RotateCcw } from 'lucide-react';
import { User, Category, TaskStatus, TaskPriority } from '../../types';

interface TaskFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  status?: string;
  onStatusChange: (value: string) => void;
  priority?: string;
  onPriorityChange: (value: string) => void;
  categoryId?: string;
  onCategoryChange: (value: string) => void;
  userId?: string;
  onUserChange: (value: string) => void;
  users?: User[];
  categories?: Category[];
  isAdmin?: boolean;
  onReset: () => void;
}

export const TaskFilters: React.FC<TaskFiltersProps> = ({
  search,
  onSearchChange,
  status,
  onStatusChange,
  priority,
  onPriorityChange,
  categoryId,
  onCategoryChange,
  userId,
  onUserChange,
  users = [],
  categories = [],
  isAdmin,
  onReset,
}) => {
  return (
    <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-xs mb-6 space-y-3">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search input */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search task title or description..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-gray-50/50"
          />
        </div>

        <button
          onClick={onReset}
          className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-900 transition self-end sm:self-center"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Filters
        </button>
      </div>

      {/* Select Filters */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div>
          <label className="block text-[11px] text-gray-500 mb-1">Status</label>
          <select
            value={status || ''}
            onChange={(e) => onStatusChange(e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg bg-white"
          >
            <option value="">All Statuses</option>
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] text-gray-500 mb-1">Priority</label>
          <select
            value={priority || ''}
            onChange={(e) => onPriorityChange(e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg bg-white"
          >
            <option value="">All Priorities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] text-gray-500 mb-1">Category</label>
          <select
            value={categoryId || ''}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg bg-white"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        {isAdmin && (
          <div>
            <label className="block text-[11px] text-gray-500 mb-1">Assigned User</label>
            <select
              value={userId || ''}
              onChange={(e) => onUserChange(e.target.value)}
              className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg bg-white"
            >
              <option value="">All Users</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>
    </div>
  );
};
