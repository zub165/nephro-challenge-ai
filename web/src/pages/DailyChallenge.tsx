import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import type { DailyChallenge as DailyChallengeType } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
  SparklesIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  CalendarDaysIcon,
  ExclamationTriangleIcon,
  FireIcon,
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

export default function DailyChallenge() {
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery<DailyChallengeType>({
    queryKey: ['daily-challenge'],
    queryFn: () => api.get('/daily-challenge').then((r) => r.data),
  });

  const completedCount = data?.questions?.length
    ? data.questions.filter((q) => q.id).length
    : 0;

  if (isLoading) return <LoadingSpinner text="Loading daily challenge..." />;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Unable to load today's challenge</p>
        <button onClick={() => window.location.reload()} className="btn-primary text-sm">Retry</button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Daily Challenge
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {format(new Date(), 'EEEE, MMMM d, yyyy')}
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-xl bg-amber-50 px-4 py-2 dark:bg-amber-900/20">
          <FireIcon className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <span className="text-sm font-bold text-amber-700 dark:text-amber-300">
            Daily Case
          </span>
        </div>
      </div>

      {data?.completed ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card text-center"
        >
          <CheckCircleIcon className="mx-auto h-16 w-16 text-green-500" />
          <h2 className="mt-4 text-xl font-bold text-gray-900 dark:text-gray-100">
            Today's Challenge Complete!
          </h2>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Your score: {data.score ?? 0}/{data.questions?.length ?? 0}
          </p>
          <p className="mt-1 text-sm text-gray-400">
            Come back tomorrow for a new case
          </p>
          <div className="mt-6 flex justify-center">
            <Link to="/dashboard" className="btn-primary">
              Back to Dashboard
            </Link>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="mb-6 flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-500 to-teal-700 shadow-lg">
              <SparklesIcon className="h-8 w-8 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                Today's Clinical Case
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {data?.questions?.length || 5} questions • 
                New case every day
              </p>
            </div>
          </div>

          <p className="mb-6 text-sm leading-relaxed text-gray-600 dark:text-gray-400">
            Test your clinical reasoning with today's curated nephrology case. 
            Each daily challenge covers diagnostic approach, management, and 
            evidence-based decision making.
          </p>

          <div className="mb-6 grid grid-cols-3 gap-3">
            {[
              { label: 'Questions', value: data?.questions?.length || 5 },
              { label: 'Time', value: '~15 min' },
              { label: 'Difficulty', value: 'Mixed' },
            ].map((item) => (
              <div key={item.label} className="rounded-xl bg-gray-50 p-3 text-center dark:bg-gray-800">
                <p className="text-lg font-bold text-primary-900 dark:text-teal-300">{item.value}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{item.label}</p>
              </div>
            ))}
          </div>

          <button
            onClick={() => navigate('/quiz/daily')}
            className="btn-teal w-full gap-2 py-3 text-base"
          >
            Start Challenge <ArrowRightIcon className="h-4 w-4" />
          </button>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="flex items-start gap-3">
          <CalendarDaysIcon className="h-5 w-5 flex-shrink-0 text-gray-400" />
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              What is the Daily Challenge?
            </h3>
            <p className="mt-1 text-xs leading-relaxed text-gray-500 dark:text-gray-400">
              Each day, we present a curated clinical case with multiple-choice 
              questions designed to test and expand your nephrology knowledge. 
              Cases cover a wide range of topics including glomerular diseases, 
              electrolyte disorders, acid-base balance, hypertension, dialysis, 
              and transplant medicine.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
