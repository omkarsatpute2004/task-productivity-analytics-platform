import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { taskApi } from '../services/taskApi';
import { userApi } from '../services/userApi';
import { categoryApi } from '../services/categoryApi';
import { User, Category } from '../types';
import { TaskForm, TaskFormData } from '../components/tasks/TaskForm';
import { Spinner } from '../components/common/Spinner';
import { useToast } from '../components/common/Toast';
import { useAuth } from '../hooks/useAuth';

export const CreateTask: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [users, setUsers] = useState<User[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoadingMetadata, setIsLoadingMetadata] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const [uRes, cRes] = await Promise.all([
          userApi.getAssignableUsers({ limit: 100 }),
          categoryApi.getCategories(),
        ]);
        setUsers(uRes.items);
        setCategories(cRes.items);
      } catch (err) {
        console.error('Failed to load form dropdown data:', err);
        showToast('Failed to load user or category options', 'error');
      } finally {
        setIsLoadingMetadata(false);
      }
    };
    loadMetadata();
  }, [showToast]);

  const handleSubmit = async (data: TaskFormData) => {
    setIsSubmitting(true);
    try {
      await taskApi.createTask({
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
      showToast('Task created successfully', 'success');
      navigate('/tasks');
    } catch (err: any) {
      console.error('Failed to create task:', err);
      const msg = err.response?.data?.detail || 'Failed to create task.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingMetadata) {
    return (
      <div className="flex justify-center p-16">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Link
          to="/tasks"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-900 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Tasks
        </Link>
      </div>

      <div>
        <h2 className="text-xl font-bold text-gray-900 tracking-tight">Create New Task</h2>
        <p className="text-xs text-gray-500">Fill in task title, assignment, category, priority, and deadline</p>
      </div>

      <TaskForm
        users={users}
        categories={categories}
        onSubmit={handleSubmit}
        isLoading={isSubmitting}
        isAdmin={user?.role === 'ADMIN'}
        currentUserId={user?.id}
      />
    </div>
  );
};
