import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/axios';
import type { Question, QuizSession } from '@/types';
import QuestionCard from '@/components/QuestionCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  HomeIcon,
} from '@heroicons/react/24/outline';

const QUIZ_TIME_LIMIT = 30 * 60;

export default function Quiz() {
  const { type, categoryId } = useParams();
  const navigate = useNavigate();
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [timeLeft, setTimeLeft] = useState(QUIZ_TIME_LIMIT);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [finished, setFinished] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['quiz-questions', type, categoryId],
    queryFn: () => {
      const params: Record<string, string> = {};
      if (type === 'category' && categoryId) params.categoryId = categoryId;
      if (type === 'daily') params.daily = 'true';
      params.limit = type === 'daily' ? '5' : '10';
      return api.get('/questions/quiz', { params }).then((r) => r.data);
    },
    enabled: !finished,
  });

  useEffect(() => {
    if (data?.questions) {
      setQuestions(data.questions);
      if (data.sessionId) setSessionId(data.sessionId);
    } else if (data?.length) {
      setQuestions(data);
    }
  }, [data]);

  useEffect(() => {
    if (questions.length > 0 && !showResults && !finished) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handleSubmitQuiz();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [questions.length, showResults, finished]);

  const handleAnswer = useCallback((choiceId: string) => {
    if (showResults) return;
    setAnswers((prev) => ({ ...prev, [questions[currentIndex].id]: choiceId }));

    setTimeout(() => {
      if (currentIndex < questions.length - 1) {
        setCurrentIndex((i) => i + 1);
      } else {
        handleSubmitQuiz();
      }
    }, 300);
  }, [currentIndex, questions, showResults]);

  const handleSubmitQuiz = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setShowResults(true);

    const correctCount = questions.filter(
      (q) => answers[q.id] === q.correctAnswer
    ).length;

    if (sessionId) {
      setSubmitting(true);
      try {
        await api.put(`/quizzes/${sessionId}`, {
          answers: questions.map((q) => ({
            questionId: q.id,
            selectedChoice: answers[q.id] || '',
            isCorrect: answers[q.id] === q.correctAnswer,
            timeSpent: QUIZ_TIME_LIMIT - timeLeft,
          })),
          score: correctCount,
          totalQuestions: questions.length,
          isCompleted: true,
          endTime: new Date().toISOString(),
        });
      } catch (err) {
        console.error('Failed to save quiz', err);
      } finally {
        setSubmitting(false);
      }
    }
    setFinished(true);
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (isLoading) return <LoadingSpinner text="Loading questions..." />;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <XCircleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Failed to load quiz questions</p>
        <button onClick={() => navigate('/dashboard')} className="btn-primary text-sm">
          Back to Dashboard
        </button>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <CheckCircleIcon className="h-12 w-12 text-teal-400" />
        <p className="text-lg font-medium text-gray-900 dark:text-gray-100">No questions available</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">Try a different category or come back later</p>
        <Link to="/dashboard" className="btn-primary text-sm">Dashboard</Link>
      </div>
    );
  }

  if (finished) {
    const correctCount = questions.filter((q) => answers[q.id] === q.correctAnswer).length;
    const percentage = Math.round((correctCount / questions.length) * 100);

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mx-auto max-w-2xl py-8"
      >
        <div className="card text-center">
          <div className="mb-6">
            {percentage >= 80 ? (
              <CheckCircleIcon className="mx-auto h-16 w-16 text-green-500" />
            ) : percentage >= 50 ? (
              <ArrowPathIcon className="mx-auto h-16 w-16 text-amber-500" />
            ) : (
              <XCircleIcon className="mx-auto h-16 w-16 text-red-500" />
            )}
          </div>

          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Quiz Complete!
          </h2>
          <p className="mt-2 text-4xl font-extrabold text-primary-900 dark:text-teal-300">
            {correctCount}/{questions.length}
          </p>
          <p className="mt-1 text-lg font-medium text-gray-600 dark:text-gray-400">
            {percentage}% Correct
          </p>

          <div className="mx-auto mt-6 h-3 w-full max-w-xs rounded-full bg-gray-100 dark:bg-gray-700">
            <div
              className={`h-3 rounded-full transition-all ${
                percentage >= 80 ? 'bg-green-500' : percentage >= 50 ? 'bg-amber-500' : 'bg-red-500'
              }`}
              style={{ width: `${percentage}%` }}
            />
          </div>

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/dashboard" className="btn-primary gap-2">
              <HomeIcon className="h-4 w-4" /> Dashboard
            </Link>
            <button
              onClick={() => {
                setQuestions([]);
                setCurrentIndex(0);
                setAnswers({});
                setShowResults(false);
                setTimeLeft(QUIZ_TIME_LIMIT);
                setSessionId(null);
                setFinished(false);
              }}
              className="btn-outline gap-2"
            >
              <ArrowPathIcon className="h-4 w-4" /> New Quiz
            </button>
            <Link
              to={type === 'daily' ? '/daily-challenge' : `/quiz/${type}`}
              className="btn-teal gap-2"
            >
              <ArrowPathIcon className="h-4 w-4" /> Retry
            </Link>
          </div>
        </div>

        <div className="mt-6 space-y-4">
          {questions.map((q, i) => {
            const isCorrect = answers[q.id] === q.correctAnswer;
            return (
              <QuestionCard
                key={q.id}
                question={q}
                selectedAnswer={answers[q.id] || null}
                showResult={true}
                onAnswer={() => {}}
                questionNumber={i + 1}
                totalQuestions={questions.length}
              />
            );
          })}
        </div>
      </motion.div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl py-4">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Progress: {currentIndex + 1}/{questions.length}
          </span>
          <div className="h-2 w-32 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700 sm:w-48">
            <div
              className="h-2 rounded-full bg-teal-600 transition-all duration-300"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        <div className={`flex items-center gap-2 rounded-xl px-3 py-1.5 text-sm font-bold ${
          timeLeft < 120
            ? 'timer-warning bg-red-50 dark:bg-red-900/30'
            : timeLeft < 300
            ? 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
            : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
        }`}>
          <ClockIcon className="h-4 w-4" />
          {formatTime(timeLeft)}
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.2 }}
        >
          <QuestionCard
            question={questions[currentIndex]}
            selectedAnswer={answers[questions[currentIndex]?.id] || null}
            showResult={false}
            onAnswer={handleAnswer}
            questionNumber={currentIndex + 1}
            totalQuestions={questions.length}
          />
        </motion.div>
      </AnimatePresence>

      <div className="mt-6 flex justify-center">
        <button
          onClick={handleSubmitQuiz}
          className="btn-outline gap-2 text-sm"
        >
          Submit Quiz Early
        </button>
      </div>
    </div>
  );
}
