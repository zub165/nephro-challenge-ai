# 🧠 Nephro Challenge AI

**AI-Powered Medical Quiz Platform for Nephrologists & Students**

Nephro Challenge AI is a full-stack medical quiz game designed for board review and continuous learning in nephrology and internal medicine. Built with Django, React, and Flutter.

## ✨ Features

- **Daily Case Challenge** — One new case every day with streak tracking
- **Board Review Mode** — 1,000+ questions across 10+ nephrology categories
- **AI Tutor** — GPT-powered explanations, clinical pearls, and similar question generation
- **Leaderboards** — Daily, weekly, monthly, and all-time rankings
- **Dark/Light Mode** — Comfortable studying day or night
- **Cross-Platform** — Web admin panel + native Android/iOS apps

## 🛠 Stack

| Layer | Tech |
|-------|------|
| Backend | Django + DRF + PostgreSQL |
| Web | React + Vite + TypeScript + Tailwind |
| Mobile | Flutter (Android & iOS) |
| AI | OpenAI GPT API |
| Auth | JWT + Google/Apple OAuth |

## 🚀 Quick Start

### Backend
```bash
cd backend && pip install -r requirements.txt
cp .env.example .env  # Configure your DB & API keys
python manage.py migrate && python manage.py seed_data
python manage.py runserver
```

### Web
```bash
cd web && npm install && npm run dev
```

### Mobile
```bash
cd mobile && flutter pub get && flutter run
```

## 📚 Docs
See [context.md](context.md) for full documentation.

> **For medical education only. Not medical advice.**
