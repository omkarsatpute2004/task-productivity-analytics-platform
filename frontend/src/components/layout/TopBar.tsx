import React from 'react';
import { Menu, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { Link } from 'react-router-dom';

interface TopBarProps {
  onToggleSidebar: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onToggleSidebar }) => {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 sm:px-6 bg-white border-b border-gray-200 shadow-xs">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg md:hidden transition"
          aria-label="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h1 className="text-base sm:text-lg font-semibold text-gray-900 tracking-tight">
          Productivity & Task Management
        </h1>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              {user.role}
            </span>
            {user.department && (
              <span className="hidden md:inline-block text-xs font-medium text-gray-500 bg-gray-100 px-2.5 py-0.5 rounded-md">
                {user.department}
              </span>
            )}
            <Link
              to="/profile"
              className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 transition text-gray-700 hover:text-gray-900"
            >
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs border border-blue-200">
                {user.name ? user.name.charAt(0).toUpperCase() : <UserIcon className="w-4 h-4" />}
              </div>
              <span className="hidden sm:inline-block text-xs font-medium text-gray-800">
                {user.name}
              </span>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
