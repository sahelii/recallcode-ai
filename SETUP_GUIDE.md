# RecallCode AI - Setup Guide

## Quick Start Checklist

Follow these steps in order to get RecallCode AI running:

### ✅ Step 1: Install Dependencies (COMPLETED)
- [x] Frontend dependencies installed (`npm install` in frontend/)
- [x] Backend dependencies installed (`pip install -r requirements.txt` in backend/)

### ⚠️ Step 2: Start Docker Desktop
**IMPORTANT**: Docker Desktop must be running before proceeding!

1. Open Docker Desktop application
2. Wait for it to fully start (whale icon in system tray)
3. Verify it's running by checking: `docker ps` in terminal

### Step 3: Start Database Services

Once Docker Desktop is running, execute:

```powershell
# From project root (D:\Project)
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache/broker (port 6379)

Verify services are running:
```powershell
docker-compose ps
```

### Step 4: Configure Environment Variables

#### Backend (.env)
The `.env` file has been created in `backend/`. Update it with your API keys:

```env
# Required for AI features (at least one)
OPENAI_API_KEY=your-openai-api-key-here
# OR
ANTHROPIC_API_KEY=your-anthropic-api-key-here
# OR
GROQ_API_KEY=your-groq-api-key-here

# Required for code execution
JUDGE0_API_KEY=your-judge0-api-key-here
```

**Note**: For MVP testing, you can skip AI and Judge0 keys initially, but some features won't work.

#### Frontend (.env.local)
The `.env.local` file has been created in `frontend/`. It should contain:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Run Database Migrations

```powershell
cd backend
.\venv\Scripts\python.exe manage.py migrate
```

### Step 6: Create Superuser (Optional)

```powershell
cd backend
.\venv\Scripts\python.exe manage.py createsuperuser
```

### Step 7: Start Backend Server

Open a new terminal window:

```powershell
cd backend
.\venv\Scripts\activate
python manage.py runserver
```

Backend will be available at: http://localhost:8000

### Step 8: Start Celery Worker (Required for Daily Plans)

Open another terminal window:

```powershell
cd backend
.\venv\Scripts\activate
celery -A recallcode worker -l info
```

### Step 9: Start Celery Beat (Required for Scheduled Tasks)

Open another terminal window:

```powershell
cd backend
.\venv\Scripts\activate
celery -A recallcode beat -l info
```

### Step 10: Start Frontend Server

Open another terminal window:

```powershell
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Running All Services

You'll need **5 terminal windows** running simultaneously:

1. **Terminal 1**: Django server (`python manage.py runserver`)
2. **Terminal 2**: Celery worker (`celery -A recallcode worker -l info`)
3. **Terminal 3**: Celery beat (`celery -A recallcode beat -l info`)
4. **Terminal 4**: Frontend dev server (`npm run dev`)
5. **Docker Desktop**: Running in background

## Testing the Application

1. Open browser: http://localhost:3000
2. Click "Sign up" to create an account
3. Login with your credentials
4. You'll be redirected to the dashboard
5. Try adding a problem: Click "Add Problem" button
6. Solve a problem and submit code
7. Check SRS reviews: Navigate to "Reviews" page

## Troubleshooting

### Docker Issues
- **Error**: "Docker Desktop is not running"
  - **Solution**: Start Docker Desktop application

### Database Connection Issues
- **Error**: "could not connect to server"
  - **Solution**: Make sure Docker containers are running: `docker-compose ps`
  - Restart containers: `docker-compose restart`

### Port Already in Use
- **Error**: "Port 8000/3000 already in use"
  - **Solution**: 
    - Find process: `netstat -ano | findstr :8000`
    - Kill process or change port in settings

### Migration Issues
- **Error**: "No changes detected"
  - **Solution**: Run `python manage.py makemigrations` first

### Celery Issues
- **Error**: "Connection refused" (Redis)
  - **Solution**: Make sure Redis container is running: `docker-compose ps`

## Next Steps After Setup

1. **Add API Keys**: Update `.env` with your AI provider and Judge0 keys
2. **Create Problems**: Add your first coding problem manually
3. **Test SRS**: Solve a problem, then check reviews after 24 hours
4. **Explore Features**: Try AI hints, code execution, daily plans

## Development Commands Reference

### Backend
```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\activate

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run Celery worker
celery -A recallcode worker -l info

# Run Celery beat
celery -A recallcode beat -l info
```

### Frontend
```powershell
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Docker
```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs

# Restart services
docker-compose restart
```

## API Endpoints

Once backend is running, you can access:

- **REST API**: http://localhost:8000/api/
- **GraphQL**: http://localhost:8000/graphql/
- **Admin Panel**: http://localhost:8000/admin/

## Need Help?

- Check the main README.md for detailed documentation
- Review error messages in terminal outputs
- Ensure all services are running before testing features

