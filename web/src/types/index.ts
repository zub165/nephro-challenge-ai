export interface User {
  id: string;
  email: string;
  name?: string;
  username?: string;
  role: 'user' | 'admin' | 'free' | 'premium' | 'guest';
  createdAt?: string;
  updatedAt?: string;
}

export interface AuthResponse {
  token: string;
  access?: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
}

export interface Question {
  id: string;
  text: string;
  caseText?: string;
  labs?: Record<string, string>;
  choices: Choice[];
  correctAnswer: string;
  correctChoiceKey?: string;
  explanation: string;
  clinicalPearl?: string;
  reference?: string;
  categoryId: string;
  chapterId?: string;
  category?: Category;
  difficulty: 'easy' | 'medium' | 'hard' | 'board';
  isAIGenerated: boolean;
  aiReviewStatus?: 'pending' | 'approved' | 'rejected';
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export interface Choice {
  id: string;
  text: string;
  key?: string;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
  questionCount?: number;
}

export interface Chapter {
  id: string;
  title: string;
  slug: string;
  order_index: number;
  description: string;
  icon: string;
  category?: string;
  topic_count?: number;
  question_count?: number;
  lesson_count?: number;
  topics?: Topic[];
}

export interface Topic {
  id: string;
  chapter: string;
  title: string;
  slug: string;
  order_index: number;
  description: string;
  lesson_count?: number;
  question_count?: number;
  lessons?: Lesson[];
}

export interface Lesson {
  id: string;
  title: string;
  lesson_type: 'animation' | 'article' | 'video';
  summary: string;
  content_md?: string;
  animation_url: string;
  thumbnail_url: string;
  duration_seconds: number;
  order_index: number;
  is_premium: boolean;
}

export interface QuizSession {
  id: string;
  userId: string;
  questions: Question[];
  answers: Answer[];
  score: number;
  totalQuestions: number;
  startTime: string;
  endTime?: string;
  isCompleted: boolean;
  type: 'daily' | 'practice' | 'category' | 'chapter';
  categoryId?: string;
  chapterId?: string;
}

export interface Answer {
  questionId: string;
  selectedChoice: string;
  isCorrect: boolean;
  timeSpent: number;
}

export interface LeaderboardEntry {
  userId: string;
  name: string;
  score: number;
  quizCount: number;
  accuracy: number;
  streak: number;
  rank: number;
}

export interface UserStats {
  totalQuizzes: number;
  totalQuestions: number;
  correctAnswers: number;
  accuracy: number;
  currentStreak: number;
  longestStreak: number;
  categoryBreakdown: CategoryPerformance[];
  dailyQuizCompleted: boolean;
  recentActivity: ActivityEntry[];
}

export interface CategoryPerformance {
  categoryId: string;
  categoryName: string;
  totalQuestions: number;
  correctAnswers: number;
  accuracy: number;
}

export interface ActivityEntry {
  date: string;
  quizzesCompleted: number;
  questionsAnswered: number;
  correctAnswers: number;
}

export interface DailyChallenge {
  id: string;
  date: string;
  questions: Question[];
  completed: boolean;
  score?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  statusCode: number;
  errors?: Record<string, string[]>;
}

export interface StudyNote {
  id: string;
  chapter: string | null;
  chapter_slug?: string | null;
  chapter_title?: string | null;
  topic_title: string;
  content: string;
  source_batch_id?: string;
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface NotesChapterGroup {
  chapter: {
    id: string;
    title: string;
    slug: string;
    order_index: number;
  };
  notes: StudyNote[];
  count: number;
}

export interface NotesReview {
  chapters: NotesChapterGroup[];
  uncategorized: StudyNote[];
  total: number;
}

export interface OrganizeNotesResponse {
  method: 'ai' | 'keywords';
  batch_id: string;
  notes: StudyNote[];
  total: number;
  skipped_duplicates?: number;
}
