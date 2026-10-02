import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/axios';
import LoadingSpinner from '@/components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  AcademicCapIcon,
  BookOpenIcon,
  ClockIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

type PlanDay = {
  day: number;
  focus: string;
  high_yield: string[];
  chapter_slugs: string[];
  mixed?: boolean;
  review_only?: boolean;
  question_target: number;
  morning_questions: number;
  evening: string;
};

type PlanPayload = {
  exam_date: string | null;
  work_weekdays: number[];
  day_number: number;
  days_until_exam: number | null;
  is_workday: boolean;
  today_answered: number;
  questions_in_plan: number;
  target_min: number;
  target_max: number;
  classification: { total: number; know: number; guessed: number; wrong: number };
  today_session: PlanDay;
  days: PlanDay[];
  method: string;
};

type ReviewItem = {
  id: string;
  question_id: string;
  tag: string;
  question_text: string;
  explanation: string;
  clinical_pearl: string;
  chapter_title: string;
};

type FactItem = {
  id: string;
  kind: string;
  text: string;
  created_at: string;
};

const WEEKDAYS = [
  { id: 1, label: 'Mon' },
  { id: 2, label: 'Tue' },
  { id: 3, label: 'Wed' },
  { id: 4, label: 'Thu' },
  { id: 5, label: 'Fri' },
  { id: 6, label: 'Sat' },
  { id: 7, label: 'Sun' },
];

