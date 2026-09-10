import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit2, Trash2, Calendar, Clock, User as UserIcon, Folder, Tag } from 'lucide-react';
import { taskApi } from '../services/taskApi';
import { Task, TaskActivity, TaskStatus } from '../types';
import { PriorityBadge, StatusBadge, DeadlineBadge } from '../components/common/Badge';
import { TaskActivityTimeline } from '../components/tasks/TaskActivityTimeline';
import { TaskRiskPredictionCard } from '../components/tasks/TaskRiskPredictionCard';
import { Spinner } from '../components/common/Spinner';

import { Modal } from '../components/common/Modal';
import { useToast } from '../components/common/Toast';
import { useAuth } from '../hooks/useAuth';

export const TaskDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [task, setTask] = useState<Task | null>(null);
  const [activities, setActivities] = useState<TaskActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const taskId = parseInt(id || '0', 10);
  const isAdmin = user?.role === 'ADMIN';
  const canEditOrDelete = isAdmin || task?.user_id === user?.id;

  const loadTaskDetails = useCallback(async () => {
    if (!taskId) return;
    setIsLoading(true);
    try {
      const [tRes, actRes] = await Promise.all([
        taskApi.getTask(taskId),
        taskApi.getTaskActivity(taskId),
      ]);
      setTask(tRes);
      setActivities(actRes);
    } catch (err) {
      console.error('Failed to load task details:', err);
      showToast('Task not found or access denied', 'error');
      navigate('/tasks');
    } finally {
      setIsLoading(false);
    }
  }, [taskId, navigate, showToast]);

  useEffect(() => {
    loadTaskDetails();
  }, [loadTaskDetails]);

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (!task) return;
    try {
      const updated = await taskApi.updateTaskStatus(task.id, { status: newStatus });
      setTask(updated);
      showToast(`Status updated to ${newStatus}`, 'success');
      // Refresh activity timeline
      const actRes = await taskApi.getTaskActivity(task.id);
      setActivities(actRes);
    } catch (err) {
      console.error('Failed to update status:', err);
      showToast('Failed to update status', 'error');
    }
  };

  const confirmDelete = async () => {
    if (!task) return;
    setIsDeleting(true);
    try {
      await taskApi.deleteTask(task.id);
      showToast('Task deleted successfully', 'success');
      navigate('/tasks');
    } catch (err) {
      console.error('Failed to delete task:', err);
      showToast('Failed to delete task', 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center p-16">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!task) return null;

  return (
    <div className="space-y-6">
      {/* Back & Actions Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Link
          to="/tasks"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-900 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Tasks
        </Link>

        {canEditOrDelete && (
          <div className="flex items-center gap-3">
            <Link
              to={`/tasks/${task.id}/edit`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <Edit2 className="w-3.5 h-3.5" />
              Edit Task
            </Link>
            <button
              onClick={() => setIsDeleteModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 bg-rose-50 border border-rose-200 rounded-lg hover:bg-rose-100 transition"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete Task
            </button>
          </div>
        )}
      </div>

      {/* Main Task Card */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-gray-100 pb-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-400">Task #{task.id}</span>
              <PriorityBadge priority={task.priority} />
              <StatusBadge status={task.status} />
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900">{task.title}</h2>
          </div>

          {/* Quick Status Update */}
          <div className="flex items-center gap-2">
            <label className="text-xs font-medium text-gray-500">Status:</label>
            <select
              value={task.status}
              onChange={(e) => handleStatusChange(e.target.value as TaskStatus)}
              className="px-2.5 py-1.5 text-xs border border-gray-200 rounded-lg bg-gray-50 font-medium text-gray-800"
            >
              <option value="TODO">To Do</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Description */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Description</h4>
          <p className="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed">
            {task.description || 'No detailed description provided.'}
          </p>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50/60 rounded-xl border border-gray-100 text-xs">
          <div>
            <span className="text-gray-400 block mb-1 flex items-center gap-1">
              <Folder className="w-3.5 h-3.5" /> Category
            </span>
            <span className="font-semibold text-gray-900">
              {task.category_name || task.category?.name || `ID #${task.category_id}`}
            </span>
          </div>

          <div>
            <span className="text-gray-400 block mb-1 flex items-center gap-1">
              <UserIcon className="w-3.5 h-3.5" /> Assigned User
            </span>
            <span className="font-semibold text-gray-900">
              {task.user_name || task.user?.name || `User #${task.user_id}`}
            </span>
          </div>

          <div>
            <span className="text-gray-400 block mb-1 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" /> Deadline Status
            </span>
            <DeadlineBadge deadline={task.deadline} status={task.status} completedAt={task.completed_at} />
          </div>

          <div>
            <span className="text-gray-400 block mb-1 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> Estimated / Actual Hours
            </span>
            <span className="font-semibold text-gray-900">
              {task.estimated_hours ?? 0} hrs est. / {task.actual_hours ?? 0} hrs act.
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 text-[11px] text-gray-400 pt-2 border-t border-gray-100">
          <span>Created: {new Date(task.created_at).toLocaleString()}</span>
          <span>Updated: {new Date(task.updated_at).toLocaleString()}</span>
          {task.completed_at && (
            <span className="text-emerald-600 font-medium">
              Completed At: {new Date(task.completed_at).toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {/* AI Task Risk Prediction Card */}
      <TaskRiskPredictionCard task={task} />

      {/* Activity Timeline */}
      <TaskActivityTimeline activities={activities} />

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Task"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-600">
            Are you sure you want to delete this task? This cannot be undone.
          </p>
          <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
            <button
              onClick={() => setIsDeleteModalOpen(false)}
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
