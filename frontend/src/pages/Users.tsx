import React, { useState, useEffect, useCallback } from 'react';
import { Users as UsersIcon, Trash2, Edit, Search } from 'lucide-react';
import { userApi } from '../services/userApi';
import { User } from '../types';
import { Modal } from '../components/common/Modal';
import { Pagination } from '../components/common/Pagination';
import { Spinner, TableSkeleton } from '../components/common/Spinner';
import { useToast } from '../components/common/Toast';
import { useAuth } from '../hooks/useAuth';

export const Users: React.FC = () => {
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();

  const [users, setUsers] = useState<User[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');

  const [isLoading, setIsLoading] = useState(true);
  const [deleteTargetId, setDeleteTargetId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const [editUser, setEditUser] = useState<User | null>(null);
  const [editDepartment, setEditDepartment] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await userApi.getUsers({
        page: currentPage,
        limit: pageSize,
        search: search || undefined,
      });
      setUsers(res.items);
      setTotalItems(res.total);
      setTotalPages(res.pages);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      showToast('Failed to load users list', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, pageSize, search, showToast]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const confirmDelete = async () => {
    if (!deleteTargetId) return;
    setIsDeleting(true);
    try {
      await userApi.deleteUser(deleteTargetId);
      showToast('User deleted successfully', 'success');
      setDeleteTargetId(null);
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to delete user:', err);
      const msg = err.response?.data?.detail || 'Failed to delete user.';
      showToast(msg, 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleUpdateDepartment = async () => {
    if (!editUser) return;
    setIsUpdating(true);
    try {
      await userApi.updateUser(editUser.id, { department: editDepartment });
      showToast('User department updated', 'success');
      setEditUser(null);
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to update user:', err);
      showToast('Failed to update user department', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">User Management</h2>
          <p className="text-xs text-gray-500">System user directory and departmental assignments (Admin access)</p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-xs">
        <div className="relative max-w-sm">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full pl-9 pr-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Users Table */}
      {isLoading ? (
        <TableSkeleton rows={8} />
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider font-semibold border-b border-gray-100">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Joined Date</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50/60 transition">
                    <td className="px-4 py-3 text-gray-400 font-mono text-[11px]">#{u.id}</td>
                    <td className="px-4 py-3 font-semibold text-gray-900">{u.name}</td>
                    <td className="px-4 py-3 text-gray-600">{u.email}</td>
                    <td className="px-4 py-3 text-gray-700">
                      {u.department ? (
                        <span className="bg-gray-100 px-2 py-0.5 rounded text-[11px] font-medium text-gray-700">
                          {u.department}
                        </span>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${
                          u.role === 'ADMIN'
                            ? 'bg-purple-50 text-purple-700 border-purple-200'
                            : 'bg-blue-50 text-blue-700 border-blue-200'
                        }`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => {
                            setEditUser(u);
                            setEditDepartment(u.department || '');
                          }}
                          className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                          title="Edit Department"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        {u.id !== currentUser?.id && (
                          <button
                            onClick={() => setDeleteTargetId(u.id)}
                            className="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                            title="Delete User"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={pageSize}
            onPageChange={(p) => setCurrentPage(p)}
          />
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal isOpen={!!deleteTargetId} onClose={() => setDeleteTargetId(null)} title="Delete User">
        <div className="space-y-4">
          <p className="text-xs text-gray-600">
            Are you sure you want to delete this user? Their assigned tasks will remain or be unassigned.
          </p>
          <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
            <button
              onClick={() => setDeleteTargetId(null)}
              className="px-4 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              onClick={confirmDelete}
              disabled={isDeleting}
              className="px-4 py-1.5 text-xs font-semibold text-white bg-rose-600 rounded-lg hover:bg-rose-700 disabled:opacity-50 transition"
            >
              {isDeleting ? 'Deleting...' : 'Delete User'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Edit Department Modal */}
      <Modal isOpen={!!editUser} onClose={() => setEditUser(null)} title={`Edit Department for ${editUser?.name}`}>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Department</label>
            <input
              type="text"
              value={editDepartment}
              onChange={(e) => setEditDepartment(e.target.value)}
              placeholder="e.g. Engineering, Sales, Product..."
              className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
            <button
              onClick={() => setEditUser(null)}
              className="px-4 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleUpdateDepartment}
              disabled={isUpdating}
              className="px-4 py-1.5 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {isUpdating ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
