import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '@/lib/axios';
import type { Category } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
  BookOpenIcon,
  ArrowRightIcon,
  ExclamationTriangleIcon,
  BeakerIcon,
  HeartIcon,
  CircleStackIcon,
  UserGroupIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import { useState } from 'react';

const iconMap: Record<string, React.ElementType> = {
  'BeakerIcon': BeakerIcon,
  'HeartIcon': HeartIcon,
  'CircleStackIcon': CircleStackIcon,
  'UserGroupIcon': UserGroupIcon,
  'DocumentTextIcon': DocumentTextIcon,
};

const defaultIcon = BookOpenIcon;

export default function Categories() {
  const [search, setSearch] = useState('');

  const { data: categories, isLoading, error } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: () => api.get('/categories').then((r) => r.data),
  });

  const filtered = (categories || []).filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.description.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return <LoadingSpinner text="Loading categories..." />;

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-center">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Failed to load categories</p>
        <button onClick={() => window.location.reload()} className="btn-primary text-sm">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Question Categories
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Browse nephrology topics and start practicing
        </p>
      </div>

      <div className="relative max-w-md">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search categories..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field pl-9"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <BookOpenIcon className="h-12 w-12 text-gray-300 dark:text-gray-600" />
          <p className="font-medium text-gray-900 dark:text-gray-100">No categories found</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {search ? 'Try a different search term' : 'Categories will appear here'}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((category, i) => {
            const Icon = iconMap[category.icon] || defaultIcon;
            return (
              <motion.div
                key={category.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Link
                  to={`/quiz/category/${category.id}`}
                  className="group card flex h-full flex-col transition-all hover:border-teal-300 hover:shadow-md dark:hover:border-teal-700"
                >
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 group-hover:text-teal-700 dark:group-hover:text-teal-400">
                    {category.name}
                  </h3>
                  <p className="mt-1 flex-1 text-sm text-gray-500 dark:text-gray-400">
                    {category.description}
                  </p>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-400 dark:text-gray-500">
                      {category.questionCount ?? 0} questions
                    </span>
                    <span className="flex items-center gap-1 text-xs font-medium text-teal-700 dark:text-teal-400">
                      Start <ArrowRightIcon className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
                    </span>
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
