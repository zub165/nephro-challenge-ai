import type { Question } from '@/types';
import { motion } from 'framer-motion';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/solid';

interface QuestionCardProps {
  question: Question;
  selectedAnswer: string | null;
  showResult: boolean;
  onAnswer: (choiceId: string) => void;
  questionNumber: number;
  totalQuestions: number;
}

const difficultyColors = {
  easy: 'badge-green',
  medium: 'badge-amber',
  hard: 'badge-red',
};

export default function QuestionCard({
  question,
  selectedAnswer,
  showResult,
  onAnswer,
  questionNumber,
  totalQuestions,
}: QuestionCardProps) {
  const getChoiceClass = (choiceId: string) => {
    const base = 'flex w-full items-center gap-3 rounded-xl border-2 p-4 text-left text-sm font-medium transition-all duration-200 ';

    if (!showResult) {
      if (selectedAnswer === choiceId) {
        return base + 'border-primary-500 bg-primary-50 dark:border-teal-500 dark:bg-primary-900/30';
      }
      return base + 'border-gray-200 bg-white hover:border-teal-300 hover:bg-teal-50 dark:border-gray-600 dark:bg-gray-800 dark:hover:border-teal-600 dark:hover:bg-teal-900/20';
    }

    if (choiceId === question.correctAnswer) {
      return base + 'border-green-500 bg-green-50 dark:border-green-400 dark:bg-green-900/30';
    }
    if (selectedAnswer === choiceId && choiceId !== question.correctAnswer) {
      return base + 'border-red-500 bg-red-50 dark:border-red-400 dark:bg-red-900/30';
    }
    return base + 'border-gray-200 bg-gray-50 opacity-50 dark:border-gray-600 dark:bg-gray-800';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="mb-4 flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
          Question {questionNumber} of {totalQuestions}
        </span>
        <span className={`text-xs font-medium ${difficultyColors[question.difficulty]}`}>
          {question.difficulty}
        </span>
      </div>

      <h3 className="mb-6 text-lg font-semibold leading-relaxed text-gray-900 dark:text-gray-100">
        {question.text}
      </h3>

      <div className="flex flex-col gap-3">
        {question.choices.map((choice) => (
          <button
            key={choice.id}
            onClick={() => !showResult && onAnswer(choice.id)}
            disabled={showResult}
            className={getChoiceClass(choice.id)}
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-600 dark:bg-gray-700 dark:text-gray-300">
              {String.fromCharCode(65 + question.choices.indexOf(choice))}
            </span>
            <span className="flex-1">{choice.text}</span>
            {showResult && choice.id === question.correctAnswer && (
              <CheckCircleIcon className="h-6 w-6 flex-shrink-0 text-green-600 dark:text-green-400" />
            )}
            {showResult && selectedAnswer === choice.id && choice.id !== question.correctAnswer && (
              <XCircleIcon className="h-6 w-6 flex-shrink-0 text-red-600 dark:text-red-400" />
            )}
          </button>
        ))}
      </div>

      {showResult && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 rounded-xl bg-blue-50 p-4 dark:bg-blue-900/20"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-blue-700 dark:text-blue-300">
            Explanation
          </p>
          <p className="mt-1 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
            {question.explanation}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}
