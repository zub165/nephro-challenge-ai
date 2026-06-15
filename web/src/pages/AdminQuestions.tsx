import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/axios';
import type { Question, Category } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  CheckCircleIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

interface QuestionFormData {
  text: string;
  choices: { id?: string; text: string }[];
  correctAnswer: string;
  explanation: string;
  categoryId: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

const emptyForm: QuestionFormData = {
  text: '',
  choices: [
    { id: 'a', text: '' },
    { id: 'b', text: '' },
    { id: 'c', text: '' },
    { id: 'd', text: '' },
  ],
  correctAnswer: '',
  explanation: '',
  categoryId: '',
  difficulty: 'medium',
};

export default function AdminQuestions() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<QuestionFormData>(emptyForm);
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-questions', page, search],
    queryFn: () =>
      api
        .get('/admin/questions', { params: { page, limit: 20, search } })
        .then((r) => r.data),
  });

  const { data: categories } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: () => api.get('/categories').then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: QuestionFormData) => api.post('/admin/questions', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-questions'] });
      toast.success('Question created');
      closeForm();
    },
    onError: (err: any) => toast.error(err.response?.data?.message || 'Failed to create'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: QuestionFormData }) =>
      api.put(`/admin/questions/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-questions'] });
      toast.success('Question updated');
      closeForm();
    },
    onError: (err: any) => toast.error(err.response?.data?.message || 'Failed to update'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/admin/questions/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-questions'] });
      toast.success('Question deleted');
    },
    onError: (err: any) => toast.error(err.response?.data?.message || 'Failed to delete'),
  });

  const closeForm = () => {
    setShowForm(false);
    setEditingId(null);
    setForm(emptyForm);
  };

  const openEdit = (q: Question) => {
    setForm({
      text: q.text,
      choices: q.choices.map((c) => ({ id: c.id, text: c.text })),
      correctAnswer: q.correctAnswer,
      explanation: q.explanation,
      categoryId: q.categoryId,
      difficulty: q.difficulty,
    });
    setEditingId(q.id);
    setShowForm(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.text || !form.explanation || !form.categoryId || !form.correctAnswer) {
      toast.error('Please fill in all required fields');
      return;
    }
    if (form.choices.some((c) => !c.text)) {
      toast.error('All choices must have text');
      return;
    }
    if (!form.choices.find((c) => c.id === form.correctAnswer)) {
      toast.error('Correct answer must match one of the choices');
      return;
    }

    if (editingId) {
      updateMutation.mutate({ id: editingId, data: form });
    } else {
      createMutation.mutate(form);
    }
  };

  const questions: Question[] = data?.questions || data?.data || [];
  const totalPages = data?.totalPages || data?.totalPages || 1;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Failed to load questions</p>
        <button onClick={() => window.location.reload()} className="btn-primary text-sm">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Manage Questions
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Create and edit quiz questions
          </p>
        </div>
        <button onClick={() => { setForm(emptyForm); setEditingId(null); setShowForm(true); }} className="btn-primary gap-2 text-sm">
          <PlusIcon className="h-4 w-4" /> New Question
        </button>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search questions..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="input-field pl-9"
          />
        </div>
      </div>

      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <form onSubmit={handleSubmit} className="card space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {editingId ? 'Edit Question' : 'New Question'}
                </h2>
                <button type="button" onClick={closeForm} className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Question Text *
                </label>
                <textarea
                  value={form.text}
                  onChange={(e) => setForm({ ...form, text: e.target.value })}
                  className="input-field min-h-[80px] resize-y"
                  rows={3}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Category *
                  </label>
                  <select
                    value={form.categoryId}
                    onChange={(e) => setForm({ ...form, categoryId: e.target.value })}
                    className="select-field"
                  >
                    <option value="">Select category</option>
                    {categories?.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Difficulty *
                  </label>
                  <select
                    value={form.difficulty}
                    onChange={(e) => setForm({ ...form, difficulty: e.target.value as 'easy' | 'medium' | 'hard' })}
                    className="select-field"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Choices *
                </label>
                <div className="space-y-2">
                  {form.choices.map((choice, i) => {
                    const label = String.fromCharCode(65 + i);
                    return (
                      <div key={choice.id || i} className="flex items-center gap-2">
                        <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                          {label}
                        </span>
                        <input
                          type="text"
                          value={choice.text}
                          onChange={(e) => {
                            const newChoices = [...form.choices];
                            newChoices[i] = { ...newChoices[i], text: e.target.value };
                            setForm({ ...form, choices: newChoices });
                          }}
                          className="input-field flex-1"
                          placeholder={`Choice ${label}`}
                        />
                        <button
                          type="button"
                          onClick={() => {
                            setForm({
                              ...form,
                              correctAnswer: choice.id,
                            });
                          }}
                          className={`rounded-lg px-2.5 py-2 text-xs font-medium transition-colors ${
                            form.correctAnswer === choice.id
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                              : 'bg-gray-100 text-gray-500 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400'
                          }`}
                        >
                          {form.correctAnswer === choice.id ? 'Correct' : 'Correct?'}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Explanation *
                </label>
                <textarea
                  value={form.explanation}
                  onChange={(e) => setForm({ ...form, explanation: e.target.value })}
                  className="input-field min-h-[60px] resize-y"
                  rows={3}
                  placeholder="Explain the correct answer"
                />
              </div>

              <div className="flex justify-end gap-2">
                <button type="button" onClick={closeForm} className="btn-outline text-sm">
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="btn-primary text-sm"
                >
                  {editingId ? 'Update' : 'Create'} Question
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {isLoading ? (
        <LoadingSpinner text="Loading questions..." />
      ) : questions.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <QuestionMarkCircleIcon className="h-12 w-12 text-gray-300 dark:text-gray-600" />
          <p className="font-medium text-gray-900 dark:text-gray-100">No questions found</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {search ? 'Try a different search' : 'Create your first question'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {questions.map((q) => (
            <motion.div
              key={q.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="card flex items-start justify-between gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`badge-${q.difficulty === 'easy' ? 'green' : q.difficulty === 'medium' ? 'amber' : 'red'}`}>
                    {q.difficulty}
                  </span>
                  {q.isAIGenerated && (
                    <span className="badge-blue flex items-center gap-1">
                      <SparklesIcon className="h-3 w-3" /> AI
                    </span>
                  )}
                  {q.aiReviewStatus === 'pending' && (
                    <span className="badge-amber">Pending Review</span>
                  )}
                  {q.category && (
                    <span className="badge-teal">{q.category.name}</span>
                  )}
                </div>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2">
                  {q.text}
                </p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-1">
                  {q.explanation}
                </p>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <button
                  onClick={() => openEdit(q)}
                  className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
                  title="Edit"
                >
                  <PencilSquareIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => {
                    if (window.confirm('Delete this question?')) {
                      deleteMutation.mutate(q.id);
                    }
                  }}
                  className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                  title="Delete"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          ))}

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                    page === p
                      ? 'bg-primary-900 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function QuestionMarkCircleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
    </svg>
  );
}
