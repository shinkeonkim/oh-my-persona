# Video Serving Server

A FastAPI-based video streaming platform that supports user management, video uploads, and real-time video playback with advanced streaming features.

## Features

### User Management
- User registration and authentication
- User login/logout functionality
- User profile management and information updates

### Video Management
- Video upload functionality for registered users
- Video management dashboard for content creators
- Real-time video streaming and playback
- Streaming analytics and metrics

### Streaming Features
- Buffering optimization
- Playback position tracking and resume
- View count tracking and analytics
- Real-time streaming support

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL
- **Package Manager**: uv
- **Containerization**: Docker
- **Frontend**: (To be determined based on implementation needs)

## Architecture

The application follows a modern microservices architecture:
- FastAPI backend for API endpoints
- MySQL database for persistent data storage
- Docker containers for deployment and development
- Real-time streaming capabilities for video content

## Prerequisites

- Docker and Docker Compose
- uv (Python package manager)
- MySQL 8.0+

## Development Setup

1. **Environment Setup**
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Project Setup**
   ```bash
   # Clone and navigate to project
   cd video-serving-experiment

   # Install backend dependencies using uv
   uv sync

   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

3. **Docker Setup**
   ```bash
   # Build and start all services (backend, frontend, database)
   docker-compose up --build
   ```

4. **Database Migration**
   ```bash
   # Run database migrations (after containers are running)
   uv run alembic upgrade head
   ```

5. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/profile` - Update user profile

### Video Management
- `POST /api/videos/upload` - Upload video
- `GET /api/videos` - List videos
- `GET /api/videos/{video_id}` - Get video details
- `DELETE /api/videos/{video_id}` - Delete video (owner only)
- `PUT /api/videos/{video_id}` - Update video metadata

### Video Streaming
- `GET /api/stream/{video_id}` - Stream video content
- `POST /api/videos/{video_id}/view` - Record video view
- `GET /api/videos/{video_id}/analytics` - Get video analytics

## Configuration

Environment variables:
- `DATABASE_URL` - MySQL connection string
- `SECRET_KEY` - JWT secret key
- `UPLOAD_PATH` - Video file storage path
- `MAX_UPLOAD_SIZE` - Maximum video file size

## Development Guidelines

- Follow FastAPI best practices
- Use uv for dependency management
- Containerize all services with Docker
- Implement proper error handling and logging
- Follow REST API conventions
- Use MySQL for persistent storage

## Project Structure

```
video-serving-experiment/
├── app/                     # FastAPI Backend
│   ├── api/
│   │   ├── auth/           # Authentication endpoints
│   │   ├── videos/         # Video management endpoints
│   │   └── streaming/      # Video streaming endpoints
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   └── security.py     # Security utilities
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   └── services/           # Business logic
├── frontend/               # Svelte Frontend
│   ├── src/
│   │   ├── routes/         # Svelte pages
│   │   ├── components/     # Reusable components
│   │   ├── stores/         # State management
│   │   └── lib/            # API integration
│   ├── package.json
│   └── Dockerfile
├── alembic/                # Database migrations
├── docker-compose.yml      # Multi-container setup
├── Dockerfile             # Backend container
└── pyproject.toml         # Python dependencies
```
