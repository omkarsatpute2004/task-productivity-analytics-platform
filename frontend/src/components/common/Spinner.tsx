import React from 'react';

export const Spinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({
  size = 'md',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div
      className={`animate-spin rounded-full border-blue-600 border-t-transparent ${sizeClasses[size]} ${className}`}
      role="status"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export const CardSkeleton: React.FC = () => (
  <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
    <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-3 bg-gray-100 rounded w-2/3"></div>
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
    <div className="h-6 bg-gray-200 rounded w-full mb-4"></div>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="h-10 bg-gray-100 rounded w-full mb-2"></div>
    ))}
  </div>
);
