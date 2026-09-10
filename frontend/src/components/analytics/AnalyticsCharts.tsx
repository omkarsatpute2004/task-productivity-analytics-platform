import React from 'react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line, AreaChart, Area
} from 'recharts';
import {
  StatusDistribution,
  PriorityAnalytics,
  CategoryAnalytics,
  UserProductivity,
  CompletionTrend,
  OverdueAnalytics,
  EstimationAnalytics
} from '../../types';

const STATUS_COLORS: Record<string, string> = {
  TODO: '#64748b',
  IN_PROGRESS: '#6366f1',
  COMPLETED: '#10b981',
  CANCELLED: '#f43f5e',
};

const PRIORITY_COLORS: Record<string, string> = {
  LOW: '#94a3b8',
  MEDIUM: '#3b82f6',
  HIGH: '#f59e0b',
  CRITICAL: '#ef4444',
};

export const StatusDistributionChart: React.FC<{ data: StatusDistribution[] }> = ({ data }) => {
  const chartData = data.map((d) => ({
    name: d.status,
    value: d.count,
    percentage: d.percentage,
  }));

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-xs">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Task Status Distribution</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={85}
              paddingAngle={4}
              dataKey="value"
            >
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || '#3b82f6'} />
              ))}
            </Pie>
            <Tooltip
              formatter={(val: number, name: string, item: any) => [
                `${val} tasks (${item.payload.percentage}%)`,
                name,
              ]}
            />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const PriorityChart: React.FC<{ data: PriorityAnalytics[] }> = ({ data }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-xs">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Priority Breakdown & Completion Rates</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="priority" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} unit="%" />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="total_tasks" name="Total Tasks" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar yAxisId="left" dataKey="completed_tasks" name="Completed Tasks" fill="#10b981" radius={[4, 4, 0, 0]} />
            <Bar yAxisId="right" dataKey="completion_rate" name="Completion Rate (%)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const CompletionTrendChart: React.FC<{ data: CompletionTrend[] }> = ({ data }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-xs">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Creation & Completion Trend Over Time</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="period" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="tasks_created" name="Tasks Created" stroke="#3b82f6" fill="#eff6ff" strokeWidth={2} />
            <Area type="monotone" dataKey="tasks_completed" name="Tasks Completed" stroke="#10b981" fill="#ecfdf5" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const CategoryChart: React.FC<{ data: CategoryAnalytics[] }> = ({ data }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-xs">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Category Volume & Hours Analysis</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 10, right: 20, left: 60, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
            <XAxis type="number" tick={{ fontSize: 12 }} />
            <YAxis dataKey="category_name" type="category" tick={{ fontSize: 11 }} width={80} />
            <Tooltip />
            <Legend />
            <Bar dataKey="total_tasks" name="Total Tasks" fill="#0284c7" radius={[0, 4, 4, 0]} />
            <Bar dataKey="completed_tasks" name="Completed Tasks" fill="#059669" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const UserProductivityTable: React.FC<{ data: UserProductivity[] }> = ({ data }) => {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900">User Productivity Metrics (Neutral Measures)</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider font-semibold border-b border-gray-100">
            <tr>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3 text-right">Total Tasks</th>
              <th className="px-4 py-3 text-right">Completed</th>
              <th className="px-4 py-3 text-right">Overdue</th>
              <th className="px-4 py-3 text-right">Completion Rate</th>
              <th className="px-4 py-3 text-right">On-Time Rate</th>
              <th className="px-4 py-3 text-right">Avg Days</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.slice(0, 10).map((u) => (
              <tr key={u.user_id} className="hover:bg-gray-50/50 transition">
                <td className="px-4 py-3 font-medium text-gray-900">{u.user_name}</td>
                <td className="px-4 py-3 text-gray-500">{u.department || '—'}</td>
                <td className="px-4 py-3 text-right font-medium">{u.total_tasks}</td>
                <td className="px-4 py-3 text-right text-emerald-600 font-medium">{u.completed_tasks}</td>
                <td className="px-4 py-3 text-right text-rose-600 font-medium">{u.overdue_tasks}</td>
                <td className="px-4 py-3 text-right font-semibold">{u.completion_rate}%</td>
                <td className="px-4 py-3 text-right text-emerald-700">{u.on_time_completion_rate}%</td>
                <td className="px-4 py-3 text-right text-gray-600">{u.average_completion_days} d</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const OverdueChart: React.FC<{ data: OverdueAnalytics }> = ({ data }) => {
  const prioData = data.overdue_by_priority || [];

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Overdue Task Distribution by Priority</h3>
        <span className="text-xs font-semibold px-2.5 py-1 bg-rose-50 text-rose-700 rounded-md border border-rose-200">
          Total Overdue: {data.total_overdue}
        </span>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={prioData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="priority" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="count" name="Overdue Tasks" fill="#ef4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const EstimationChart: React.FC<{ data: EstimationAnalytics }> = ({ data }) => {
  const summaryData = [
    { name: 'Estimated Hours', value: data.total_estimated_hours, avg: data.average_estimated_hours },
    { name: 'Actual Hours', value: data.total_actual_hours, avg: data.average_actual_hours },
  ];

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Estimated vs Actual Hours</h3>
        <div className="text-xs text-gray-500">
          Underestimated: <span className="font-semibold text-rose-600">{data.underestimated_tasks_count}</span> | Overestimated: <span className="font-semibold text-emerald-600">{data.overestimated_tasks_count}</span>
        </div>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={summaryData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} unit=" hrs" />
            <Tooltip formatter={(val: number) => [`${val} hrs`, 'Hours']} />
            <Bar dataKey="value" name="Total Hours" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
