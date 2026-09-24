/** Vite `base` path without trailing slash (e.g. /nephro-challenge-ai). */
export const APP_BASENAME = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Django API root; production uses GoDaddy VPS. */
export const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '/api';

export function appPath(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${APP_BASENAME}${normalized}`;
}
