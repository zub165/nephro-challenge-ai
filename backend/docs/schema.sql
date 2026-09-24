
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  role TEXT DEFAULT 'student',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chapters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  order_index INT NOT NULL,
  description TEXT
);

CREATE TABLE topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  slug TEXT NOT NULL,
  order_index INT NOT NULL,
  description TEXT
);

CREATE TABLE lessons (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  lesson_type TEXT NOT NULL,
  summary TEXT,
  content_md TEXT,
  animation_url TEXT,
  thumbnail_url TEXT,
  duration_seconds INT DEFAULT 0,
  order_index INT NOT NULL,
  is_premium BOOLEAN DEFAULT FALSE
);

CREATE TABLE mcqs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
  topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
  lesson_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
  difficulty TEXT DEFAULT 'medium',
  question_stem TEXT NOT NULL,
  clinical_case TEXT,
  labs JSONB,
  image_url TEXT,
  correct_choice_key TEXT NOT NULL,
  explanation TEXT NOT NULL,
  clinical_pearl TEXT,
  reference TEXT,
  is_premium BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE mcq_choices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  mcq_id UUID REFERENCES mcqs(id) ON DELETE CASCADE,
  choice_key TEXT NOT NULL,
  choice_text TEXT NOT NULL,
  why_wrong TEXT,
  UNIQUE(mcq_id, choice_key)
);

CREATE TABLE quiz_attempts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  mode TEXT NOT NULL,
  chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
  topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
  score INT DEFAULT 0,
  total_questions INT DEFAULT 0,
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

CREATE TABLE user_answers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  attempt_id UUID REFERENCES quiz_attempts(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  mcq_id UUID REFERENCES mcqs(id) ON DELETE CASCADE,
  selected_choice_key TEXT,
  is_correct BOOLEAN,
  time_taken_seconds INT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE saved_pearls (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  mcq_id UUID REFERENCES mcqs(id) ON DELETE CASCADE,
  note TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
