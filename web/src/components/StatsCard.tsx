import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'primary' | 'teal' | 'amber' | 'green' | 'red';
}

const colorVariants = {
  primary: 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300',
  teal: 'bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300',
  amber: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  green: 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  red: 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300',
};

export default function StatsCard({ title, value, icon, trend, color = 'primary' }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
            {title}
          </p>
          <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-100">
            {value}
          </p>
          {trend && (
            <p className={`mt-1 flex items-center gap-1 text-xs font-medium ${
              trend.isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`}>
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              <span>{trend.value}% from last week</span>
            </p>
          )}
        </div>
        <div className={`rounded-xl p-3 ${colorVariants[color]}`}>
          {icon}
        </div>
      </div>
    </motion.div>
  );
}
