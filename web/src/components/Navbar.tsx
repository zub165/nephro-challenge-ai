import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import {
  HomeIcon,
  AcademicCapIcon,
  TrophyIcon,
  UserIcon,
  BookOpenIcon,
  SunIcon,
  MoonIcon,
  ArrowRightOnRectangleIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { path: '/daily-challenge', label: 'Daily Challenge', icon: AcademicCapIcon },
  { path: '/categories', label: 'Categories', icon: BookOpenIcon },
  { path: '/leaderboard', label: 'Leaderboard', icon: TrophyIcon },
  { path: '/profile', label: 'Profile', icon: UserIcon },
];

const adminItems = [
  { path: '/admin', label: 'Admin', icon: ShieldCheckIcon },
  { path: '/admin/questions', label: 'Questions', icon: BookOpenIcon },
  { path: '/admin/ai-generated', label: 'AI Review', icon: AcademicCapIcon },
];

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const [darkMode, setDarkMode] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const isDark = localStorage.getItem('theme') === 'dark' ||
      (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    setDarkMode(isDark);
    document.documentElement.classList.toggle('dark', isDark);
  }, []);

  const toggleDark = () => {
    const next = !darkMode;
    setDarkMode(next);
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  };

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-lg dark:border-gray-700 dark:bg-gray-900/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link to="/dashboard" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-900">
            <svg viewBox="0 0 64 64" className="h-6 w-6" fill="none">
              <path d="M32 12C32 12 20 20 20 32C20 38.627 25.373 44 32 44C38.627 44 44 38.627 44 32C44 20 32 12 32 12Z" stroke="white" strokeWidth="3"/>
              <path d="M32 22V34" stroke="white" strokeWidth="3" strokeLinecap="round"/>
              <path d="M26 28H38" stroke="white" strokeWidth="3" strokeLinecap="round"/>
              <circle cx="32" cy="32" r="1.5" fill="#0d9488"/>
            </svg>
          </div>
          <span className="text-lg font-bold text-primary-900 dark:text-white">
            Nephro<span className="text-teal-700">Challenge</span>
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive(item.path)
                  ? 'bg-primary-50 text-primary-900 dark:bg-primary-900/30 dark:text-teal-300'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200'
              }`}
            >
              <item.icon className="h-4.5 w-4.5" />
              {item.label}
            </Link>
          ))}
          {user?.role === 'admin' && (
            <div className="ml-2 border-l border-gray-200 pl-2 dark:border-gray-700">
              {adminItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive(item.path)
                      ? 'bg-amber-50 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200'
                  }`}
                >
                  <item.icon className="h-4.5 w-4.5" />
                  {item.label}
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleDark}
            className="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
            aria-label="Toggle dark mode"
          >
            {darkMode ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
          </button>

          <button
            onClick={logout}
            className="hidden rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 sm:block"
            aria-label="Logout"
            title="Logout"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5" />
          </button>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 md:hidden"
            aria-label="Toggle menu"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-900 md:hidden"
          >
            <div className="flex flex-col gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium ${
                    isActive(item.path)
                      ? 'bg-primary-50 text-primary-900 dark:bg-primary-900/30 dark:text-teal-300'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  {item.label}
                </Link>
              ))}
              {user?.role === 'admin' && (
                <>
                  <div className="my-1 border-t border-gray-200 pt-1 dark:border-gray-700" />
                  <p className="px-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Admin</p>
                  {adminItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium ${
                        isActive(item.path)
                          ? 'bg-amber-50 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
                          : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                      }`}
                    >
                      <item.icon className="h-5 w-5" />
                      {item.label}
                    </Link>
                  ))}
                </>
              )}
              <div className="my-1 border-t border-gray-200 pt-1 dark:border-gray-700" />
              <button
                onClick={() => { logout(); setMobileOpen(false); }}
                className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
                Logout
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
