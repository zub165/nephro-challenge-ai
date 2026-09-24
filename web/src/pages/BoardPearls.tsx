import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import PearlCard, { type PearlItem } from '@/components/PearlCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
  LightBulbIcon,
  AcademicCapIcon,
  BookOpenIcon,
  ArrowRightIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface PearlChapterGroup {
  chapter: { id: string; title: string; slug: string; order_index: number };
  pearls: PearlItem[];
  count: number;
}

interface PearlsResponse {
  chapters: PearlChapterGroup[];
  total: number;
}

const TAB_LABELS: Record<string, string> = {
  'acid-base-disorders': 'Acid-Base',
  electrolytes: 'Na & K',
  aki: 'AKI & ICU',
  ckd: 'CKD',
  'glomerular-diseases': 'Glomerular',
  dialysis: 'Dialysis',
  hypertension: 'HTN',
  transplantation: 'Transplant',
};

export default function BoardPearls() {
  const [activeSlug, setActiveSlug] = useState<string>('all');

  const { data, isLoading, error } = useQuery<PearlsResponse>({
    queryKey: ['board-pearls'],
    queryFn: () => api.get('/pearls/').then((r) => r.data),
  });

  const activePearls = useMemo(() => {
    if (!data) return [];
    if (activeSlug === 'all') {
      return data.chapters.flatMap((c) =>
        c.pearls.map((p) => ({ ...p, chapterTitle: c.chapter.title, chapterSlug: c.chapter.slug }))
      );
    }
    const group = data.chapters.find((c) => c.chapter.slug === activeSlug);
    return (group?.pearls ?? []).map((p) => ({
      ...p,
      chapterTitle: group?.chapter.title,
      chapterSlug: group?.chapter.slug,
    }));
  }, [data, activeSlug]);

  if (isLoading) return <LoadingSpinner text="Loading board pearls..." />;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500">Could not load board pearls</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-600 via-amber-700 to-primary-900 p-8 text-white shadow-lg">
        <div className="absolute -right-10 -top-10 h-48 w-48 rounded-full bg-yellow-400/20 blur-3xl" />
        <div className="relative flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-amber-200">High-Yield Review</p>
            <h1 className="mt-2 flex items-center gap-3 text-3xl font-bold">
              <LightBulbIcon className="h-9 w-9 text-yellow-300" />
              Board Examination Pearls
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-amber-100/90">
              Curated mnemonics, algorithms, and one-liners for nephrology boards. Includes pearls from MCQs and your saved My Book notes.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-sm">
            <span className="rounded-full bg-white/15 px-3 py-1 font-semibold">{data?.total ?? 0} pearls</span>
            <span className="rounded-full bg-white/15 px-3 py-1">{data?.chapters.length ?? 0} chapters</span>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setActiveSlug('all')}
          className={`rounded-lg px-3 py-2 text-xs font-semibold sm:text-sm ${
            activeSlug === 'all'
              ? 'bg-amber-600 text-white shadow-md'
              : 'bg-primary-900 text-white/90 hover:bg-primary-800'
          }`}
        >
          All ({data?.total ?? 0})
        </button>
        {(data?.chapters ?? []).map((g) => (
          <button
            key={g.chapter.slug}
            type="button"
            onClick={() => setActiveSlug(g.chapter.slug)}
            className={`rounded-lg px-3 py-2 text-xs font-semibold sm:text-sm ${
              activeSlug === g.chapter.slug
                ? 'bg-amber-600 text-white shadow-md'
                : 'bg-primary-900 text-white/90 hover:bg-primary-800'
            }`}
          >
            {TAB_LABELS[g.chapter.slug] ?? g.chapter.title} ({g.count})
          </button>
        ))}
      </div>

      {activePearls.length === 0 ? (
        <div className="card py-16 text-center">
          <LightBulbIcon className="mx-auto h-12 w-12 text-amber-300" />
          <p className="mt-4 font-medium text-gray-900 dark:text-gray-100">No pearls in this section yet</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {activePearls.map((item, i) => (
            <motion.div
              key={`${item.chapterSlug}-${item.topic}-${i}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              {activeSlug === 'all' && item.chapterTitle && (
                <p className="mb-1.5 text-xs font-semibold text-teal-700 dark:text-teal-400">{item.chapterTitle}</p>
              )}
              <PearlCard item={item} />
            </motion.div>
          ))}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <Link
          to="/chapters"
          className="card flex items-center gap-3 transition-all hover:border-teal-300 hover:shadow-md"
        >
          <BookOpenIcon className="h-8 w-8 text-teal-700 dark:text-teal-400" />
          <div>
            <p className="font-semibold text-gray-900 dark:text-gray-100">Chapters</p>
            <p className="text-xs text-gray-500">Animations + topic MCQs</p>
          </div>
        </Link>
        <Link
          to="/notes"
          className="card flex items-center gap-3 transition-all hover:border-amber-300 hover:shadow-md"
        >
          <LightBulbIcon className="h-8 w-8 text-amber-600" />
          <div>
            <p className="font-semibold text-gray-900 dark:text-gray-100">My Book</p>
            <p className="text-xs text-gray-500">Short notes appear here as pearls</p>
          </div>
        </Link>
        <Link
          to="/categories"
          className="card flex items-center gap-3 transition-all hover:border-primary-300 hover:shadow-md"
        >
          <AcademicCapIcon className="h-8 w-8 text-primary-700 dark:text-primary-400" />
          <div>
            <p className="font-semibold text-gray-900 dark:text-gray-100">Practice MCQs</p>
            <p className="text-xs text-gray-500">Test yourself <ArrowRightIcon className="inline h-3 w-3" /></p>
          </div>
        </Link>
      </div>
    </div>
  );
}
