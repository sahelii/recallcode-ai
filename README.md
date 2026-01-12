# RecallCode AI

A lifelong coding brain for developers that combines spaced repetition (SRS), AI coaching, and LeetCode integration to help maintain long-term coding knowledge.

## Features

- 🧠 **Spaced Repetition System (SRS)** - Custom SM-17 algorithm optimized for coding problems
- 🤖 **AI Coach** - Context-aware hints using OpenAI, Anthropic, or Groq
- 💻 **Code Execution** - Run and test code directly using Judge0
- 📅 **Daily Plans** - Personalized 5-problem daily practice plans
- 📊 **Progress Tracking** - Streak tracking and mastery metrics
- 📱 **PWA Support** - Installable as a Progressive Web App

## Tech Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Monaco Editor
- **Backend**: Django 5, Django REST Framework, Strawberry GraphQL
- **Database**: PostgreSQL
- **Cache/Broker**: Redis
- **Task Queue**: Celery
- **Code Execution**: Judge0 API
- **AI**: Configurable (OpenAI, Anthropic, Groq)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop

### Setup

1. **Start Docker services:**
```bash
docker-compose up -d
```

2. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

3. **Frontend setup (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

4. **Start Celery worker (new terminal):**
```bash
cd backend
source venv/bin/activate
celery -A recallcode worker -l info
```

5. **Start Celery beat (new terminal):**
```bash
cd backend
source venv/bin/activate
celery -A recallcode beat -l info
```

6. **Open browser:** http://localhost:3000

## Environment Variables

Create `backend/.env`:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=recallcode
DB_USER=recallcode
DB_PASSWORD=recallcode_dev
DB_HOST=localhost
DB_PORT=5433
REDIS_URL=redis://localhost:6379/0

# Optional: For AI features
OPENAI_API_KEY=your-key
JUDGE0_API_KEY=your-key
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
.
├── backend/          # Django backend
│   ├── users/       # Authentication
│   ├── problems/    # Problem management & code execution
│   ├── srs/         # Spaced repetition system
│   ├── coach/       # AI coach
│   └── ai/          # AI hint generation
├── frontend/         # Next.js frontend
└── docker-compose.yml
```

## API Endpoints

- REST API: http://localhost:8000/api/
- GraphQL: http://localhost:8000/graphql/
- Admin: http://localhost:8000/admin/

## License

MIT
