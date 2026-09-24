import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import type { Chapter } from '@/types';
import type { PearlItem } from '@/components/PearlCard';
import PearlCard from '@/components/PearlCard';
import { formatDuration } from '@/lib/apiMappers';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
  ArrowLeftIcon,
  PlayCircleIcon,
  AcademicCapIcon,
  ArrowRightIcon,
  ClockIcon,
  FilmIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';

interface PearlsResponse {
  chapters: { chapter: { slug: string }; pearls: PearlItem[]; count: number }[];
  total: number;
}

export default function ChapterDetail() {
  const { slug } = useParams<{ slug: string }>();

  const { data: chapter, isLoading } = useQuery<Chapter>({
    queryKey: ['chapter', slug],
    queryFn: () => api.get(`/chapters/${slug}/`).then((r) => r.data),
    enabled: !!slug,
  });

  const { data: pearlsData } = useQuery<PearlsResponse>({
    queryKey: ['board-pearls', slug],
    queryFn: () => api.get('/pearls/', { params: { chapter: slug } }).then((r) => r.data),
    enabled: !!slug,
  });

  const pearls = pearlsData?.chapters[0]?.pearls ?? [];

  if (isLoading) return <LoadingSpinner text="Loading chapter..." />;
  if (!chapter) {
    return (
      <div className="py-20 text-center">
        <p className="text-gray-500">Chapter not found</p>
        <Link to="/chapters" className="btn-primary mt-4 inline-flex text-sm">Back to Chapters</Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <Link to="/chapters" className="mb-4 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-teal-700 dark:hover:text-teal-400">
          <ArrowLeftIcon className="h-4 w-4" /> All Chapters
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{chapter.title}</h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-500 dark:text-gray-400">{chapter.description}</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link to={`/quiz/chapter/${chapter.id}`} className="btn-teal gap-2 text-sm">
            <AcademicCapIcon className="h-4 w-4" /> Start Chapter Quiz
          </Link>
          <Link to={`/pearls?chapter=${chapter.slug}`} className="btn-outline gap-2 text-sm border-amber-300 text-amber-800 hover:bg-amber-50 dark:border-amber-700 dark:text-amber-300">
            <LightBulbIcon className="h-4 w-4" /> All Pearls
          </Link>
        </div>
      </div>

      {pearls.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-amber-200 bg-amber-50/30 p-5 dark:border-amber-900/50 dark:bg-amber-950/20"
        >
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <LightBulbIcon className="h-6 w-6 text-amber-600" />
              <h2 className="text-lg font-bold text-gray-900 dark:text-amber-100">Board Examination Pearls</h2>
            </div>
            <span className="rounded-full bg-amber-500/20 px-2.5 py-0.5 text-xs font-bold text-amber-800 dark:text-amber-200">
              {pearls.length} high-yield
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {pearls.slice(0, 4).map((p, i) => (
              <PearlCard key={`${p.topic}-${i}`} item={p} compact />
            ))}
          </div>
          {pearls.length > 4 && (
            <Link to="/pearls" className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-amber-800 dark:text-amber-300">
              View all {pearls.length} pearls <ArrowRightIcon className="h-3 w-3" />
            </Link>
          )}
        </motion.section>
      )}

      <div className="space-y-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Topics & Animations</h2>
        {(chapter.topics || []).map((topic, ti) => (
          <motion.div
            key={topic.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: ti * 0.08 }}
            className="card"
          >
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{topic.title}</h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{topic.description}</p>
              </div>
              <Link
                to={`/quiz/chapter/${chapter.id}?topic=${topic.id}`}
                className="hidden items-center gap-1 text-xs font-medium text-teal-700 hover:text-teal-600 dark:text-teal-400 sm:flex"
              >
                Practice MCQs <ArrowRightIcon className="h-3 w-3" />
              </Link>
            </div>

            {(topic.lessons || []).length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {(topic.lessons || []).map((lesson) => (
                  <Link
                    key={lesson.id}
                    to={`/lessons/${lesson.id}`}
                    className="group flex gap-4 rounded-xl border border-gray-100 p-4 transition-all hover:border-teal-300 hover:bg-teal-50/50 dark:border-gray-700 dark:hover:border-teal-700 dark:hover:bg-teal-900/10"
                  >
                    <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-teal-600 to-primary-800 text-white shadow-md">
                      {lesson.lesson_type === 'animation' ? (
                        <FilmIcon className="h-7 w-7" />
                      ) : (
                        <PlayCircleIcon className="h-7 w-7" />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-semibold uppercase tracking-wide text-teal-700 dark:text-teal-400">
                        {lesson.lesson_type}
                      </p>
                      <h4 className="mt-0.5 truncate font-semibold text-gray-900 group-hover:text-teal-800 dark:text-gray-100 dark:group-hover:text-teal-300">
                        {lesson.title}
                      </h4>
                      <p className="mt-1 line-clamp-2 text-xs text-gray-500 dark:text-gray-400">{lesson.summary}</p>
                      {lesson.duration_seconds > 0 && (
                        <p className="mt-2 flex items-center gap-1 text-xs text-gray-400">
                          <ClockIcon className="h-3 w-3" /> {formatDuration(lesson.duration_seconds)}
                        </p>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400">No lessons yet for this topic.</p>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
