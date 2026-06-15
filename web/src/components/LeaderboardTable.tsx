import type { LeaderboardEntry } from '@/types';
import { motion } from 'framer-motion';
import { TrophyIcon } from '@heroicons/react/24/solid';

interface LeaderboardTableProps {
  entries: LeaderboardEntry[];
  isLoading?: boolean;
}

const rankColors = ['text-amber-500', 'text-gray-400', 'text-amber-700'];

export default function LeaderboardTable({ entries, isLoading }: LeaderboardTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-16 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />
        ))}
      </div>
    );
  }

  if (!entries.length) {
    return (
      <div className="flex flex-col items-center gap-3 py-12 text-center">
        <TrophyIcon className="h-12 w-12 text-gray-300 dark:text-gray-600" />
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
          No entries yet. Be the first to take a quiz!
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Rank
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Name
            </th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Score
            </th>
            <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 sm:table-cell">
              Accuracy
            </th>
            <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 md:table-cell">
              Quizzes
            </th>
            <th className="hidden px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 md:table-cell">
              Streak
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-900">
          {entries.map((entry, index) => (
            <motion.tr
              key={entry.userId}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <td className="whitespace-nowrap px-4 py-3">
                <div className="flex items-center gap-2">
                  {index < 3 ? (
                    <TrophyIcon className={`h-5 w-5 ${rankColors[index]}`} />
                  ) : (
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-500 dark:bg-gray-700 dark:text-gray-400">
                      {entry.rank}
                    </span>
                  )}
                </div>
              </td>
              <td className="whitespace-nowrap px-4 py-3">
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {entry.name}
                </span>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-right">
                <span className="text-sm font-bold text-primary-900 dark:text-teal-300">
                  {entry.score.toLocaleString()}
                </span>
              </td>
              <td className="hidden whitespace-nowrap px-4 py-3 text-right sm:table-cell">
                <span className={`text-sm font-medium ${
                  entry.accuracy >= 80 ? 'text-green-600 dark:text-green-400' :
                  entry.accuracy >= 60 ? 'text-amber-600 dark:text-amber-400' :
                  'text-red-600 dark:text-red-400'
                }`}>
                  {entry.accuracy}%
                </span>
              </td>
              <td className="hidden whitespace-nowrap px-4 py-3 text-right md:table-cell">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {entry.quizCount}
                </span>
              </td>
              <td className="hidden whitespace-nowrap px-4 py-3 text-right md:table-cell">
                <span className="inline-flex items-center gap-1 text-sm font-medium text-amber-600 dark:text-amber-400">
                  {entry.streak > 0 ? (
                    <>🔥 {entry.streak}</>
                  ) : (
                    '—'
                  )}
                </span>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
