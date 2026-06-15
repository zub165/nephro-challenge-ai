import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import ProtectedRoute from '@/components/ProtectedRoute';
import Layout from '@/components/Layout';

import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import Quiz from '@/pages/Quiz';
import Leaderboard from '@/pages/Leaderboard';
import Profile from '@/pages/Profile';
import Categories from '@/pages/Categories';
import DailyChallenge from '@/pages/DailyChallenge';
import AdminDashboard from '@/pages/AdminDashboard';
import AdminQuestions from '@/pages/AdminQuestions';
import AdminAIGenerated from '@/pages/AdminAIGenerated';

export default function App() {
  const { isAuthenticated, user } = useAuthStore();

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />}
      />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/quiz/:type" element={<Quiz />} />
        <Route path="/quiz/:type/:categoryId" element={<Quiz />} />
        <Route path="/daily-challenge" element={<DailyChallenge />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/categories" element={<Categories />} />

        {user?.role === 'admin' && (
          <>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/questions" element={<AdminQuestions />} />
            <Route path="/admin/ai-generated" element={<AdminAIGenerated />} />
          </>
        )}
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
