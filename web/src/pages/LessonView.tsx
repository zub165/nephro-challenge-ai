import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import type { Lesson, Topic } from '@/types';
import { formatDuration } from '@/lib/apiMappers';
import { resolveMedicalAssetUrl } from '@/lib/animationUtils';
import LoadingSpinner from '@/components/LoadingSpinner';
import LessonAnimation from '@/components/LessonAnimation';
import {
  ArrowLeftIcon,
  AcademicCapIcon,
  FilmIcon,
  LightBulbIcon,
  PhotoIcon,
  PresentationChartBarIcon,
} from '@heroicons/react/24/outline';

interface LessonDetail extends Lesson {
  topic?: Topic & { chapter?: { id: string; title: string; slug: string } };
}

export default function LessonView() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const [showInteractive, setShowInteractive] = useState(false);

  const { data: lesson, isLoading } = useQuery<LessonDetail>({
    queryKey: ['lesson', lessonId],
    queryFn: () => api.get(`/lessons/${lessonId}/`).then((r) => r.data),
    enabled: !!lessonId,
  });

  if (isLoading) return <LoadingSpinner text="Loading lesson..." />;

  if (!lesson) {
    return (
      <div className="py-20 text-center">
        <p className="text-gray-500">Lesson not found</p>
        <Link to="/chapters" className="btn-primary mt-4 inline-flex text-sm">Back to Chapters</Link>
      </div>
    );
  }

  const chapter = lesson.topic?.chapter;
  const imageUrl = resolveMedicalAssetUrl(lesson.image_url ?? '');
  const interactiveUrl = resolveMedicalAssetUrl(lesson.interactive_url ?? '');

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        {chapter && (
          <Link
            to={`/chapters/${chapter.slug}`}
            className="mb-4 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-teal-700 dark:hover:text-teal-400"
          >
            <ArrowLeftIcon className="h-4 w-4" /> {chapter.title}
          </Link>
        )}
        <div className="flex items-start gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-800 text-white">
            <FilmIcon className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-teal-700 dark:text-teal-400">
              {lesson.lesson_type} · {lesson.topic?.title}
            </p>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{lesson.title}</h1>
            {lesson.duration_seconds > 0 && (
              <p className="mt-1 text-sm text-gray-500">{formatDuration(lesson.duration_seconds)}</p>
            )}
          </div>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="overflow-hidden rounded-2xl border border-gray-200 shadow-xl dark:border-gray-700"
      >
        {lesson.lesson_type === 'animation' && lesson.animation_url ? (
          <LessonAnimation
            animationUrl={lesson.animation_url}
            fallbackTitle={lesson.title}
            fallbackSummary={lesson.summary}
          />
        ) : imageUrl ? (
          <img
            src={imageUrl}
            alt={lesson.title}
            loading="lazy"
            className="w-full bg-white object-contain"
          />
        ) : (
          <div className="flex aspect-video flex-col items-center justify-center bg-gradient-to-br from-primary-900 via-teal-900 to-gray-900 p-8 text-center">
            <FilmIcon className="mb-4 h-16 w-16 text-teal-400/80" />
            <p className="text-lg font-semibold text-white">{lesson.title}</p>
            <p className="mt-2 max-w-md text-sm text-teal-100/80">{lesson.summary}</p>
          </div>
        )}
      </motion.div>

      {interactiveUrl && (
        <div className="card">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <PresentationChartBarIcon className="h-5 w-5 text-teal-600 dark:text-teal-400" />
              <h2 className="font-semibold text-gray-900 dark:text-gray-100">Interactive Lesson</h2>
            </div>
            <button
              type="button"
              onClick={() => setShowInteractive((open) => !open)}
              className="btn-outline text-sm"
            >
              {showInteractive ? 'Hide' : 'Open'} interactive lesson
            </button>
          </div>
          {showInteractive ? (
            <iframe
              src={interactiveUrl}
              title={`${lesson.title} interactive lesson`}
              className="h-[70vh] w-full rounded-xl border border-gray-200 dark:border-gray-700"
            />
          ) : (
            <p className="text-sm text-gray-600 dark:text-gray-300">
              A self-contained interactive lesson covering {lesson.title.toLowerCase()}. It opens
              inside this page and needs no additional downloads.
            </p>
          )}
        </div>
      )}

      {imageUrl && (
        <div className="card flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <PhotoIcon className="h-4 w-4" />
          <span>Pinch or right-click the image to view it full size.</span>
        </div>
      )}

      <div className="card">
        <div className="mb-3 flex items-center gap-2">
          <LightBulbIcon className="h-5 w-5 text-amber-500" />
          <h2 className="font-semibold text-gray-900 dark:text-gray-100">Summary</h2>
        </div>
        <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{lesson.summary}</p>
        {lesson.content_md && (
          <div className="prose prose-sm mt-4 whitespace-pre-wrap dark:prose-invert">{lesson.content_md}</div>
        )}
      </div>

      {chapter && (
        <div className="flex flex-wrap gap-3">
          <Link to={`/quiz/chapter/${chapter.id}`} className="btn-teal gap-2">
            <AcademicCapIcon className="h-4 w-4" /> Practice Chapter MCQs
          </Link>
          <Link to={`/chapters/${chapter.slug}`} className="btn-outline gap-2">
            Back to Chapter
          </Link>
        </div>
      )}
    </div>
  );
}
