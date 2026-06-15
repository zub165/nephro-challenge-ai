import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import type { UserStats } from '@/types';
import StatsCard from '@/components/StatsCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
  AcademicCapIcon,
  TrophyIcon,
  FireIcon,
  ChartBarIcon,
  ArrowRightIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { useAuthStore } from '@/store/authStore';

export default function Dashboard() {
  const { user } = useAuthStore();

  const { data: stats, isLoading, error } = useQuery<UserStats>({
    queryKey: ['user-stats'],
    queryFn: () => api.get('/stats').then((r) => r.data),
  });

  if (isLoading) return <LoadingSpinner text="Loading your dashboard..." />;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Failed to load dashboard data. Please try again.
        </p>
        <button onClick={() => window.location.reload()} className="btn-primary text-sm">
          Retry
        </button>
      </div>
    );
  }

  const weakTopics = stats?.categoryBreakdown
    ?.filter((c) => c.totalQuestions > 0)
    ?.sort((a, b) => a.accuracy - b.accuracy)
    ?.slice(0, 3);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Welcome, {user?.name?.split(' ')[0] || 'Doctor'}
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Continue your nephrology learning journey
          </p>
        </div>
        <Link
          to={stats?.dailyQuizCompleted ? '/categories' : '/daily-challenge'}
          className={`btn-teal gap-2 text-sm ${stats?.dailyQuizCompleted ? '' : 'animate-pulse-slow'}`}
        >
          <SparklesIcon className="h-4 w-4" />
          {stats?.dailyQuizCompleted ? 'Practice More' : 'Daily Challenge'}
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Quizzes Taken"
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
          color={stats?.currentStreak && stats.currentStreak >= 3 ? 'amber' : 'primary'}
        />
        <StatsCard
          title="Total Questions"
          value={stats?.totalQuestions ?? 0}
          icon={<TrophyIcon className="h-6 w-6" />}
          color="teal"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Topics to Improve
            </h2>
            <Link
              to="/categories"
              className="flex items-center gap-1 text-xs font-medium text-teal-700 hover:text-teal-600 dark:text-teal-400"
            >
              All Topics <ArrowRightIcon className="h-3 w-3" />
            </Link>
          </div>

          {weakTopics && weakTopics.length > 0 ? (
            <div className="space-y-3">
              {weakTopics.map((topic, i) => (
                <Link
                  key={topic.categoryId}
                  to={`/quiz/category/${topic.categoryId}`}
                  className="block rounded-xl border border-gray-100 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {topic.categoryName}
                    </span>
                    <span className={`text-sm font-bold ${
                      topic.accuracy < 50 ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'
                    }`}>
                      {topic.accuracy}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-gray-100 dark:bg-gray-700">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        topic.accuracy < 50 ? 'bg-red-500' : topic.accuracy < 75 ? 'bg-amber-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${topic.accuracy}%` }}
                    />
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="py-6 text-center text-sm text-gray-500 dark:text-gray-400">
              Take your first quiz to see topic breakdown
            </p>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Quick Actions
            </h2>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <Link
              to="/daily-challenge"
              className="flex flex-col items-center gap-2 rounded-xl border-2 border-teal-100 bg-teal-50 p-5 text-center transition-all hover:border-teal-300 hover:shadow-md dark:border-teal-900/50 dark:bg-teal-900/20 dark:hover:border-teal-700"
            >
              <AcademicCapIcon className="h-8 w-8 text-teal-700 dark:text-teal-400" />
              <span className="text-sm font-semibold text-teal-800 dark:text-teal-300">
                {stats?.dailyQuizCompleted ? 'Completed ✓' : 'Daily Challenge'}
              </span>
              <span className="text-xs text-teal-600 dark:text-teal-400">
                {stats?.dailyQuizCompleted ? 'Come back tomorrow' : 'New case every day'}
              </span>
            </Link>

            <Link
              to="/categories"
              className="flex flex-col items-center gap-2 rounded-xl border-2 border-primary-100 bg-primary-50 p-5 text-center transition-all hover:border-primary-300 hover:shadow-md dark:border-primary-900/50 dark:bg-primary-900/20 dark:hover:border-primary-700"
            >
              <ChartBarIcon className="h-8 w-8 text-primary-700 dark:text-primary-300" />
              <span className="text-sm font-semibold text-primary-800 dark:text-primary-300">
                Practice by Topic
              </span>
              <span className="text-xs text-primary-600 dark:text-primary-400">
                Focus on specific areas
              </span>
            </Link>

            <Link
              to="/leaderboard"
              className="flex flex-col items-center gap-2 rounded-xl border-2 border-amber-100 bg-amber-50 p-5 text-center transition-all hover:border-amber-300 hover:shadow-md dark:border-amber-900/50 dark:bg-amber-900/20 dark:hover:border-amber-700"
            >
              <TrophyIcon className="h-8 w-8 text-amber-700 dark:text-amber-400" />
              <span className="text-sm font-semibold text-amber-800 dark:text-amber-300">
                Leaderboard
              </span>
              <span className="text-xs text-amber-600 dark:text-amber-400">
                See how you rank
              </span>
            </Link>

            <Link
              to="/quiz/practice"
              className="flex flex-col items-center gap-2 rounded-xl border-2 border-gray-200 bg-white p-5 text-center transition-all hover:border-gray-300 hover:shadow-md dark:border-gray-600 dark:bg-gray-800 dark:hover:border-gray-500"
            >
              <FireIcon className="h-8 w-8 text-gray-600 dark:text-gray-300" />
              <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                Quick Quiz
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Random questions
              </span>
            </Link>
          </div>
        </motion.div>
      </div>

      {stats?.recentActivity && stats.recentActivity.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
            Recent Activity
          </h2>
          <div className="overflow-hidden rounded-lg border border-gray-100 dark:border-gray-700">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold uppercase text-gray-500">Date</th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold uppercase text-gray-500">Quizzes</th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold uppercase text-gray-500">Questions</th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold uppercase text-gray-500">Correct</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {stats.recentActivity.slice(-7).reverse().map((day, i) => (
                  <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300">
                      {new Date(day.date).toLocaleDateString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </td>
                    <td className="px-4 py-2.5 text-right text-sm text-gray-700 dark:text-gray-300">{day.quizzesCompleted}</td>
                    <td className="px-4 py-2.5 text-right text-sm text-gray-700 dark:text-gray-300">{day.questionsAnswered}</td>
                    <td className="px-4 py-2.5 text-right text-sm font-medium text-green-600 dark:text-green-400">{day.correctAnswers}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  );
}
