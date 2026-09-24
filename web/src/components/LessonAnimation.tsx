import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  ArrowPathIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PauseIcon,
  PlayIcon,
} from '@heroicons/react/24/outline';
import type { LessonAnimationData } from '@/lib/animationUtils';
import { resolveAnimationUrl } from '@/lib/animationUtils';
import CrrtStepVisual from '@/components/CrrtStepVisual';

interface LessonAnimationProps {
  animationUrl: string;
  fallbackTitle: string;
  fallbackSummary?: string;
}

export default function LessonAnimation({
  animationUrl,
  fallbackTitle,
  fallbackSummary,
}: LessonAnimationProps) {
  const [data, setData] = useState<LessonAnimationData | null>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stepIndex, setStepIndex] = useState(0);
  const [playing, setPlaying] = useState(false);

  const resolvedUrl = resolveAnimationUrl(animationUrl);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    setData(null);
    setStepIndex(0);
    setPlaying(false);

    if (!resolvedUrl) {
      setLoading(false);
      setError(true);
      return;
    }

    fetch(resolvedUrl)
      .then((res) => {
        if (!res.ok) throw new Error('Animation not found');
        return res.json();
      })
      .then((json: LessonAnimationData) => {
        if (!cancelled) {
          setData(json);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(true);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [resolvedUrl]);

  useEffect(() => {
    if (!playing || !data?.steps.length) return;
    const timer = window.setInterval(() => {
      setStepIndex((current) => {
        if (current >= data.steps.length - 1) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, 4500);
    return () => window.clearInterval(timer);
  }, [playing, data?.steps.length]);

  if (loading) {
    return (
      <div className="flex aspect-video items-center justify-center bg-gradient-to-br from-primary-900 via-teal-900 to-gray-900">
        <p className="text-sm text-teal-100/80">Loading animation...</p>
      </div>
    );
  }

  if (error || !data?.steps?.length) {
    return (
      <div className="flex aspect-video flex-col items-center justify-center bg-gradient-to-br from-primary-900 via-teal-900 to-gray-900 p-8 text-center">
        <p className="text-lg font-semibold text-white">{fallbackTitle}</p>
        {fallbackSummary && (
          <p className="mt-2 max-w-md text-sm text-teal-100/80">{fallbackSummary}</p>
        )}
        <p className="mt-4 text-xs text-amber-200/90">Animation file unavailable</p>
      </div>
    );
  }

  const step = data.steps[stepIndex];
  const progress = ((stepIndex + 1) / data.steps.length) * 100;

  return (
    <div className={`bg-gradient-to-br ${data.theme === 'crrt' ? 'from-slate-900 via-blue-950 to-teal-950' : 'from-primary-900 via-teal-950 to-gray-950'}`}>
      <div className="border-b border-white/10 px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-widest text-teal-300">
          Animated Algorithm
        </p>
        <h2 className="mt-1 text-lg font-bold text-white">{data.title || fallbackTitle}</h2>
        {data.subtitle && <p className="mt-1 text-sm text-teal-100/70">{data.subtitle}</p>}
      </div>

      <div className="relative min-h-[280px] px-5 py-6 sm:min-h-[320px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={stepIndex}
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
            transition={{ duration: 0.35 }}
            className="mx-auto max-w-2xl"
          >
            <div className="mb-3 flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-teal-500 text-sm font-bold text-white shadow-lg">
                {stepIndex + 1}
              </span>
              <h3 className="text-xl font-semibold text-white">{step.title}</h3>
            </div>
            <p className="text-base leading-relaxed text-teal-50/95">{step.body}</p>
            {step.visual && (
              <div className="mt-4 rounded-xl border border-white/10 bg-black/20 p-4">
                <CrrtStepVisual visual={step.visual} metrics={step.metrics} />
              </div>
            )}
            {step.tip && (
              <div className="mt-4 rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-amber-300">Pearl</p>
                <p className="mt-1 text-sm text-amber-50/90">{step.tip}</p>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="border-t border-white/10 px-5 py-4">
        <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-white/10">
          <motion.div
            className="h-full rounded-full bg-teal-400"
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-teal-200/70">
            Step {stepIndex + 1} of {data.steps.length}
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setStepIndex(0)}
              className="rounded-lg p-2 text-teal-200 transition-colors hover:bg-white/10"
              aria-label="Restart"
            >
              <ArrowPathIcon className="h-5 w-5" />
            </button>
            <button
              type="button"
              onClick={() => setStepIndex((i) => Math.max(0, i - 1))}
              disabled={stepIndex === 0}
              className="rounded-lg p-2 text-teal-200 transition-colors hover:bg-white/10 disabled:opacity-40"
              aria-label="Previous step"
            >
              <ChevronLeftIcon className="h-5 w-5" />
            </button>
            <button
              type="button"
              onClick={() => setPlaying((p) => !p)}
              className="rounded-lg bg-teal-600 px-3 py-2 text-white transition-colors hover:bg-teal-500"
            >
              {playing ? <PauseIcon className="h-5 w-5" /> : <PlayIcon className="h-5 w-5" />}
            </button>
            <button
              type="button"
              onClick={() => setStepIndex((i) => Math.min(data.steps.length - 1, i + 1))}
              disabled={stepIndex >= data.steps.length - 1}
              className="rounded-lg p-2 text-teal-200 transition-colors hover:bg-white/10 disabled:opacity-40"
              aria-label="Next step"
            >
              <ChevronRightIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
