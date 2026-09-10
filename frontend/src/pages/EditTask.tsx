import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { taskApi } from '../services/taskApi';
import { userApi } from '../services/userApi';
import { categoryApi } from '../services/categoryApi';
import { Task, User, Category } from '../types';
import { TaskForm, TaskFormData } from '../components/tasks/TaskForm';
import { Spinner } from '../components/common/Spinner';
import { useToast } from '../components/common/Toast';
import { useAuth } from '../hooks/useAuth';

export const EditTask: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [task, setTask] = useState<Task | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const taskId = parseInt(id || '0', 10);

  const loadData = useCallback(async () => {
    if (!taskId) return;
    setIsLoading(true);
    try {
      const [tRes, uRes, cRes] = await Promise.all([
        taskApi.getTask(taskId),
        userApi.getUsers({ limit: 100 }),
        categoryApi.getCategories(),
      ]);
      setTask(tRes);
      setUsers(uRes.items);
      setCategories(cRes.items);
    } catch (err) {
      console.error('Failed to load edit task data:', err);
      showToast('Task not found or access denied', 'error');
      navigate('/tasks');
    } finally {
      setIsLoading(false);
    }
  }, [taskId, navigate, showToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSubmit = async (data: TaskFormData) => {
    if (!task) return;
    setIsSubmitting(true);
    try {
      await taskApi.updateTask(task.id, {
        title: data.title,
        description: data.description || undefined,
        user_id: data.user_id,
        category_id: data.category_id,
        priority: data.priority,
        status: data.status,
        deadline: data.deadline ? new Date(data.deadline).toISOString() : undefined,
        estimated_hours: data.estimated_hours ?? undefined,
        actual_hours: data.actual_hours ?? undefined,
      });
      showToast('Task updated successfully', 'success');
      navigate(`/tasks/${task.id}`);
    } catch (err: any) {
      console.error('Failed to update task:', err);
      const msg = err.response?.data?.detail || 'Failed to update task.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
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
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Link
          to={`/tasks/${task.id}`}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-900 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Task Details
        </Link>
      </div>

      <div>
        <h2 className="text-xl font-bold text-gray-900 tracking-tight">Edit Task #{task.id}</h2>
        <p className="text-xs text-gray-500">Update task scope, priority, assigned user, status, or hours</p>
      </div>

      <TaskForm
        initialValues={{
          title: task.title,
          description: task.description || '',
          user_id: task.user_id,
          category_id: task.category_id,
          priority: task.priority,
          status: task.status,
          deadline: task.deadline || undefined,
          estimated_hours: task.estimated_hours,
          actual_hours: task.actual_hours,
        }}
        users={users}
        categories={categories}
        onSubmit={handleSubmit}
        isLoading={isSubmitting}
        isEditing={true}
        isAdmin={user?.role === 'ADMIN'}
        currentUserId={user?.id}
      />
    </div>
  );
};