export default function BoardPrep() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<'today' | 'calendar' | 'review' | 'sheet'>('today');
  const [examDate, setExamDate] = useState('');
  const [workdays, setWorkdays] = useState<number[]>([1, 2, 3, 4, 5]);
  const [reviewTag, setReviewTag] = useState('review');
  const [factText, setFactText] = useState('');
  const [factKind, setFactKind] = useState('formula');

  const { data: plan, isLoading } = useQuery<PlanPayload>({
    queryKey: ['board-prep-plan'],
    queryFn: () => api.get('/board-prep/plan/').then((r) => r.data),
  });

  const { data: review } = useQuery({
    queryKey: ['board-prep-review', reviewTag],
    queryFn: () =>
      api.get('/board-prep/review-queue/', { params: { tag: reviewTag } }).then((r) => r.data),
    enabled: tab === 'review',
  });

  const { data: sheet } = useQuery({
    queryKey: ['board-prep-last48'],
    queryFn: () => api.get('/board-prep/last-48h/').then((r) => r.data),
    enabled: tab === 'sheet',
  });

  const savePlan = useMutation({
    mutationFn: () =>
      api.post('/board-prep/plan/', {
        exam_date: examDate || undefined,
        work_weekdays: workdays,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['board-prep-plan'] });
      queryClient.invalidateQueries({ queryKey: ['user-stats'] });
      toast.success('25-day plan saved');
    },
    onError: () => toast.error('Could not save plan'),
  });

  const addFact = useMutation({
    mutationFn: () => api.post('/board-prep/last-48h/', { kind: factKind, text: factText }),
    onSuccess: () => {
      setFactText('');
      queryClient.invalidateQueries({ queryKey: ['board-prep-last48'] });
    },
  });

  const deleteFact = useMutation({
    mutationFn: (id: string) => api.delete(`/board-prep/last-48h/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['board-prep-last48'] }),
  });

  const day = plan?.today_session;
  const remaining = Math.max(0, (day?.question_target ?? 25) - (plan?.today_answered ?? 0));

  const progressPct = useMemo(() => {
    if (!plan) return 0;
    return Math.min(100, Math.round((plan.questions_in_plan / plan.target_max) * 100));
  }, [plan]);

  if (isLoading || !plan) return <LoadingSpinner text="Loading 25-day board plan..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">25-Day Board Plan</h1>
          <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">{plan.method}</p>
        </div>
        <Link
          to={`/quiz/board-prep?day=${plan.day_number}&limit=${Math.min(20, Math.max(5, remaining || 18))}`}
          className="btn-primary gap-2"
        >
          <AcademicCapIcon className="h-4 w-4" /> Today’s questions
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Plan day" value={`${plan.day_number}/25`} />
        <Stat
          label="Days until exam"
          value={plan.days_until_exam == null ? 'Set exam date' : String(plan.days_until_exam)}
        />
        <Stat label="Today" value={`${plan.today_answered}/${day?.question_target ?? 0} Q`} />
        <Stat
          label="Plan total"
          value={`${plan.questions_in_plan} / ${plan.target_min}–${plan.target_max}`}
        />
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-2 bg-teal-600" style={{ width: `${progressPct}%` }} />
      </div>
      <p className="text-xs text-gray-500">
        Know {plan.classification.know} · Guessed {plan.classification.guessed} · Wrong{' '}
        {plan.classification.wrong}
        {plan.is_workday ? ' · Workday (AM 15–20 Q, PM review)' : ' · Day off (60–100 Q)'}
      </p>

      <form
        className="card flex flex-wrap items-end gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          savePlan.mutate();
        }}
      >
        <label className="text-sm">
          <span className="mb-1 block text-gray-500">Exam date</span>
          <input
            type="date"
            className="input-field"
            value={examDate || plan.exam_date || ''}
            onChange={(e) => setExamDate(e.target.value)}
          />
        </label>
        <div className="text-sm">
          <span className="mb-1 block text-gray-500">Workdays (7 AM–7 PM)</span>
          <div className="flex flex-wrap gap-1">
            {WEEKDAYS.map((d) => {
              const on = workdays.includes(d.id);
              return (
                <button
                  key={d.id}
                  type="button"
                  onClick={() =>
                    setWorkdays((prev) =>
                      prev.includes(d.id) ? prev.filter((x) => x !== d.id) : [...prev, d.id].sort()
                    )
                  }
                  className={`rounded-lg px-2 py-1 text-xs font-medium ${
                    on
                      ? 'bg-teal-700 text-white'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300'
                  }`}
                >
                  {d.label}
                </button>
              );
            })}
          </div>
        </div>
        <button type="submit" className="btn-teal text-sm" disabled={savePlan.isPending}>
          Save calendar
        </button>
      </form>

      <div className="flex flex-wrap gap-2">
        {(
          [
            ['today', 'Today'],
            ['calendar', 'Day 1–25'],
            ['review', 'Wrong / Guessed'],
            ['sheet', 'Last 48 Hours'],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
              tab === id
                ? 'bg-primary-900 text-white'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'today' && day && (
        <div className="card space-y-3">
          <h2 className="text-lg font-semibold">
            Day {day.day}: {day.focus}
          </h2>
          <p className="text-sm text-gray-500">{day.evening}</p>
          <div className="flex flex-wrap gap-2">
            {day.high_yield.map((item) => (
              <span
                key={item}
                className="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-800 dark:bg-teal-900/30 dark:text-teal-200"
              >
                {item}
              </span>
            ))}
          </div>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              to={`/quiz/board-prep?day=${day.day}&limit=${day.morning_questions}`}
              className="btn-primary text-sm"
            >
              Morning block ({day.morning_questions} Q)
            </Link>
            <Link to="/board-prep" onClick={() => setTab('review')} className="btn-outline text-sm">
              Review incorrect + guessed
            </Link>
            <Link to="/board-exams" className="btn-outline gap-2 text-sm">
              <ClockIcon className="h-4 w-4" /> Timed simulation
            </Link>
          </div>
        </div>
      )}

      {tab === 'calendar' && (
        <div className="grid gap-3 md:grid-cols-2">
          {plan.days.map((item) => (
            <Link
              key={item.day}
              to={`/quiz/board-prep?day=${item.day}&limit=${item.morning_questions}`}
              className={`card block hover:border-teal-400 ${
                item.day === plan.day_number ? 'ring-2 ring-teal-600' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-teal-700">Day {item.day}</span>
                {item.review_only && <span className="text-xs text-amber-600">Review only</span>}
              </div>
              <p className="mt-1 font-semibold text-gray-900 dark:text-gray-100">{item.focus}</p>
              <p className="mt-1 text-xs text-gray-500">{item.high_yield.join(' · ')}</p>
            </Link>
          ))}
        </div>
      )}

      {tab === 'review' && (
        <div className="space-y-3">
          <div className="flex gap-2">
            {['review', 'wrong', 'guessed'].map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => setReviewTag(tag)}
                className={`rounded-lg px-3 py-1 text-sm ${
                  reviewTag === tag ? 'bg-amber-600 text-white' : 'bg-gray-100 dark:bg-gray-800'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
          {(review?.items as ReviewItem[] | undefined)?.length ? (
            (review.items as ReviewItem[]).map((item) => (
              <div key={item.id} className="card space-y-2">
                <p className="text-xs uppercase text-gray-400">
                  {item.tag} · {item.chapter_title}
                </p>
                <p className="text-sm font-medium">{item.question_text}</p>
                {item.clinical_pearl && (
                  <p className="text-sm text-teal-800 dark:text-teal-200">{item.clinical_pearl}</p>
                )}
                <p className="text-sm text-gray-600 dark:text-gray-300">{item.explanation}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">No items yet. Tag questions Know / Guessed after each stem.</p>
          )}
        </div>
      )}

      {tab === 'sheet' && (
        <div className="space-y-4">
          <form
            className="card flex flex-wrap gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              if (factText.trim()) addFact.mutate();
            }}
          >
            <select
              className="input-field w-40"
              value={factKind}
              onChange={(e) => setFactKind(e.target.value)}
            >
              {['formula', 'biopsy', 'toxicity', 'electrolyte', 'dialysis', 'transplant', 'pearl', 'miss'].map(
                (k) => (
                  <option key={k} value={k}>
                    {k}
                  </option>
                )
              )}
            </select>
            <input
              className="input-field min-w-[16rem] flex-1"
              placeholder="Formula, biopsy pattern, toxicity…"
              value={factText}
              onChange={(e) => setFactText(e.target.value)}
            />
            <button type="submit" className="btn-teal gap-1 text-sm">
              <PlusIcon className="h-4 w-4" /> Add
            </button>
          </form>
          {(sheet?.items as FactItem[] | undefined)?.map((fact) => (
            <div key={fact.id} className="card flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase text-gray-400">{fact.kind}</p>
                <p className="text-sm">{fact.text}</p>
              </div>
              <button type="button" onClick={() => deleteFact.mutate(fact.id)} aria-label="Delete">
                <TrashIcon className="h-4 w-4 text-gray-400" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2 text-sm text-gray-500">
        <BookOpenIcon className="h-4 w-4" />
        Review quality beats hitting 1,200–1,500 if you are exhausted after a shift.
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="card">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="mt-1 text-xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
    </div>
  );
}
