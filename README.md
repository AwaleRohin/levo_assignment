# Flask + React Survey Application

A full-stack survey web application built with Flask backend and React frontend, featuring background task processing with Celery & Redis, and PostgreSQL for data persistence.

## 🏗️ Architecture

- **Backend**: Flask (Python) with Docker containerization
- **Frontend**: React with Vite
- **Database**: PostgreSQL
- **Message Broker**: Redis
- **Background Tasks**: Celery
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js (v16+ recommended)
- npm or yarn

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/AwaleRohin/levo_assignment.git
   cd levo_assignment
   ```
### Backend Setup (Flask)

1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

2. **Environment Configuration**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit the .env file with your configuration
   nano .env  # or use your preferred editor
   ```

3. **Start the Backend Services**
   ```bash
   # Build and start all services (PostgreSQL, Redis, Flask, Celery)
   docker compose up --build
   
   # Or run in background
   docker compose up -d --build
   ```

### Frontend Setup (React)

1. **Navigate to the frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

The React app will be available at `http://localhost:5173` (default Vite port).

## 🐳 Docker Services

The application uses Docker Compose to orchestrate the following services:

- **Flask App**: Main backend application
- **PostgreSQL**: Primary database
- **Redis**: Cache and message broker for Celery
- **Celery Worker**: Background task processor
- **Celery Beat**: Task scheduler

### Docker Commands

```bash
# Start all services
docker-compose up

# Start services in background
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend

# Rebuild services
docker compose up --build

# Access Flask app container
docker compose exec backend-backend-1 bash
```

## ⚙️ Environment Configuration

Create a `.env` file based on `.env.example` and update the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@postgres:5432/dbname

# Flask Configuration
FLASK_ENV=development
FLASK_APP=survey/wsgi.py

# Celery Configuration
REDIS_BROKER_URL=redis://redis:6379/0
REDIS_RESULT_BACKEND=redis://redis:6379/0
```

## 🔧 Development Workflow

### Backend Development

1. Make changes to your Flask code
2. The Docker container will automatically reload if you have volume mounts configured
3. Check logs: `docker compose logs -f backend`

### Frontend Development

1. Make changes to your React code
2. Vite will automatically reload the browser
3. The dev server runs on `http://localhost:5173`

### Background Tasks

- Celery workers process background tasks
- Celery Beat handles scheduled tasks
- Monitor tasks through logs: `docker compose logs -f celery_worker`

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 5000, 5173, 5432, and 6379 are available
2. **Database connection**: Ensure PostgreSQL is running and credentials are correct
3. **Redis connection**: Verify Redis is accessible for Celery tasks
4. **Docker issues**: Try `docker compose down` and `docker compose up --build`


## 🧪 Testing
```bash
# Backend tests (run inside Flask container)
cd backend
docker compose exec backend pytest
```

### Logs

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs backend
docker compose logs postgres
docker compose logs redis
docker compose logs celery_worker
```

## 🛠️ Future Improvements

Currently, the application allows **anyone to create, edit, or delete surveys without authentication or ownership restrictions**. With more time, the following improvements would be made:

- **User Authentication & Authorization**  
  Introduce user accounts and associate each survey with its creator. This would ensure:
  - Only authenticated users can create surveys  
  - Users can only view or edit their own surveys  
  - Access control is enforced both on the frontend and backend

- **Survey Integration with External Platforms**  
  Enable integration with platforms like **Google Forms**, **SurveyMonkey**, and **JotForm** to import responses into our system:  
  - Use **webhooks** for real-time syncing of survey responses  
  - Alternatively, set up **periodic background tasks** (e.g., every 10–15 minutes via Celery Beat) to poll external APIs for new responses

- **Admin Panel**  
  Add an administrative interface to manage users, surveys, and system-wide settings.

- **Improved Validation & Error Handling**  
  Add robust input validation and better error 

## 📞 Support

For questions or issues, please [create an issue](https://github.com/AwaleRohin/levo_assignment/issues) or contact [rohinawale331@gmail.com].
