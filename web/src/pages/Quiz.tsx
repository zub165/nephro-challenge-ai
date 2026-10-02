import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link, useSearchParams } from 'react-router-dom';
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

interface QuizResult {
  chosenId: string;
  correctId: string;
  isCorrect: boolean;
  explanation: string;
  clinicalPearl: string;
  whyWrong?: string;
  reference: string;
}

export default function Quiz() {
  const { type, categoryId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const submitRef = useRef<() => void>(() => {});
  const advancingRef = useRef(false);
  const submittingRef = useRef(false);
  const answersRef = useRef<Record<string, string>>({});
  const confidenceRef = useRef<Record<string, 'know' | 'guessed'>>({});
  const timeLeftRef = useRef(QUIZ_TIME_LIMIT);

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [confidence, setConfidence] = useState<Record<string, 'know' | 'guessed'>>({});
  const [pendingChoice, setPendingChoice] = useState<string | null>(null);
  const [revealing, setRevealing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [timeLeft, setTimeLeft] = useState(QUIZ_TIME_LIMIT);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [finished, setFinished] = useState(false);
  const [results, setResults] = useState<Record<string, QuizResult>>({});
  const [submitFailed, setSubmitFailed] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['quiz-questions', type, categoryId, searchParams.toString()],
    queryFn: async () => {
      const boardDay = searchParams.get('day');
      const limitParam = searchParams.get('limit');
      const params: Record<string, string> = {
        limit: limitParam || (type === 'daily' ? '5' : type === 'board-prep' ? '18' : '10'),
      };
      if (type === 'category' && categoryId) params.categoryId = categoryId;
      if (type === 'chapter' && categoryId) params.chapterId = categoryId;
      if (type === 'daily') params.daily = 'true';
      if (type === 'board-prep') params.board_day = boardDay || '1';
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
    confidenceRef.current = confidence;
  }, [confidence]);

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

      setSubmitting(true);
      setSubmitFailed(false);
      try {
        const { data: attempt } = await api.post('/attempts/', {
          mode: type === 'daily' ? 'daily' : type === 'chapter' ? 'chapter' : type === 'category' ? 'category' : type === 'board-prep' ? 'board_prep' : 'practice',
          chapter: type === 'chapter' && categoryId ? categoryId : undefined,
          category: type === 'category' && categoryId ? categoryId : undefined,
          total_questions: questions.length,
          time_taken: QUIZ_TIME_LIMIT - timeLeftRef.current,
          answers_data: questions
            .filter((q) => submitted[q.id])
            .map((q) => ({
              question_id: q.id,
              chosen_choice_id: submitted[q.id],
              confidence: confidenceRef.current[q.id] || 'know',
              time_taken: Math.floor((QUIZ_TIME_LIMIT - timeLeftRef.current) / questions.length),
            })),
        });

        // The server is the only place answers live; the reveal below comes
        // from the graded attempt, never from the question payload.
        const byQuestion: Record<string, QuizResult> = {};
        (attempt.answers || []).forEach((a: Record<string, unknown>) => {
          const refs = Array.isArray(a.references)
            ? (a.references as Array<Record<string, unknown>>)
                .map((r) => String(r.citation ?? r.title ?? ''))
                .filter(Boolean)
                .join(' | ')
            : '';
          const qid = String(
            a.question_id ??
              (typeof a.question === 'object' && a.question
                ? (a.question as { id?: unknown }).id
                : a.question) ??
              ''
          );
          byQuestion[qid] = {
            chosenId: String(a.chosen_choice_id ?? ''),
            correctId: String(a.correct_choice_id ?? ''),
            isCorrect: Boolean(a.is_correct),
            explanation: String(a.explanation ?? ''),
            clinicalPearl: String(a.clinical_pearl ?? ''),
            whyWrong: String(a.why_wrong ?? ''),
            reference: refs,
          };
        });
        setResults(byQuestion);
      } catch (err) {
        console.error('Failed to save quiz', err);
        setSubmitFailed(true);
      } finally {
        setSubmitting(false);
      }
      setFinished(true);
      submittingRef.current = false;
    },
    [questions, type, categoryId, showResults]
  );

  submitRef.current = handleSubmitQuiz;

  const commitAnswer = useCallback(
    (choiceId: string, tag: 'know' | 'guessed') => {
      if (showResults || advancingRef.current) return;
      const current = questions[currentIndex];
      if (!current) return;
      const next = { ...answersRef.current, [current.id]: choiceId };
      const nextConf = { ...confidenceRef.current, [current.id]: tag };
      answersRef.current = next;
      confidenceRef.current = nextConf;
      setAnswers(next);
      setConfidence(nextConf);
      advancingRef.current = true;
      setPendingChoice(null);
      setTimeout(() => {
        advancingRef.current = false;
        if (currentIndex < questions.length - 1) {
          setCurrentIndex((i) => i + 1);
        } else {
          handleSubmitQuiz(next);
        }
      }, 150);
    },
    [currentIndex, questions, showResults, handleSubmitQuiz]
  );

  const handleAnswer = useCallback(
    async (choiceId: string) => {
      if (showResults || advancingRef.current || revealing) return;
      const current = questions[currentIndex];
      if (!current || results[current.id]) return;
      setPendingChoice(choiceId);
      setRevealing(true);
      try {
        const { data: reveal } = await api.post('/quiz/answer/', {
          question_id: current.id,
          chosen_choice_id: choiceId,
        });
        const refs = Array.isArray(reveal.references)
          ? reveal.references
              .map((r: { citation?: string; title?: string }) => r.citation || r.title || '')
              .filter(Boolean)
              .join(' | ')
          : '';
        setResults((prev) => ({
          ...prev,
          [current.id]: {
            chosenId: choiceId,
            correctId: String(reveal.correct_choice_id ?? ''),
            isCorrect: Boolean(reveal.is_correct),
            explanation: String(reveal.explanation ?? ''),
            clinicalPearl: String(reveal.clinical_pearl ?? ''),
            whyWrong: String(reveal.why_wrong ?? ''),
            reference: refs,
          },
        }));
      } catch (err) {
        console.error('Could not reveal answer', err);
        toast.error('Could not load the explanation. Check your connection.');
      } finally {
        setRevealing(false);
      }
    },
    [showResults, revealing, questions, currentIndex, results]
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
    const answered = questions.filter((q) => results[q.id]).length;
    const correctCount = questions.filter((q) => results[q.id]?.isCorrect).length;
    const percentage = answered
      ? Math.round((correctCount / answered) * 100)
      : 0;

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
            {correctCount}/{answered}
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
                setConfidence({});
                confidenceRef.current = {};
                setPendingChoice(null);
                setShowResults(false);
                setTimeLeft(QUIZ_TIME_LIMIT);
                timeLeftRef.current = QUIZ_TIME_LIMIT;
                setSessionId(null);
                setFinished(false);
                setResults({});
                setRevealing(false);
                setSubmitFailed(false);
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
          {submitFailed && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900/40 dark:bg-amber-900/20 dark:text-amber-200">
              Your answers could not be saved to the server, so the correct
              answers and explanations are not available for this attempt.
              Please check your connection and try again.
            </div>
          )}
          {questions.map((q, i) => {
            const r = results[q.id];
            const revealed: Question = r
              ? {
                  ...q,
                  correctAnswer: r.correctId,
                  explanation: r.explanation,
                  clinicalPearl: r.clinicalPearl,
                  reference: r.reference,
                }
              : q;
            return (
              <QuestionCard
                key={q.id}
                question={revealed}
                selectedAnswer={answers[q.id] || r?.chosenId || null}
                showResult={true}
                whyWrong={r?.whyWrong}
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
            question={
              results[questions[currentIndex]?.id]
                ? {
                    ...questions[currentIndex],
                    correctAnswer: results[questions[currentIndex].id].correctId,
                    explanation: results[questions[currentIndex].id].explanation,
                    clinicalPearl: results[questions[currentIndex].id].clinicalPearl,
                    reference: results[questions[currentIndex].id].reference,
                  }
                : questions[currentIndex]
            }
            selectedAnswer={pendingChoice || answers[questions[currentIndex]?.id] || null}
            showResult={Boolean(results[questions[currentIndex]?.id])}
            whyWrong={results[questions[currentIndex]?.id]?.whyWrong}
            onAnswer={handleAnswer}
            questionNumber={currentIndex + 1}
            totalQuestions={questions.length}
          />
          {revealing && (
            <p className="mt-3 text-center text-sm text-gray-500">Checking your answer…</p>
          )}
          {pendingChoice && results[questions[currentIndex]?.id] && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-900/40 dark:bg-amber-900/20">
              <p className="mb-3 text-sm font-medium text-amber-900 dark:text-amber-100">
                Classify this question, then continue
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="btn-primary text-sm"
                  onClick={() => commitAnswer(pendingChoice, 'know')}
                >
                  Know
                </button>
                <button
                  type="button"
                  className="btn-outline text-sm"
                  onClick={() => commitAnswer(pendingChoice, 'guessed')}
                >
                  Guessed
                </button>
              </div>
            </div>
          )}
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
