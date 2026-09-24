import type { Question, LeaderboardEntry, DailyChallenge, Category } from '@/types';

/** Django REST Framework paginated or plain list responses */
export function unwrapList<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  if (data && typeof data === 'object' && Array.isArray((data as { results?: T[] }).results)) {
    return (data as { results: T[] }).results;
  }
  return [];
}

export function mapLeaderboardEntries(raw: unknown): LeaderboardEntry[] {
  return unwrapList<Record<string, unknown>>(raw).map((entry, index) => ({
    userId: String(entry.user ?? entry.id ?? index),
    name: String(entry.username ?? entry.name ?? 'User'),
    score: Number(entry.score ?? 0),
    quizCount: Number(entry.quiz_count ?? entry.quizCount ?? 0),
    accuracy: Number(entry.accuracy ?? 0),
    streak: Number(entry.streak ?? entry.streak_count ?? 0),
    rank: Number(entry.rank ?? index + 1),
  }));
}

export function mapDailyChallenge(raw: Record<string, unknown>): DailyChallenge {
  const questionsRaw = Array.isArray(raw.questions)
    ? raw.questions
    : raw.id
      ? [raw]
      : [];
  return {
    id: String(raw.id ?? `daily-${new Date().toISOString().slice(0, 10)}`),
    date: String(raw.date ?? new Date().toISOString().slice(0, 10)),
    questions: questionsRaw.map((q) => mapBackendQuestion(q as Record<string, unknown>)),
    completed: Boolean(raw.completed),
    score: raw.score != null ? Number(raw.score) : undefined,
  };
}

export function mapCategories(raw: unknown): Category[] {
  return unwrapList<Record<string, unknown>>(raw).map((c) => ({
    id: String(c.id),
    name: String(c.name),
    description: String(c.description ?? ''),
    icon: String(c.icon ?? ''),
    questionCount: Number(c.question_count ?? c.questionCount ?? 0),
  }));
}

/** Map backend /questions/quiz response item to Question type */
export function mapBackendQuestion(raw: Record<string, unknown>): Question {
  return {
    id: String(raw.id),
    text: String(raw.text ?? raw.question_text ?? ''),
    caseText: String(raw.caseText ?? raw.case_text ?? ''),
    labs: (raw.labs as Record<string, string>) || {},
    choices: ((raw.choices as Array<Record<string, unknown>>) || []).map((c) => ({
      id: String(c.id),
      text: String(c.text ?? c.choice_text ?? ''),
      key: String(c.key ?? c.choice_key ?? ''),
    })),
    correctAnswer: String(raw.correctAnswer ?? ''),
    correctChoiceKey: String(raw.correctChoiceKey ?? raw.correct_choice_key ?? ''),
    explanation: String(raw.explanation ?? ''),
    clinicalPearl: String(raw.clinicalPearl ?? raw.clinical_pearl ?? ''),
    reference: String(raw.reference ?? ''),
    categoryId: String(raw.categoryId ?? raw.category ?? ''),
    chapterId: raw.chapterId ? String(raw.chapterId) : undefined,
    difficulty: (raw.difficulty as Question['difficulty']) || 'medium',
    isAIGenerated: Boolean(raw.isAIGenerated ?? false),
    createdBy: String(raw.createdBy ?? ''),
    createdAt: String(raw.createdAt ?? ''),
    updatedAt: String(raw.updatedAt ?? ''),
  };
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}
