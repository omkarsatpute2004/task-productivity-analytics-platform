import React from 'react';
import { Link } from 'react-router-dom';
import { Eye, Edit2, Trash2, CheckCircle2 } from 'lucide-react';
import { Task, TaskStatus } from '../../types';
import { PriorityBadge, StatusBadge, DeadlineBadge } from '../common/Badge';

interface TaskTableProps {
  tasks: Task[];
  onDelete: (id: number) => void;
  onStatusChange: (id: number, status: TaskStatus) => void;
  currentUserId?: number;
  isAdmin?: boolean;
}

export const TaskTable: React.FC<TaskTableProps> = ({
  tasks,
  onDelete,
  onStatusChange,
  currentUserId,
  isAdmin,
}) => {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-xs overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider font-semibold border-b border-gray-100">
            <tr>
              <th className="px-4 py-3">Task Title</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Assigned User</th>
              <th className="px-4 py-3">Priority</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Deadline</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {tasks.map((t) => {
              const canEditOrDelete = isAdmin || t.user_id === currentUserId;

              return (
                <tr key={t.id} className="hover:bg-gray-50/60 transition">
                  <td className="px-4 py-3 font-medium text-gray-900 max-w-xs truncate">
                    <Link to={`/tasks/${t.id}`} className="hover:text-blue-600 font-semibold transition">
                      {t.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    <span className="bg-gray-100 px-2 py-0.5 rounded text-[11px] font-medium text-gray-700">
                      {t.category_name || t.category?.name || `Cat #${t.category_id}`}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700 font-medium">
                    {t.user_name || t.user?.name || `User #${t.user_id}`}
                  </td>
                  <td className="px-4 py-3">
                    <PriorityBadge priority={t.priority} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={t.status} />
                  </td>
                  <td className="px-4 py-3">
                    <DeadlineBadge deadline={t.deadline} status={t.status} completedAt={t.completed_at} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Link
                        to={`/tasks/${t.id}`}
                        title="View Details"
                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>

                      {t.status !== 'COMPLETED' && (
                        <button
                          onClick={() => onStatusChange(t.id, 'COMPLETED')}
                          title="Mark Completed"
                          className="p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                        </button>
                      )}

                      {canEditOrDelete && (
                        <>
                          <Link
                            to={`/tasks/${t.id}/edit`}
                            title="Edit Task"
                            className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                          >
                            <Edit2 className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => onDelete(t.id)}
                            title="Delete Task"
                            className="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
