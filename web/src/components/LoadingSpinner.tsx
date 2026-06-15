import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

const sizes = {
  sm: 'h-6 w-6',
  md: 'h-10 w-10',
  lg: 'h-16 w-16',
};

export default function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <motion.div
        className={`relative ${sizes[size]}`}
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      >
        <div
          className={`absolute inset-0 rounded-full border-4 border-gray-200 dark:border-gray-700 ${sizes[size]}`}
        />
        <div
          className={`absolute inset-0 rounded-full border-4 border-t-teal-600 ${sizes[size]}`}
          style={{ clipPath: 'inset(0 0 50% 0)' }}
        />
      </motion.div>
      {text && (
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{text}</p>
      )}
    </div>
  );
}
