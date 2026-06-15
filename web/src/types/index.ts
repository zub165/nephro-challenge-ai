export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  token: string;
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
  choices: Choice[];
  correctAnswer: string;
  explanation: string;
  categoryId: string;
  category?: Category;
  difficulty: 'easy' | 'medium' | 'hard';
  isAIGenerated: boolean;
  aiReviewStatus?: 'pending' | 'approved' | 'rejected';
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export interface Choice {
  id: string;
  text: string;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
  questionCount?: number;
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
  type: 'daily' | 'practice' | 'category';
  categoryId?: string;
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
