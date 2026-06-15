import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import LoadingSpinner from '@/components/LoadingSpinner';
import StatsCard from '@/components/StatsCard';
import {
  UsersIcon,
  QuestionMarkCircleIcon,
  AcademicCapIcon,
  ShieldCheckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

interface AdminStats {
  totalUsers: number;
  totalQuestions: number;
  aiGeneratedPending: number;
  totalQuizzes: number;
  recentUsers: { id: string; name: string; email: string; createdAt: string }[];
}

export default function AdminDashboard() {
  const { data: stats, isLoading, error } = useQuery<AdminStats>({
    queryKey: ['admin-stats'],
    queryFn: () => api.get('/admin/stats').then((r) => r.data),
  });

  if (isLoading) return <LoadingSpinner text="Loading admin panel..." />;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Failed to load admin data</p>
        <button onClick={() => window.location.reload()} className="btn-primary text-sm">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Admin Dashboard
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Manage the Nephro Challenge platform
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Users"
          value={stats?.totalUsers ?? 0}
          icon={<UsersIcon className="h-6 w-6" />}
          color="primary"
        />
        <StatsCard
          title="Questions"
          value={stats?.totalQuestions ?? 0}
          icon={<QuestionMarkCircleIcon className="h-6 w-6" />}
          color="teal"
        />
        <StatsCard
          title="Pending AI Review"
          value={stats?.aiGeneratedPending ?? 0}
          icon={<SparklesIcon className="h-6 w-6" />}
          color="amber"
        />
        <StatsCard
          title="Total Quizzes"
          value={stats?.totalQuizzes ?? 0}
          icon={<AcademicCapIcon className="h-6 w-6" />}
          color="green"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card lg:col-span-2"
        >
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
            Quick Actions
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <Link
              to="/admin/questions"
              className="flex items-center gap-3 rounded-xl border border-gray-200 p-4 transition-all hover:border-primary-300 hover:bg-primary-50 dark:border-gray-700 dark:hover:border-primary-700 dark:hover:bg-primary-900/20"
            >
              <QuestionMarkCircleIcon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              <div>
                <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">Manage Questions</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Create, edit, delete questions</p>
              </div>
            </Link>

            <Link
              to="/admin/ai-generated"
              className="flex items-center gap-3 rounded-xl border border-gray-200 p-4 transition-all hover:border-amber-300 hover:bg-amber-50 dark:border-gray-700 dark:hover:border-amber-700 dark:hover:bg-amber-900/20"
            >
              <SparklesIcon className="h-8 w-8 text-amber-600 dark:text-amber-400" />
              <div>
                <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">AI Review</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {stats?.aiGeneratedPending ?? 0} pending reviews
                </p>
              </div>
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Recent Users</h2>
          </div>
          {stats?.recentUsers && stats.recentUsers.length > 0 ? (
            <div className="space-y-3">
              {stats.recentUsers.slice(0, 5).map((u) => (
                <div key={u.id} className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700 dark:bg-primary-900/30 dark:text-primary-300">
                    {u.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">{u.name}</p>
                    <p className="truncate text-xs text-gray-500 dark:text-gray-400">{u.email}</p>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(u.createdAt).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="py-6 text-center text-sm text-gray-500 dark:text-gray-400">
              No recent users
            </p>
          )}
        </motion.div>
      </div>
    </div>
  );
}
