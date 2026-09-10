import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { User, Category } from '../../types';

interface AnalyticsFiltersProps {
  users?: User[];
  categories?: Category[];
  filters: {
    start_date?: string;
    end_date?: string;
    user_id?: string;
    department?: string;
    category_id?: string;
    priority?: string;
    status?: string;
    interval?: 'daily' | 'weekly' | 'monthly';
  };
  onChange: (filters: any) => void;
  onReset: () => void;
}

export const AnalyticsFilters: React.FC<AnalyticsFiltersProps> = ({
  users = [],
  categories = [],
  filters,
  onChange,
  onReset,
}) => {
  const handleChange = (key: string, value: string) => {
    onChange({ ...filters, [key]: value || undefined });
  };

  const departments = Array.from(new Set(users.map((u) => u.department).filter(Boolean))) as string[];

  return (
    <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-xs mb-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider">
          <Filter className="w-4 h-4 text-blue-600" />
          Analytics Filters
        </div>
        <button
          onClick={onReset}
          className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900 transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-3 text-xs">
        <div>
          <label className="block text-gray-500 mb-1">Start Date</label>
          <input
            type="date"
            value={filters.start_date || ''}
            onChange={(e) => handleChange('start_date', e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
          />
        </div>

        <div>
          <label className="block text-gray-500 mb-1">End Date</label>
          <input
            type="date"
            value={filters.end_date || ''}
            onChange={(e) => handleChange('end_date', e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
          />
        </div>

        <div>
          <label className="block text-gray-500 mb-1">User</label>
          <select
            value={filters.user_id || ''}
            onChange={(e) => handleChange('user_id', e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
          >
            <option value="">All Users</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-gray-500 mb-1">Department</label>
          <select
            value={filters.department || ''}
            onChange={(e) => handleChange('department', e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-gray-500 mb-1">Category</label>
          <select
            value={filters.category_id || ''}
            onChange={(e) => handleChange('category_id', e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-gray-500 mb-1">Trend Interval</label>
          <select
            value={filters.interval || 'daily'}
            onChange={(e) => handleChange('interval', e.target.value)}
            className="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
      </div>
    </div>
  );
};
