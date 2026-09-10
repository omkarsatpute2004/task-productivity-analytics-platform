import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Category, TaskPriority, TaskStatus, TaskCreate, TaskUpdate } from '../../types';

const taskSchema = z.object({
  title: z.string().min(1, 'Task title is required').max(200, 'Title cannot exceed 200 characters'),
  description: z.string().optional(),
  user_id: z.coerce.number().min(1, 'Assigned user is required'),
  category_id: z.coerce.number().min(1, 'Category is required'),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
  status: z.enum(['TODO', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']).default('TODO'),
  deadline: z.string().optional(),
  estimated_hours: z.coerce.number().min(0, 'Estimated hours must be non-negative').optional().nullable(),
  actual_hours: z.coerce.number().min(0, 'Actual hours must be non-negative').optional().nullable(),
});

export type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  initialValues?: Partial<TaskFormData>;
  users: User[];
  categories: Category[];
  onSubmit: (data: TaskFormData) => Promise<void>;
  isLoading?: boolean;
  isEditing?: boolean;
  isAdmin?: boolean;
  currentUserId?: number;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  initialValues,
  users,
  categories,
  onSubmit,
  isLoading,
  isEditing,
  isAdmin,
  currentUserId,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initialValues?.title || '',
      description: initialValues?.description || '',
      user_id: initialValues?.user_id || currentUserId || (users[0]?.id ?? 1),
      category_id: initialValues?.category_id || (categories[0]?.id ?? 1),
      priority: initialValues?.priority || 'MEDIUM',
      status: initialValues?.status || 'TODO',
      deadline: initialValues?.deadline ? new Date(initialValues.deadline).toISOString().slice(0, 16) : '',
      estimated_hours: initialValues?.estimated_hours ?? 0,
      actual_hours: initialValues?.actual_hours ?? 0,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 bg-white p-6 rounded-xl border border-gray-100 shadow-xs">
      <div>
        <label className="block text-xs font-semibold text-gray-700 mb-1">
          Task Title <span className="text-rose-500">*</span>
        </label>
        <input
          type="text"
          {...register('title')}
          placeholder="e.g. Implement JWT Auth Flow"
          className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
        />
        {errors.title && <p className="mt-1 text-[11px] text-rose-600">{errors.title.message}</p>}
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-700 mb-1">Description</label>
        <textarea
          rows={3}
          {...register('description')}
          placeholder="Add detailed task scope, requirements, or links..."
          className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            Category <span className="text-rose-500">*</span>
          </label>
          <select
            {...register('category_id')}
            className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg bg-white focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          >
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          {errors.category_id && <p className="mt-1 text-[11px] text-rose-600">{errors.category_id.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            Assigned User <span className="text-rose-500">*</span>
          </label>
          <select
            {...register('user_id')}
            disabled={!isAdmin && isEditing}
            className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg bg-white disabled:bg-gray-100 disabled:cursor-not-allowed focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          >
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name} ({u.email})
              </option>
            ))}
          </select>
          {errors.user_id && <p className="mt-1 text-[11px] text-rose-600">{errors.user_id.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">Priority</label>
          <select
            {...register('priority')}
            className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg bg-white focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          >
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">Status</label>
          <select
            {...register('status')}
            className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg bg-white focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          >
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">Deadline</label>
          <input
            type="datetime-local"
            {...register('deadline')}
            className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">Estimated Hours</label>
          <input
            type="number"
            step="0.5"
            min="0"
            {...register('estimated_hours')}
            placeholder="e.g. 8.0"
            className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          />
          {errors.estimated_hours && <p className="mt-1 text-[11px] text-rose-600">{errors.estimated_hours.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">Actual Hours Spent</label>
          <input
            type="number"
            step="0.5"
            min="0"
            {...register('actual_hours')}
            placeholder="e.g. 10.5"
            className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          />
          {errors.actual_hours && <p className="mt-1 text-[11px] text-rose-600">{errors.actual_hours.message}</p>}
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
        <button
          type="submit"
          disabled={isLoading}
          className="px-5 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition shadow-xs"
        >
          {isLoading ? 'Saving...' : isEditing ? 'Update Task' : 'Create Task'}
        </button>
      </div>
    </form>
  );
};
