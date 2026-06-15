import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import type { LeaderboardEntry } from '@/types';
import LeaderboardTable from '@/components/LeaderboardTable';
import LoadingSpinner from '@/components/LoadingSpinner';
import { TrophyIcon } from '@heroicons/react/24/outline';

type Period = 'all' | 'weekly' | 'monthly';

export default function Leaderboard() {
  const [period, setPeriod] = useState<Period>('all');

  const { data, isLoading, error } = useQuery<LeaderboardEntry[]>({
    queryKey: ['leaderboard', period],
    queryFn: () =>
      api.get('/leaderboard', { params: { period } }).then((r) => r.data),
  });

  const periods: { key: Period; label: string }[] = [
    { key: 'weekly', label: 'This Week' },
    { key: 'monthly', label: 'This Month' },
    { key: 'all', label: 'All Time' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Leaderboard
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Top performers in nephrology
        </p>
      </div>

      <div className="flex gap-2">
        {periods.map((p) => (
          <button
            key={p.key}
            onClick={() => setPeriod(p.key)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              period === p.key
                ? 'bg-primary-900 text-white dark:bg-teal-800'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <LoadingSpinner text="Loading leaderboard..." />
      ) : error ? (
        <div className="flex flex-col items-center gap-4 py-20 text-center">
          <TrophyIcon className="h-12 w-12 text-gray-300 dark:text-gray-600" />
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Unable to load leaderboard
          </p>
          <button onClick={() => window.location.reload()} className="btn-primary text-sm">
            Retry
          </button>
        </div>
      ) : (
        <LeaderboardTable entries={data || []} />
      )}
    </div>
  );
}
