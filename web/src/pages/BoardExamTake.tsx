import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/axios';
import LoadingSpinner from '@/components/LoadingSpinner';
import toast from 'react-hot-toast';

type Item = {
  position: number;
  question: {
    question_text?: string;
    case_text?: string;
    choices?: { choice_key: string; choice_text: string }[];
  };
  selected_choice_key?: string | null;
};

export default function BoardExamTake() {
  const { slug, attemptId } = useParams();
  const queryClient = useQueryClient();
  const [index, setIndex] = useState(0);

  const { data, isLoading, error } = useQuery({
    queryKey: ['board-exam-attempt', attemptId],
    queryFn: () => api.get(`/board-exams/attempts/${attemptId}/`).then((r) => r.data),
    refetchInterval: 30000,
  });

  const answer = useMutation({
    mutationFn: ({ position, key }: { position: number; key: string }) =>
      api.put(`/board-exams/attempts/${attemptId}/items/${position}/`, {
        selected_choice_key: key,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['board-exam-attempt', attemptId] }),
    onError: () => toast.error('Could not save answer'),
  });

  const submit = useMutation({
    mutationFn: async () => {
      const { data } = await api.post(`/board-exams/attempts/${attemptId}/submit/`);
      return data;
    },
    onSuccess: (payload) => {
      queryClient.setQueryData(['board-exam-results', attemptId], payload);
    },
    onError: () => toast.error('Could not submit exam'),
  });

  const { data: results } = useQuery({
    queryKey: ['board-exam-results', attemptId],
    queryFn: () => api.get(`/board-exams/attempts/${attemptId}/results/`).then((r) => r.data),
    enabled: false,
  });

  const graded = submit.data || results;
  const items: Item[] = data?.items || [];
  const current = items[index];

  const remaining = data?.remaining_seconds ?? 0;

  if (isLoading) return <LoadingSpinner text="Loading exam..." />;
  if (error) {
    return (
      <div className="py-12 text-center">
        <p className="text-sm text-gray-500">This attempt is not active. Check results or start again.</p>
        <Link to="/board-exams" className="btn-primary mt-4 inline-block text-sm">
          Exams
        </Link>
      </div>
    );
  }

  if (graded) {
    return (
      <div className="card space-y-3">
        <h1 className="text-2xl font-bold">Exam submitted</h1>
        <p className="text-lg">
          Score {graded.correct_count ?? graded.score}/{graded.total_questions}
        </p>
        <Link to="/board-prep" className="btn-primary inline-block text-sm">
          Review plan weak areas
        </Link>
      </div>
    );
  }

  const choices = current?.question?.choices || [];

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div className="flex justify-between text-sm text-gray-500">
        <span>
          {slug} · {index + 1}/{items.length}
        </span>
        <span>{Math.max(0, data?.remaining_seconds ?? 0)}s left</span>
      </div>
      <div className="card space-y-3">
        {current?.question?.case_text && (
          <p className="text-sm text-gray-600 dark:text-gray-300">{current.question.case_text}</p>
        )}
        <p className="font-medium">{current?.question?.question_text}</p>
        <div className="space-y-2">
          {choices.map((choice) => (
            <button
              key={choice.choice_key}
              type="button"
              className={`w-full rounded-xl border px-4 py-3 text-left text-sm ${
                (current.selected_choice_key || '') === choice.choice_key
                  ? 'border-teal-600 bg-teal-50 dark:bg-teal-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
              onClick={() =>
                answer.mutate({ position: current.position, key: choice.choice_key })
              }
            >
              <strong>{choice.choice_key}.</strong> {choice.choice_text}
            </button>
          ))}
        </div>
      </div>
      <div className="flex justify-between">
        <button
          type="button"
          className="btn-outline text-sm"
          disabled={index === 0}
          onClick={() => setIndex((i) => i - 1)}
        >
          Previous
        </button>
        {index < items.length - 1 ? (
          <button type="button" className="btn-primary text-sm" onClick={() => setIndex((i) => i + 1)}>
            Next
          </button>
        ) : (
          <button
            type="button"
            className="btn-primary text-sm"
            onClick={() => submit.mutate()}
            disabled={submit.isPending}
          >
            Submit exam
          </button>
        )}
      </div>
    </div>
  );
}
