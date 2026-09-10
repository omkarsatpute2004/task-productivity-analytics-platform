import React, { ReactNode } from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: string;
  color?: 'blue' | 'emerald' | 'amber' | 'rose' | 'indigo' | 'purple' | 'slate';
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color = 'blue',
}) => {
  const colorMap = {
    blue: 'text-blue-600 bg-blue-50 border-blue-100',
    emerald: 'text-emerald-600 bg-emerald-50 border-emerald-100',
    amber: 'text-amber-600 bg-amber-50 border-amber-100',
    rose: 'text-rose-600 bg-rose-50 border-rose-100',
    indigo: 'text-indigo-600 bg-indigo-50 border-indigo-100',
    purple: 'text-purple-600 bg-purple-50 border-purple-100',
    slate: 'text-slate-600 bg-slate-50 border-slate-100',
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-xs hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">{title}</span>
        {icon && <div className={`p-2 rounded-lg border ${colorMap[color]}`}>{icon}</div>}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">{value}</span>
      </div>
      {subtitle && <p className="mt-1 text-xs text-gray-500">{subtitle}</p>}
    </div>
  );
};
