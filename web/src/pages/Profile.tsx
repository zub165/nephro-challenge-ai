import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import { useAuthStore } from '@/store/authStore';
import type { UserStats } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import StatsCard from '@/components/StatsCard';
import toast from 'react-hot-toast';
import {
  UserIcon,
  AcademicCapIcon,
  FireIcon,
  ChartBarIcon,
  TrophyIcon,
  EnvelopeIcon,
  CalendarIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

export default function Profile() {
  const { user, updateUser } = useAuthStore();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');

  const { data: stats, isLoading } = useQuery<UserStats>({
    queryKey: ['user-stats'],
    queryFn: () => api.get('/stats').then((r) => r.data),
  });

  const updateMutation = useMutation({
    mutationFn: (newName: string) => api.put('/auth/profile', { name: newName }),
    onSuccess: (res) => {
      updateUser(res.data.user || res.data);
      toast.success('Profile updated');
      setEditing(false);
    },
    onError: () => toast.error('Failed to update profile'),
  });

  const handleSave = () => {
    if (!name.trim()) {
      toast.error('Name cannot be empty');
      return;
    }
    updateMutation.mutate(name);
  };

  if (isLoading) return <LoadingSpinner text="Loading profile..." />;

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary-100 dark:bg-primary-900/30">
            <UserIcon className="h-10 w-10 text-primary-700 dark:text-primary-300" />
          </div>

          <div className="flex-1 text-center sm:text-left">
            {editing ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-field max-w-xs"
                  autoFocus
                />
                <button onClick={handleSave} className="btn-primary text-sm" disabled={updateMutation.isPending}>
                  Save
                </button>
                <button onClick={() => { setEditing(false); setName(user?.name || ''); }} className="btn-outline text-sm">
                  Cancel
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {user?.name}
                </h1>
                <button
                  onClick={() => setEditing(true)}
                  className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
              </div>
            )}

            <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1.5">
                <EnvelopeIcon className="h-4 w-4" />
                {user?.email}
              </span>
              {user?.createdAt && (
                <span className="flex items-center gap-1.5">
                  <CalendarIcon className="h-4 w-4" />
                  Joined {format(new Date(user.createdAt), 'MMM yyyy')}
                </span>
              )}
              <span className="flex items-center gap-1.5">
                <ShieldCheckIcon className="h-4 w-4" />
                {user?.role === 'admin' ? 'Administrator' : 'Learner'}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Quizzes"
          value={stats?.totalQuizzes ?? 0}
          icon={<AcademicCapIcon className="h-6 w-6" />}
          color="primary"
        />
        <StatsCard
          title="Accuracy"
          value={`${stats?.accuracy ?? 0}%`}
          icon={<ChartBarIcon className="h-6 w-6" />}
          color={stats?.accuracy && stats.accuracy >= 70 ? 'green' : 'amber'}
        />
        <StatsCard
          title="Current Streak"
          value={`${stats?.currentStreak ?? 0} days`}
          icon={<FireIcon className="h-6 w-6" />}
          color="amber"
        />
        <StatsCard
          title="Best Streak"
          value={`${stats?.longestStreak ?? 0} days`}
          icon={<TrophyIcon className="h-6 w-6" />}
          color="teal"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
          Category Performance
        </h2>
        {stats?.categoryBreakdown && stats.categoryBreakdown.length > 0 ? (
          <div className="space-y-4">
            {stats.categoryBreakdown.map((cat) => (
              <div key={cat.categoryId}>
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {cat.categoryName}
                  </span>
                  <span className={`text-sm font-bold ${
                    cat.accuracy >= 75 ? 'text-green-600 dark:text-green-400' :
                    cat.accuracy >= 50 ? 'text-amber-600 dark:text-amber-400' :
                    'text-red-600 dark:text-red-400'
                  }`}>
                    {cat.accuracy}%
                  </span>
                </div>
                <div className="h-2.5 w-full rounded-full bg-gray-100 dark:bg-gray-700">
                  <div
                    className={`h-2.5 rounded-full transition-all ${
                      cat.accuracy >= 75 ? 'bg-green-500' :
                      cat.accuracy >= 50 ? 'bg-amber-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${cat.accuracy}%` }}
                  />
                </div>
                <p className="mt-0.5 text-xs text-gray-400">
                  {cat.correctAnswers}/{cat.totalQuestions} correct
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 py-10 text-center">
            <ChartBarIcon className="h-10 w-10 text-gray-300 dark:text-gray-600" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No quiz data yet. Start taking quizzes to see your performance breakdown.
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
