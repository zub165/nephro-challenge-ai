import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import type { Question } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  SparklesIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

export default function AdminAIGenerated() {
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<Question | null>(null);
  const [tab, setTab] = useState<'pending' | 'approved' | 'rejected'>('pending');

  const { data, isLoading, error } = useQuery<Question[]>({
    queryKey: ['admin-ai-generated', tab],
    queryFn: () =>
      api
        .get('/admin/questions/ai-generated', { params: { status: tab } })
        .then((r) => r.data),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) =>
      api.put(`/admin/questions/${id}/review`, { aiReviewStatus: 'approved' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-ai-generated'] });
      toast.success('Question approved');
      setSelected(null);
    },
    onError: () => toast.error('Failed to approve'),
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) =>
      api.put(`/admin/questions/${id}/review`, { aiReviewStatus: 'rejected' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-ai-generated'] });
      toast.success('Question rejected');
      setSelected(null);
    },
    onError: () => toast.error('Failed to reject'),
  });

  const questions = data || [];

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Failed to load AI-generated questions
        </p>
        <button onClick={() => window.location.reload()} className="btn-primary text-sm">
          Retry
        </button>
      </div>
    );
  }

  const tabs = [
    {
      key: 'pending' as const,
      label: 'Pending Review',
      count: questions.filter((q) => q.aiReviewStatus === 'pending').length,
    },
    { key: 'approved' as const, label: 'Approved' },
    { key: 'rejected' as const, label: 'Rejected' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          AI-Generated Questions
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Review and approve AI-generated medical questions
        </p>
      </div>

      <div className="flex gap-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => { setTab(t.key); setSelected(null); }}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.key
                ? 'bg-primary-900 text-white dark:bg-teal-800'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
            }`}
          >
            {t.label}
            {t.count !== undefined && (
              <span className="ml-1.5 rounded-full bg-white/20 px-1.5 py-0.5 text-xs">
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {isLoading ? (
        <LoadingSpinner text="Loading AI-generated questions..." />
      ) : questions.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <SparklesIcon className="h-12 w-12 text-gray-300 dark:text-gray-600" />
          <p className="font-medium text-gray-900 dark:text-gray-100">
            {tab === 'pending'
              ? 'No pending reviews'
              : tab === 'approved'
                ? 'No approved questions'
                : 'No rejected questions'}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {tab === 'pending' &&
              'AI-generated questions awaiting your review will appear here'}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3">
            {questions.map((q, i) => (
              <motion.div
                key={q.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                onClick={() => setSelected(q)}
                className={`card cursor-pointer transition-all ${
                  selected?.id === q.id
                    ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800'
                    : 'hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="mb-1 flex items-center gap-2">
                      <SparklesIcon className="h-3.5 w-3.5 text-blue-500" />
                      <span
                        className={`badge-${
                          q.difficulty === 'easy'
                            ? 'green'
                            : q.difficulty === 'medium'
                              ? 'amber'
                              : 'red'
                        }`}
                      >
                        {q.difficulty}
                      </span>
                      {q.category && (
                        <span className="badge-teal">{q.category.name}</span>
                      )}
                    </div>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2">
                      {q.text}
                    </p>
                  </div>
                  {q.aiReviewStatus === 'pending' && (
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          approveMutation.mutate(q.id);
                        }}
                        className="rounded-lg p-1.5 text-green-600 transition-colors hover:bg-green-50 dark:hover:bg-green-900/20"
                        title="Approve"
                      >
                        <CheckCircleIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          rejectMutation.mutate(q.id);
                        }}
                        className="rounded-lg p-1.5 text-red-600 transition-colors hover:bg-red-50 dark:hover:bg-red-900/20"
                        title="Reject"
                      >
                        <XCircleIcon className="h-5 w-5" />
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>

          <div>
            {selected ? (
              <motion.div
                key={selected.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="card sticky top-20"
              >
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Question Details
                  </h2>
                  <span
                    className={`badge-${
                      selected.difficulty === 'easy'
                        ? 'green'
                        : selected.difficulty === 'medium'
                          ? 'amber'
                          : 'red'
                    }`}
                  >
                    {selected.difficulty}
                  </span>
                </div>

                <p className="mb-6 text-sm leading-relaxed text-gray-900 dark:text-gray-100">
                  {selected.text}
                </p>

                <div className="mb-6 space-y-2">
                  {selected.choices.map((c) => {
                    const isCorrect = c.id === selected.correctAnswer;
                    return (
                      <div
                        key={c.id}
                        className={`flex items-center gap-3 rounded-xl border-2 p-3 ${
                          isCorrect
                            ? 'border-green-500 bg-green-50 dark:bg-green-900/30'
                            : 'border-gray-200 dark:border-gray-600'
                        }`}
                      >
                        <span
                          className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
                            isCorrect
                              ? 'bg-green-500 text-white'
                              : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                          }`}
                        >
                          {String.fromCharCode(
                            65 + selected.choices.indexOf(c)
                          )}
                        </span>
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {c.text}
                        </span>
                        {isCorrect && (
                          <CheckCircleIcon className="ml-auto h-5 w-5 text-green-600 dark:text-green-400" />
                        )}
                      </div>
                    );
                  })}
                </div>

                <div className="mb-6 rounded-xl bg-blue-50 p-4 dark:bg-blue-900/20">
                  <p className="text-xs font-semibold uppercase tracking-wider text-blue-700 dark:text-blue-300">
                    Explanation
                  </p>
                  <p className="mt-1 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                    {selected.explanation}
                  </p>
                </div>

                {selected.aiReviewStatus === 'pending' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => approveMutation.mutate(selected.id)}
                      disabled={approveMutation.isPending}
                      className="btn-teal flex-1 gap-2 text-sm"
                    >
                      <CheckCircleIcon className="h-4 w-4" /> Approve
                    </button>
                    <button
                      onClick={() => rejectMutation.mutate(selected.id)}
                      disabled={rejectMutation.isPending}
                      className="btn-danger flex-1 gap-2 text-sm"
                    >
                      <XCircleIcon className="h-4 w-4" /> Reject
                    </button>
                  </div>
                )}

                {selected.aiReviewStatus === 'approved' && (
                  <div className="rounded-xl bg-green-50 p-3 text-center text-sm font-medium text-green-700 dark:bg-green-900/30 dark:text-green-300">
                    ✓ Approved
                  </div>
                )}

                {selected.aiReviewStatus === 'rejected' && (
                  <div className="rounded-xl bg-red-50 p-3 text-center text-sm font-medium text-red-700 dark:bg-red-900/30 dark:text-red-300">
                    ✕ Rejected
                  </div>
                )}
              </motion.div>
            ) : (
              <div className="flex flex-col items-center gap-3 py-20 text-center">
                <EyeIcon className="h-12 w-12 text-gray-300 dark:text-gray-600" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Select a question to review
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function EyeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
      />
    </svg>
  );
}
