import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/axios';
import { mapBackendQuestion } from '@/lib/apiMappers';
import type { Question } from '@/types';
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
  const queryClient = useQueryClient();
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const submitRef = useRef<() => void>(() => {});
  const advancingRef = useRef(false);
  const submittingRef = useRef(false);
  const answersRef = useRef<Record<string, string>>({});
  const timeLeftRef = useRef(QUIZ_TIME_LIMIT);

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
    queryFn: async () => {
      const params: Record<string, string> = { limit: type === 'daily' ? '5' : '10' };
      if (type === 'category' && categoryId) params.categoryId = categoryId;
      if (type === 'chapter' && categoryId) params.chapterId = categoryId;
      if (type === 'daily') params.daily = 'true';
      const { data: res } = await api.get('/questions/quiz/', { params });
      return {
        questions: (res.questions || []).map(mapBackendQuestion),
        sessionId: res.sessionId,
      };
    },
    enabled: !finished,
  });

  useEffect(() => {
    if (data?.questions) {
      setQuestions(data.questions);
      if (data.sessionId) setSessionId(data.sessionId);
    }
  }, [data]);

  useEffect(() => {
    answersRef.current = answers;
  }, [answers]);

  useEffect(() => {
    timeLeftRef.current = timeLeft;
  }, [timeLeft]);

  useEffect(() => {
    if (questions.length > 0 && !showResults && !finished) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => Math.max(0, prev - 1));
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [questions.length, showResults, finished]);

  useEffect(() => {
    if (timeLeft <= 0 && questions.length > 0 && !showResults && !finished) {
      submitRef.current();
    }
  }, [timeLeft, questions.length, showResults, finished]);

  const handleSubmitQuiz = useCallback(
    async (finalAnswers?: Record<string, string>) => {
      if (submittingRef.current || showResults) return;
      submittingRef.current = true;

      const submitted = finalAnswers ?? answersRef.current;
      if (timerRef.current) clearInterval(timerRef.current);
      setShowResults(true);

      const correctCount = questions.filter(
        (q) => submitted[q.id] === q.correctAnswer
      ).length;

      setSubmitting(true);
      try {
        await api.post('/attempts/', {
          mode: type === 'daily' ? 'daily' : type === 'chapter' ? 'chapter' : type === 'category' ? 'category' : 'practice',
          chapter: type === 'chapter' && categoryId ? categoryId : undefined,
          category: type === 'category' && categoryId ? categoryId : undefined,
          total_questions: questions.length,
          time_taken: QUIZ_TIME_LIMIT - timeLeftRef.current,
          answers_data: questions
            .filter((q) => submitted[q.id])
            .map((q) => ({
              question_id: q.id,
              chosen_choice_id: submitted[q.id],
              time_taken: Math.floor((QUIZ_TIME_LIMIT - timeLeftRef.current) / questions.length),
            })),
        });
      } catch (err) {
        console.error('Failed to save quiz', err);
      } finally {
        setSubmitting(false);
      }
      setFinished(true);
      submittingRef.current = false;
    },
    [questions, type, categoryId, showResults]
  );

  submitRef.current = handleSubmitQuiz;

  const handleAnswer = useCallback(
    (choiceId: string) => {
      if (showResults || advancingRef.current) return;
      advancingRef.current = true;

      const current = questions[currentIndex];
      if (!current) return;
      const next = { ...answersRef.current, [current.id]: choiceId };
      answersRef.current = next;
      setAnswers(next);

      setTimeout(() => {
        advancingRef.current = false;
        if (currentIndex < questions.length - 1) {
          setCurrentIndex((i) => i + 1);
        } else {
          handleSubmitQuiz(next);
        }
      }, 300);
    },
    [currentIndex, questions, showResults, handleSubmitQuiz]
  );

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
                answersRef.current = {};
                setShowResults(false);
                setTimeLeft(QUIZ_TIME_LIMIT);
                timeLeftRef.current = QUIZ_TIME_LIMIT;
                setSessionId(null);
                setFinished(false);
                submittingRef.current = false;
                advancingRef.current = false;
                queryClient.invalidateQueries({ queryKey: ['quiz-questions', type, categoryId] });
              }}
              className="btn-outline gap-2"
            >
              <ArrowPathIcon className="h-4 w-4" /> New Quiz
            </button>
            <Link
              to={type === 'daily' ? '/daily-challenge' : type === 'category' || type === 'chapter' && categoryId ? `/quiz/${type}/${categoryId}` : `/quiz/${type}`}
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
          onClick={() => handleSubmitQuiz()}
          className="btn-outline gap-2 text-sm"
        >
          Submit Quiz Early
        </button>
      </div>
    </div>
  );
}
