import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { Layout } from '../components/layout/Layout';

import { Login } from '../pages/Login';
import { Register } from '../pages/Register';
import { Dashboard } from '../pages/Dashboard';
import { Tasks } from '../pages/Tasks';
import { TaskDetails } from '../pages/TaskDetails';
import { CreateTask } from '../pages/CreateTask';
import { EditTask } from '../pages/EditTask';
import { Analytics } from '../pages/Analytics';
import { Users } from '../pages/Users';
import { Categories } from '../pages/Categories';
import { Profile } from '../pages/Profile';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Routes wrapped in Layout */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/tasks/new" element={<CreateTask />} />
        <Route path="/tasks/:id" element={<TaskDetails />} />
        <Route path="/tasks/:id/edit" element={<EditTask />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/profile" element={<Profile />} />

        {/* Admin-only Routes */}
        <Route
          path="/users"
          element={
            <ProtectedRoute requireAdmin>
              <Users />
            </ProtectedRoute>
          }
        />
        <Route
          path="/categories"
          element={
            <ProtectedRoute requireAdmin>
              <Categories />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
