# RecallCode AI

A lifelong coding brain for developers that combines spaced repetition (SRS), AI coaching, and LeetCode integration to help maintain long-term coding knowledge.

## Features

- **Spaced Repetition System (SRS)**: Custom SM-17 algorithm optimized for coding problems
- **AI Coach**: Context-aware hints and guidance using multiple AI providers (OpenAI, Anthropic, Groq)
- **LeetCode Integration**: Sync your LeetCode history and track progress (Phase 2)
- **Daily Plans**: Personalized 5-problem daily practice plans
- **Weakness Detection**: AI-powered analysis of your coding patterns and weak areas (Phase 2)
- **Code Execution**: Run and test code directly in the app using Judge0
- **PWA Support**: Offline-first Progressive Web App

## Tech Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Monaco Editor
- **Backend**: Django 5, Django REST Framework, Strawberry GraphQL
- **Database**: PostgreSQL with pgvector (Phase 2)
- **Cache/Broker**: Redis
- **Task Queue**: Celery with Celery Beat
- **Code Execution**: Judge0 API
- **AI**: Configurable (OpenAI, Anthropic, Groq)

## Project Structure

```
.
├── backend/          # Django backend
│   ├── users/        # User authentication and management
│   ├── problems/     # Problem CRUD and code execution
│   ├── srs/          # Spaced Repetition System
│   ├── coach/        # AI Coach interactions
│   ├── ai/           # AI hint generation
│   └── recallcode/   # Main Django project settings
├── frontend/         # Next.js frontend
│   ├── app/          # Next.js App Router pages
│   ├── components/   # React components
│   └── lib/          # API clients and utilities
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 14+ (or use Docker)
- Redis 7+ (or use Docker)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start PostgreSQL and Redis using Docker Compose:
```bash
cd ..
docker-compose up -d
```

6. Run migrations:
```bash
cd backend
python manage.py migrate
```

7. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

8. Start the Django development server:
```bash
python manage.py runserver
```

9. Start Celery worker (in a separate terminal):
```bash
cd backend
celery -A recallcode worker -l info
```

10. Start Celery beat (in another terminal):
```bash
cd backend
celery -A recallcode beat -l info
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Environment Variables

### Backend (.env)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=recallcode
DB_USER=recallcode
DB_PASSWORD=recallcode_dev
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

AI_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key

JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=your-judge0-api-key

FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user
- `POST /api/auth/password-reset/` - Request password reset

### Problems
- `GET /api/problems/problems/` - List problems
- `POST /api/problems/problems/` - Create problem
- `GET /api/problems/problems/{id}/` - Get problem
- `POST /api/problems/problems/{id}/submit_code/` - Submit code
- `GET /api/problems/submissions/` - List submissions
- `POST /api/problems/submissions/{id}/execute/` - Execute code

### SRS
- `GET /api/srs/reviews/due/` - Get due reviews
- `POST /api/srs/reviews/{id}/rate/` - Rate a review
- `GET /api/srs/plans/today/` - Get today's plan
- `POST /api/srs/plans/{id}/complete_problem/` - Mark problem as completed

### AI
- `POST /api/ai/hint/` - Generate AI hint
- `POST /api/coach/chat/` - Chat with AI coach

### GraphQL
- `POST /graphql/` - GraphQL endpoint

## Development

### Running Tests

```bash
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
cd backend
black .
isort .

# Frontend
cd frontend
npm run lint
```

## Deployment

### Backend

The backend can be deployed to:
- Railway
- Render
- Heroku
- AWS Elastic Beanstalk

### Frontend

The frontend can be deployed to:
- Vercel (recommended)
- Netlify
- AWS Amplify

### Database

- Railway PostgreSQL
- AWS RDS
- Google Cloud SQL

### Redis

- Upstash (recommended)
- AWS ElastiCache
- Redis Cloud

## Roadmap

### Phase 1 (MVP) - ✅ Completed
- [x] User authentication
- [x] Problem CRUD
- [x] SRS engine
- [x] Daily review queue
- [x] Code editor with Monaco
- [x] Basic AI hints
- [x] Dashboard
- [x] Judge0 integration
- [x] PWA support

### Phase 2 (AI-Powered) - In Progress
- [ ] LeetCode sync
- [ ] Weakness DNA mapping
- [ ] Enhanced AI coach
- [ ] Pattern extraction
- [ ] Smart daily plans

### Phase 3 (Full SaaS)
- [ ] System Design module
- [ ] Mock interview simulator
- [ ] Real-time LeetCode sync
- [ ] Community features
- [ ] Mobile app
- [ ] Subscription & billing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
