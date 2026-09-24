import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import { unwrapList } from '@/lib/apiMappers';
import type { Chapter } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
  BookOpenIcon,
  ArrowRightIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  PlayCircleIcon,
  AcademicCapIcon,
  FilmIcon,
} from '@heroicons/react/24/outline';

const iconMap: Record<string, React.ElementType> = {
  BeakerIcon: BookOpenIcon,
  CircleStackIcon: AcademicCapIcon,
  ExclamationTriangleIcon: ExclamationTriangleIcon,
  HeartIcon: BookOpenIcon,
  DocumentTextIcon: BookOpenIcon,
  UserGroupIcon: FilmIcon,
};

const chapterGradients = [
  'from-teal-500/10 to-emerald-500/5 border-teal-200 dark:border-teal-800',
  'from-blue-500/10 to-indigo-500/5 border-blue-200 dark:border-blue-800',
  'from-amber-500/10 to-orange-500/5 border-amber-200 dark:border-amber-800',
  'from-rose-500/10 to-pink-500/5 border-rose-200 dark:border-rose-800',
  'from-violet-500/10 to-purple-500/5 border-violet-200 dark:border-violet-800',
  'from-cyan-500/10 to-sky-500/5 border-cyan-200 dark:border-cyan-800',
];

export default function Chapters() {
  const [search, setSearch] = useState('');

  const { data: chapters, isLoading, error } = useQuery<Chapter[]>({
    queryKey: ['chapters'],
    queryFn: () => api.get('/chapters/').then((r) => unwrapList<Chapter>(r.data)),
  });

  const filtered = (chapters || []).filter(
    (c) =>
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.description.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return <LoadingSpinner text="Loading board chapters..." />;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Failed to load chapters</p>
        <button onClick={() => window.location.reload()} className="btn-primary text-sm">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-900 via-primary-800 to-teal-900 p-8 text-white shadow-lg">
        <div className="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-teal-500/20 blur-2xl" />
        <div className="relative">
          <p className="text-xs font-semibold uppercase tracking-widest text-teal-300">Nephrology Board Review</p>
          <h1 className="mt-2 text-3xl font-bold">Chapter-wise MCQs & Animations</h1>
          <p className="mt-2 max-w-2xl text-sm text-teal-100/90">
            Study fast with animated algorithms, then test yourself with board-style questions organized by chapter.
          </p>
          <div className="mt-6 flex flex-wrap gap-4 text-sm">
            <span className="rounded-full bg-white/10 px-3 py-1">{chapters?.length ?? 0} Chapters</span>
            <span className="rounded-full bg-white/10 px-3 py-1">
              {chapters?.reduce((n, c) => n + (c.lesson_count ?? 0), 0) ?? 0} Animations
            </span>
            <span className="rounded-full bg-white/10 px-3 py-1">
              {chapters?.reduce((n, c) => n + (c.question_count ?? 0), 0) ?? 0} MCQs
            </span>
          </div>
        </div>
      </div>

      <div className="relative max-w-md">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search chapters..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field pl-9"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <BookOpenIcon className="h-12 w-12 text-gray-300 dark:text-gray-600" />
          <p className="font-medium text-gray-900 dark:text-gray-100">No chapters found</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((chapter, i) => {
            const Icon = iconMap[chapter.icon] || BookOpenIcon;
            const gradient = chapterGradients[i % chapterGradients.length];
            return (
              <motion.div
                key={chapter.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Link
                  to={`/chapters/${chapter.slug}`}
                  className={`group flex h-full flex-col rounded-2xl border bg-gradient-to-br p-6 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-lg dark:bg-gray-900/50 ${gradient}`}
                >
                  <div className="mb-4 flex items-start justify-between">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/80 text-primary-900 shadow-sm dark:bg-gray-800 dark:text-teal-300">
                      <Icon className="h-6 w-6" />
                    </div>
                    <span className="rounded-full bg-white/60 px-2 py-0.5 text-xs font-bold text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                      Ch.{chapter.order_index}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 group-hover:text-teal-800 dark:group-hover:text-teal-300">
                    {chapter.title}
                  </h3>
                  <p className="mt-2 flex-1 text-sm leading-relaxed text-gray-600 dark:text-gray-400">
                    {chapter.description}
                  </p>
                  <div className="mt-5 flex items-center justify-between border-t border-black/5 pt-4 dark:border-white/10">
                    <div className="flex gap-3 text-xs text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <PlayCircleIcon className="h-3.5 w-3.5" /> {chapter.lesson_count ?? 0}
                      </span>
                      <span className="flex items-center gap-1">
                        <AcademicCapIcon className="h-3.5 w-3.5" /> {chapter.question_count ?? 0}
                      </span>
                    </div>
                    <span className="flex items-center gap-1 text-xs font-semibold text-teal-700 dark:text-teal-400">
                      Explore <ArrowRightIcon className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
                    </span>
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
