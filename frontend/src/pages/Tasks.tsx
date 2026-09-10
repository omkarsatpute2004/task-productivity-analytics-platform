import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Plus, CheckSquare } from 'lucide-react';
import { taskApi, TaskQueryParams } from '../services/taskApi';
import { userApi } from '../services/userApi';
import { categoryApi } from '../services/categoryApi';
import { Task, User, Category, TaskStatus } from '../types';
import { TaskTable } from '../components/tasks/TaskTable';
import { TaskFilters } from '../components/tasks/TaskFilters';
import { Pagination } from '../components/common/Pagination';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
import { Spinner, TableSkeleton } from '../components/common/Spinner';
import { useToast } from '../components/common/Toast';
import { useAuth } from '../hooks/useAuth';

export const Tasks: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(15);

  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [userId, setUserId] = useState('');

  const [users, setUsers] = useState<User[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [deleteTargetId, setDeleteTargetId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const isAdmin = user?.role === 'ADMIN';

  // Load dropdown lists
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const [uRes, cRes] = await Promise.all([
          userApi.getUsers({ limit: 100 }),
          categoryApi.getCategories(),
        ]);
        setUsers(uRes.items);
        setCategories(cRes.items);
      } catch (err) {
        console.error('Failed to load filter metadata:', err);
      }
    };
    loadMetadata();
  }, []);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    try {
      const params: TaskQueryParams = {
        page: currentPage,
        limit: pageSize,
        search: search || undefined,
        status: status || undefined,
        priority: priority || undefined,
        category_id: categoryId ? parseInt(categoryId, 10) : undefined,
        user_id: userId ? parseInt(userId, 10) : undefined,
        sort_by: 'created_at',
        sort_order: 'desc',
      };

      const res = await taskApi.getTasks(params);
      setTasks(res.items);
      setTotalItems(res.total);
      setTotalPages(res.pages);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      showToast('Failed to load tasks', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, pageSize, search, status, priority, categoryId, userId, showToast]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleResetFilters = () => {
    setSearch('');
    setStatus('');
    setPriority('');
    setCategoryId('');
    setUserId('');
    setCurrentPage(1);
  };

  const handleStatusChange = async (id: number, newStatus: TaskStatus) => {
    try {
      await taskApi.updateTaskStatus(id, { status: newStatus });
      showToast(`Task status updated to ${newStatus}`, 'success');
      fetchTasks();
    } catch (err) {
      console.error('Failed to update status:', err);
      showToast('Failed to update task status', 'error');
    }
  };

  const confirmDelete = async () => {
    if (!deleteTargetId) return;
    setIsDeleting(true);
    try {
      await taskApi.deleteTask(deleteTargetId);
      showToast('Task deleted successfully', 'success');
      setDeleteTargetId(null);
      fetchTasks();
    } catch (err) {
      console.error('Failed to delete task:', err);
      showToast('Failed to delete task', 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">Tasks Management</h2>
          <p className="text-xs text-gray-500">View, search, filter, and manage tasks across your team</p>
        </div>

        <Link
          to="/tasks/new"
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition shadow-xs"
        >
          <Plus className="w-4 h-4" />
          Create New Task
        </Link>
      </div>

      {/* Filters Bar */}
      <TaskFilters
        search={search}
        onSearchChange={(val) => {
          setSearch(val);
          setCurrentPage(1);
        }}
        status={status}
        onStatusChange={(val) => {
          setStatus(val);
          setCurrentPage(1);
        }}
        priority={priority}
        onPriorityChange={(val) => {
          setPriority(val);
          setCurrentPage(1);
        }}
        categoryId={categoryId}
        onCategoryChange={(val) => {
          setCategoryId(val);
          setCurrentPage(1);
        }}
        userId={userId}
        onUserChange={(val) => {
          setUserId(val);
          setCurrentPage(1);
        }}
        users={users}
        categories={categories}
        isAdmin={isAdmin}
        onReset={handleResetFilters}
      />

      {/* Task List / Table */}
      {isLoading ? (
        <TableSkeleton rows={8} />
      ) : tasks.length === 0 ? (
        <EmptyState
          title="No tasks match your filters"
          description="Try clearing search keywords or adjusting priority, status, and category filters."
          action={
            <button
              onClick={handleResetFilters}
              className="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition"
            >
              Reset All Filters
            </button>
          }
        />
      ) : (
        <div>
          <TaskTable
            tasks={tasks}
            onDelete={(id) => setDeleteTargetId(id)}
            onStatusChange={handleStatusChange}
            currentUserId={user?.id}
            isAdmin={isAdmin}
          />
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
      <Modal
        isOpen={!!deleteTargetId}
        onClose={() => setDeleteTargetId(null)}
        title="Confirm Task Deletion"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-600">
            Are you sure you want to delete this task? This action will permanently remove the task and its activity audit logs.
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
              {isDeleting ? 'Deleting...' : 'Delete Task'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
