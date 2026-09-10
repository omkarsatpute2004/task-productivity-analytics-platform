import React, { useState } from 'react';
import { UserCircle, Mail, Building, Shield, Calendar } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { userApi } from '../services/userApi';
import { useToast } from '../components/common/Toast';

export const Profile: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const { showToast } = useToast();

  const [department, setDepartment] = useState(user?.department || '');
  const [isUpdating, setIsUpdating] = useState(false);

  if (!user) return null;

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);
    try {
      await userApi.updateUser(user.id, { department });
      await refreshUser();
      showToast('Profile department updated', 'success');
    } catch (err) {
      console.error('Failed to update profile:', err);
      showToast('Failed to update profile', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">My Account Profile</h2>
        <p className="text-xs text-gray-500">View personal details and manage department assignments</p>
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-xs space-y-6">
        <div className="flex items-center gap-4 border-b border-gray-100 pb-6">
          <div className="w-16 h-16 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-2xl font-bold border-2 border-blue-200">
            {user.name ? user.name.charAt(0).toUpperCase() : <UserCircle className="w-8 h-8" />}
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">{user.name}</h3>
            <p className="text-xs text-gray-500">{user.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                {user.role}
              </span>
              {user.department && (
                <span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                  {user.department}
                </span>
              )}
            </div>
          </div>
        </div>

        <form onSubmit={handleUpdate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-gray-700 mb-1 flex items-center gap-1.5">
                <UserCircle className="w-4 h-4 text-gray-400" /> Full Name
              </label>
              <input
                type="text"
                disabled
                value={user.name}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1 flex items-center gap-1.5">
                <Mail className="w-4 h-4 text-gray-400" /> Email Address
              </label>
              <input
                type="email"
                disabled
                value={user.email}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1 flex items-center gap-1.5">
                <Building className="w-4 h-4 text-gray-400" /> Department
              </label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="Engineering, Product, Analytics..."
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1 flex items-center gap-1.5">
                <Shield className="w-4 h-4 text-gray-400" /> Authorization Role
              </label>
              <input
                type="text"
                disabled
                value={user.role}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-gray-100">
            <button
              type="submit"
              disabled={isUpdating}
              className="px-5 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition shadow-xs"
            >
              {isUpdating ? 'Saving...' : 'Update Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
