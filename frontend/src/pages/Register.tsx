import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { UserPlus, Mail, Lock, User as UserIcon, Building, AlertCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../components/common/Toast';

const registerSchema = z.object({
  name: z.string().min(1, 'Full name is required').max(100, 'Name too long'),
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  department: z.string().optional(),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const Register: React.FC = () => {
  const { register: registerAuth } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      await registerAuth(data);
      showToast('Registration successful! Please log in.', 'success');
      navigate('/login');
    } catch (err: any) {
      console.error('Registration error:', err);
      const msg = err.response?.data?.detail || 'Registration failed. Email may already be in use.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl border border-gray-100 shadow-xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-blue-50 text-blue-600 mb-2">
            <UserPlus className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Create Account</h2>
          <p className="text-xs text-gray-500">Join Task Productivity & Analytics Platform</p>
        </div>

        {errorMessage && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Full Name</label>
            <div className="relative">
              <UserIcon className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="text"
                {...register('name')}
                placeholder="Jane Doe"
                className="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>
            {errors.name && <p className="mt-1 text-[11px] text-rose-600">{errors.name.message}</p>}
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="email"
                {...register('email')}
                placeholder="jane@company.com"
                className="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>
            {errors.email && <p className="mt-1 text-[11px] text-rose-600">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="password"
                {...register('password')}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>
            {errors.password && <p className="mt-1 text-[11px] text-rose-600">{errors.password.message}</p>}
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Department</label>
            <div className="relative">
              <Building className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="text"
                {...register('department')}
                placeholder="Engineering, Product, Marketing..."
                className="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition shadow-xs"
          >
            {isLoading ? 'Creating Account...' : 'Register Account'}
          </button>
        </form>

        <div className="text-center text-xs text-gray-500 pt-2 border-t border-gray-100">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
