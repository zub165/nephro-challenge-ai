import { appPath } from '@/lib/appConfig';

/** Resolve lesson animation URL to a bundled GitHub Pages / local public file. */
export function resolveAnimationUrl(animationUrl: string): string {
  if (!animationUrl) return '';

  const filenameMatch = animationUrl.match(/\/([^/]+\.json)(?:\?.*)?$/);
  const filename = filenameMatch?.[1];
  if (filename) {
    return appPath(`/animations/${filename}`);
  }

  if (!animationUrl.includes('://')) {
    const normalized = animationUrl.startsWith('/') ? animationUrl.slice(1) : animationUrl;
    return appPath(`/${normalized}`);
  }

  return animationUrl;
}

export interface AnimationStep {
  title: string;
  body: string;
  tip?: string;
  visual?: AnimationVisual;
  metrics?: AnimationMetrics;
}

export type AnimationVisual =
  | 'circuit-cvvh'
  | 'circuit-cvvhd'
  | 'circuit-scuf'
  | 'pressures'
  | 'dose-summary'
  | 'monitoring';

export interface AnimationMetrics {
  access?: string;
  prefilter?: string;
  return?: string;
  tmp?: string;
  flow?: string;
  effluent?: string;
  dose?: string;
  input?: string;
  balance?: string;
}

export interface LessonAnimationData {
  title: string;
  subtitle?: string;
  theme?: 'crrt' | 'default';
  steps: AnimationStep[];
}
