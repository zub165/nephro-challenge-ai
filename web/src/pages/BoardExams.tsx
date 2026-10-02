import { useQuery, useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import api from '@/lib/axios';
import LoadingSpinner from '@/components/LoadingSpinner';
import toast from 'react-hot-toast';

type Exam = {
  id: number;
  slug: string;
  title: string;
  description: string;
  question_count: number;
  duration_minutes: number;
};

export default function BoardExams() {
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({
    queryKey: ['board-exams'],
    queryFn: () => api.get('/board-exams/').then((r) => r.data),
  });

  const start = useMutation({
    mutationFn: (slug: string) => api.post(`/board-exams/${slug}/start/`),
    onSuccess: (res, slug) => {
      navigate(`/board-exams/${slug}/attempt/${res.data.attempt_id}`);
    },
    onError: () => toast.error('Could not start exam'),
  });

  if (isLoading) return <LoadingSpinner text="Loading board exams..." />;
  const exams: Exam[] = data?.results || data || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Timed board simulation</h1>
        <p className="mt-1 text-sm text-gray-500">
          Day 24 of the plan. Answers are saved on the server; explanations appear after submit.
        </p>
      </div>
      {exams.length === 0 ? (
        <p className="text-sm text-gray-500">No published exams yet.</p>
      ) : (
        exams.map((exam) => (
          <div key={exam.slug} className="card flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="font-semibold">{exam.title}</h2>
              <p className="text-sm text-gray-500">{exam.description}</p>
              <p className="mt-1 text-xs text-gray-400">
                {exam.question_count} questions · {exam.duration_minutes} minutes
              </p>
            </div>
            <button
              type="button"
              className="btn-primary text-sm"
              disabled={start.isPending}
              onClick={() => start.mutate(exam.slug)}
            >
              Start / resume
            </button>
          </div>
        ))
      )}
      <Link to="/board-prep" className="text-sm text-teal-700">
        ← Back to 25-day plan
      </Link>
    </div>
  );
}
