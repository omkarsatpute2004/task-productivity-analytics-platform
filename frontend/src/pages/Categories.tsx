import React, { useState, useEffect, useCallback } from 'react';
import { FolderKanban, Plus, Edit, Trash2 } from 'lucide-react';
import { categoryApi } from '../services/categoryApi';
import { Category } from '../types';
import { Modal } from '../components/common/Modal';
import { Spinner, TableSkeleton } from '../components/common/Spinner';
import { useToast } from '../components/common/Toast';

export const Categories: React.FC = () => {
  const { showToast } = useToast();

  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [editCategory, setEditCategory] = useState<Category | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchCategories = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await categoryApi.getCategories();
      setCategories(res.items);
    } catch (err) {
      console.error('Failed to load categories:', err);
      showToast('Failed to load categories', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);
    try {
      await categoryApi.createCategory({ name, description: description || undefined });
      showToast('Category created successfully', 'success');
      setName('');
      setDescription('');
      setIsCreateModalOpen(false);
      fetchCategories();
    } catch (err: any) {
      console.error('Failed to create category:', err);
      const msg = err.response?.data?.detail || 'Failed to create category. Name may already exist.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editCategory || !name.trim()) return;
    setIsSubmitting(true);
    try {
      await categoryApi.updateCategory(editCategory.id, { name, description: description || undefined });
      showToast('Category updated successfully', 'success');
      setEditCategory(null);
      setName('');
      setDescription('');
      fetchCategories();
    } catch (err: any) {
      console.error('Failed to update category:', err);
      const msg = err.response?.data?.detail || 'Failed to update category.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTargetId) return;
    setIsDeleting(true);
    try {
      await categoryApi.deleteCategory(deleteTargetId);
      showToast('Category deleted successfully', 'success');
      setDeleteTargetId(null);
      fetchCategories();
    } catch (err: any) {
      console.error('Failed to delete category:', err);
      const msg = err.response?.data?.detail || 'Cannot delete category that is assigned to tasks.';
      showToast(msg, 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">Category Management</h2>
          <p className="text-xs text-gray-500">Organize tasks into categories for analytical grouping</p>
        </div>

        <button
          onClick={() => {
            setName('');
            setDescription('');
            setIsCreateModalOpen(true);
          }}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition shadow-xs"
        >
          <Plus className="w-4 h-4" />
          Add Category
        </button>
      </div>

      {isLoading ? (
        <TableSkeleton rows={5} />
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 shadow-xs overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider font-semibold border-b border-gray-100">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Category Name</th>
                <th className="px-4 py-3">Description</th>
                <th className="px-4 py-3">Created Date</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {categories.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50/60 transition">
                  <td className="px-4 py-3 text-gray-400 font-mono text-[11px]">#{c.id}</td>
                  <td className="px-4 py-3 font-semibold text-gray-900">{c.name}</td>
                  <td className="px-4 py-3 text-gray-600">{c.description || '—'}</td>
                  <td className="px-4 py-3 text-gray-500">{new Date(c.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => {
                          setEditCategory(c);
                          setName(c.name);
                          setDescription(c.description || '');
                        }}
                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                        title="Edit Category"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteTargetId(c.id)}
                        className="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                        title="Delete Category"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Create New Category">
        <form onSubmit={handleCreateCategory} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Category Name *</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Backend Development"
              className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of tasks included in this category..."
              className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(false)}
              className="px-4 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {isSubmitting ? 'Creating...' : 'Create Category'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={!!editCategory} onClose={() => setEditCategory(null)} title="Edit Category">
        <form onSubmit={handleUpdateCategory} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Category Name *</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setEditCategory(null)}
              className="px-4 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={!!deleteTargetId} onClose={() => setDeleteTargetId(null)} title="Delete Category">
        <div className="space-y-4">
          <p className="text-xs text-gray-600">
            Are you sure you want to delete this category? Categories assigned to active tasks cannot be deleted.
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
              {isDeleting ? 'Deleting...' : 'Delete Category'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
