# Canvas Planner Backend

A Django REST API backend that integrates with Canvas LMS to provide enhanced planning and organization features for university students.

## Quick Start

### Option 1: Docker (Recommended for Development)

```bash
# Clone the repository
git clone <your-repo-url>
cd uofa_planner_django

# Edit Docker environment file with your Canvas credentials
# Edit .env.docker with your Canvas API token

# Build the Django containers
make docker-build

# Start all services (Django + PostgreSQL + Redis)
make docker-up

# Run initial migrations
make docker-migrate

# Your API will be available at http://localhost:8000
```

### Option 2: Local Development

```bash
# Create virtual environment and install dependencies
make venv

# Activate virtual environment
source venv/bin/activate

# Copy environment file and add your Canvas credentials
cp .env.example .env
# Edit .env with your Canvas API token

# Run migrations and start server
make migrate
make run
```

## Getting Canvas API Credentials

1. Log into your Canvas account
2. Go to Account → Settings
3. Scroll to "Approved Integrations"
4. Click "+ New Access Token"
5. Add a description and generate token
6. **Save the token immediately** (you can't see it again!)
7. Add it to your `.env` and `.env.docker` file

## Available Commands

### Local Development
- `make venv` - Create virtual environment and install dependencies
- `make install` - Install/update dependencies from requirements.txt
- `make migrate` - Run Django database migrations
- `make run` - Start Django development server
- `make test` - Run tests
- `make clean` - Remove virtual environment and cache files

### Docker Development
- `make docker-build` - Build Docker image
- `make docker-up` - Start all services (Django + PostgreSQL + Redis)
- `make docker-migrate` - Run database migrations in container
- `make docker-superuser` - Create superuser with username <whoami> (The output of that bash command) and password "admin"
- `make docker-down` - Stop all services
- `make docker-shell` - Open shell in Django container
- `make docker-logs` - View logs from all services
- `make docker-clean` - Remove all Docker containers and volumes

### All below is subject to change and has not been reviewed by Orion.

## API Endpoints

### Health Check
- `GET /api/health/` - Check API status and Canvas configuration

### Courses
- `GET /api/courses/` - List user's courses
- `GET /api/courses/?enrollment_state=all` - List all courses (active, past, future)
- `GET /api/courses/<id>/` - Get specific course details

### Assignments
- `GET /api/courses/<id>/assignments/` - List course assignments
- `GET /api/courses/<id>/assignments/<id>/` - Get assignment details

### Calendar & Profile
- `GET /api/calendar-events/` - Get calendar events
- `GET /api/profile/` - Get user profile

### Authentication
- `GET /api-auth/login/` - Django login page
- `GET /admin/` - Django admin interface

## Project Structure

```
├── canvas_backend/          # Main Django project
│   ├── settings.py         # Django settings with DRF and Canvas config
│   └── urls.py             # Root URL configuration
├── canvas_api/             # Canvas API integration app
│   ├── services.py         # Canvas API service layer
│   ├── serializers.py      # DRF serializers for data transformation
│   ├── views.py            # API views and endpoints
│   └── urls.py             # App URL patterns
├── docker/                 # Docker configuration
│   └── entrypoint.sh       # Container startup script
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-service Docker setup
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env.docker            # Docker environment template
└── Makefile               # Development commands
```

## Environment Variables

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Docker uses PostgreSQL, local uses SQLite)
DATABASE_URL=postgresql://postgres:postgres@db:5432/canvas_planner

# Canvas API Configuration
CANVAS_API_BASE_URL=https://canvas.ualberta.ca
CANVAS_API_TOKEN=your-canvas-api-token-here

# CORS Configuration  
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Cache Configuration (Docker uses Redis, local optional)
REDIS_URL=redis://redis:6379/0
```

## Development Features

### Docker Services
- **Django**: Main application server
- **PostgreSQL**: Production-like database
- **Redis**: Caching and session storage

### Built-in Features
- Django REST Framework with browsable API
- CORS headers for frontend integration
- Environment-based configuration
- Automatic admin user creation in Docker
- Request/response caching with Redis
- Canvas API service layer with error handling

## Testing Your Setup

```bash
# Test Canvas connection
python test_canvas_connection.py

# Check health endpoint
curl http://localhost:8000/api/health/

# Get your courses (requires authentication)
# Visit http://localhost:8000/admin/ to login first
curl http://localhost:8000/api/courses/
```

## Canvas API Notes

### Enrollment States
- `active` - Currently enrolled courses
- `all` - All courses (past, present, future)  
- `past` - Completed courses
- `future` - Upcoming courses
- `completed` - Finished courses

### Common Issues
- **Missing course names**: Courses may not be published yet by instructors
- **403 Forbidden**: Need to authenticate with Django first (visit `/admin/` to login)
- **Empty responses**: Some courses may be placeholders until term starts

### Rate Limits
Canvas has API rate limits. The service layer handles basic error cases, but for production you should implement:
- Exponential backoff
- Request queuing
- Cache-first strategies

## Next Steps

See `ROADMAP.md` for planned features and development phases.

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test with `make test` (local) or `make docker-shell` + `python manage.py test` (Docker)
4. Submit a pull request