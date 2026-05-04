# RoleFit - Intelligent Resume & Cover Letter Generation Platform

RoleFit is a sophisticated backend service that leverages AI to generate tailored resumes and cover letters based on job descriptions. It provides a comprehensive platform for managing user profiles, skills, experiences, and automatic document generation with intelligent content optimization.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Core Modules](#core-modules)
- [Database Schema](#database-schema)
- [Async Processing with Celery](#async-processing-with-celery)
- [Caching Strategy](#caching-strategy)
- [Configuration](#configuration)
- [Development](#development)

## 🎯 Overview

RoleFit is a FastAPI-based backend service designed to help job seekers create customized resumes and cover letters. The platform intelligently analyzes job descriptions and generates optimized documents that match the job requirements while maintaining authenticity.

### Problem Statement
Job seekers spend considerable time manually tailoring their resumes for each job application. RoleFit automates this process using AI to:
- Parse and understand job descriptions
- Extract relevant user skills and experiences
- Generate customized, ATS-friendly resumes
- Create compelling cover letters tailored to specific jobs
- Manage multiple document versions

## 🌟 Key Features

### User Management
- User registration and authentication
- Secure JWT-based authorization
- User profile management with customizable settings
- Account authentication with email verification

### Resume Management
- Multiple resume templates (Sidebar, Bold, Minimalist styles)
- Automatic resume generation from user profile data
- Resume extraction from uploaded PDF files
- Dynamic resume updates based on job descriptions
- PDF generation in multiple formats
- ATS-optimized resume structure

### Cover Letter Generation
- AI-powered cover letter creation
- Multiple template styles (Minimal, Professional, Creative)
- Job description-based content generation
- Dynamic PDF generation with formatting
- Cover letter caching for performance

### Job Description Management
- Import and store job descriptions
- Automated JD parsing and analysis
- Skill and requirement extraction
- Support for multiple job descriptions per user
- Job description caching and search

### Profile Data Management
The system manages comprehensive user profile information:
- **Profile**: Basic user information and preferences
- **Experience**: Work history with detailed descriptions
- **Education**: Academic qualifications and certifications
- **Skills**: Professional skills with proficiency levels
- **Tools/Technologies**: Technical tools and programming languages
- **Projects**: Portfolio projects with descriptions
- **Publications**: Research papers, articles, and publications
- **Achievements**: Certifications, awards, and recognitions

### Intelligent Features
- **AI-Powered Content Generation**: Uses Groq AI for intelligent content synthesis
- **Smart Filtering**: Filters user data based on job requirements
- **Caching Layer**: Redis-based caching for performance optimization
- **Real-time Updates**: WebSocket support for live document generation status
- **Async Processing**: Celery for background task processing

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Web Server                       │
│                    (Port 8000)                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        │          │          │          │
    ┌───▼──┐  ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
    │Users │  │Resume│  │Cover │  │  Job │
    │      │  │Letter│  │Letter│  │ Desc │
    └───┬──┘  └───┬──┘  └───┬──┘  └───┬──┘
        │         │         │         │
        └─────────┼─────────┼─────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
    ┌───▼──┐  ┌──▼──┐  ┌──▼──┐
    │  DB  │  │Redis│  │Celery
    │(PgSQL)  │Cache│  │Worker
    └───────┘  └─────┘  └──────┘
```

### Request Flow
1. **Client Request** → FastAPI Router
2. **Authentication** → JWT Validation
3. **Business Logic** → Service Layer
4. **Data Access** → Database/Cache
5. **Long Operations** → Celery Queue
6. **Response** → JSON Response or WebSocket Update

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** (0.135.2) - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** (2.12.5) - Data validation and settings management
- **Python** (3.9+)

### Database & Caching
- **PostgreSQL** (16-Alpine) - Primary database
- **Redis** (7-Alpine) - Caching layer and message broker
- **SQLAlchemy** - ORM for database operations

### AI & Content Generation
- **Groq** (1.2.0) - AI API for intelligent content generation
- **PDFMiner.six** (20251230) - PDF parsing and extraction
- **pdfplumber** (0.11.9) - PDF analysis
- **Pillow** (12.2.0) - Image processing for PDF generation

### Async & Background Jobs
- **Celery** - Distributed task queue
- **aioredis** (2.0.1) - Async Redis client
- **asyncio** - Async runtime

### Authentication & Security
- **python-jose** (3.5.0) - JWT token handling
- **bcrypt** (3.2.0) - Password hashing
- **passlib** (1.7.4) - Password utilities
- **cryptography** (47.0.0) - Encryption utilities

### Utilities
- **python-dotenv** - Environment configuration
- **httpx** - Async HTTP client
- **email-validator** - Email validation
- **PyYAML** - Configuration parsing

## 📁 Project Structure

```
rolefit-backend/
├── app/
│   ├── api/
│   │   ├── router.py                 # Main API router
│   │   └── v1/                       # API v1 endpoints
│   │       ├── auth/                 # Authentication endpoints
│   │       ├── user/                 # User management
│   │       ├── profile/              # User profile management
│   │       ├── resume/               # Resume generation endpoints
│   │       ├── cover_letter/         # Cover letter endpoints
│   │       ├── job_description/      # Job description endpoints
│   │       ├── experience/           # Work experience endpoints
│   │       ├── academics/            # Education endpoints
│   │       ├── skill/                # Skills management
│   │       ├── tools/                # Tools/technologies management
│   │       ├── project/              # Portfolio projects
│   │       ├── publications/         # Publications management
│   │       ├── resume_extractor/     # PDF resume extraction
│   │       ├── content/              # Content retrieval
│   │       ├── health/               # Health check endpoint
│   │       └── websocket/            # WebSocket connections
│   │
│   ├── core/
│   │   ├── AppError.py               # Custom exception handling
│   │   ├── celery_app.py             # Celery configuration
│   │   ├── cors.py                   # CORS setup
│   │   ├── logger.py                 # Logging configuration
│   │   ├── redis_keys.py             # Redis key constants
│   │   ├── validation_error.py       # Validation utilities
│   │   ├── expectations.py           # Expectation validations
│   │   ├── grok_const.py             # Groq AI constants
│   │   ├── sarvam_const.py           # Sarvam AI constants
│   │   └── resume_colors.py          # Resume styling constants
│   │
│   ├── db/
│   │   ├── db.py                     # SQLAlchemy setup
│   │   └── redis_db.py               # Redis connection
│   │
│   ├── models/
│   │   ├── User.py                   # User model
│   │   ├── Profile.py                # User profile model
│   │   ├── Experience.py             # Work experience model
│   │   ├── Academic.py               # Education model
│   │   ├── Skill.py                  # Skills model
│   │   ├── Tool.py                   # Tools/technologies model
│   │   ├── Project.py                # Portfolio projects model
│   │   ├── Publication.py            # Publications model
│   │   ├── Achievement.py            # Achievements/certifications
│   │   ├── JobDescription.py         # Job description model
│   │   ├── GeneratedDocument.py      # Generated resumes/letters
│   │   ├── UserSkill.py              # User-skill relationship
│   │   └── UserTool.py               # User-tool relationship
│   │
│   ├── schema/
│   │   ├── auth.py                   # Authentication schemas
│   │   ├── pdf_resume.py             # PDF resume schemas
│   │   ├── CoverLetterData.py        # Cover letter data schemas
│   │   ├── Academic.py               # Academic schemas
│   │   ├── Experience.py             # Experience schemas
│   │   ├── Skill.py                  # Skill schemas
│   │   ├── Tool.py                   # Tool schemas
│   │   ├── Project.py                # Project schemas
│   │   ├── Publication.py            # Publication schemas
│   │   ├── JobDescription.py         # Job description schemas
│   │   └── GeneratedDocument.py      # Generated document schemas
│   │
│   ├── response/
│   │   ├── user_responses.py         # User response schemas
│   │   ├── profile_responses.py      # Profile response schemas
│   │   ├── experience_responses.py   # Experience responses
│   │   ├── academic_responses.py     # Academic responses
│   │   ├── skill_responses.py        # Skill responses
│   │   ├── tool_responses.py         # Tool responses
│   │   ├── project_responses.py      # Project responses
│   │   ├── publication_responses.py  # Publication responses
│   │   ├── GenerateDocument_responses.py  # Document responses
│   │   └── job_description_response.py   # Job description responses
│   │
│   ├── helpers/
│   │   ├── redis_cache_helpers.py    # Redis caching utilities
│   │   ├── db_helpers.py             # Database helper functions
│   │   ├── pdf_helpers.py            # PDF generation utilities
│   │   ├── jd_parser.py              # Job description parsing
│   │   ├── filter_jd.py              # Job description filtering
│   │   ├── filter_jd_sync.py         # Sync JD filtering
│   │   ├── resume_prompt.py          # Resume generation prompts
│   │   ├── cover_letter_prompt.py    # Cover letter prompts
│   │   ├── build_pdf.py              # Base PDF builder
│   │   ├── build_pdf_bold.py         # Bold resume template
│   │   ├── build_pdf_minimalist.py   # Minimalist resume template
│   │   ├── build_pdf_sidebar.py      # Sidebar resume template
│   │   ├── build_cover_letter_pdf.py # Cover letter PDF builder
│   │   ├── build_cover_letter_bold.py # Bold cover letter template
│   │   ├── build_cover_letter_minimal.py # Minimal cover letter template
│   │   ├── celery_helpers.py         # Celery task helpers
│   │   ├── grok_ai_headers.py        # Groq API headers
│   │   ├── sarvam_ai_headers.py      # Sarvam API headers
│   │   └── validation_schemas.py     # Data validation
│   │
│   ├── dependency/
│   │   └── dependencies.py           # FastAPI dependency injection
│   │
│   ├── tasks/
│   │   └── [Celery async tasks]     # Background job tasks
│   │
│   ├── utils/
│   │   └── [Utility functions]      # General utilities
│   │
│   ├── validators/
│   │   └── [Data validators]        # Validation logic
│   │
│   └── websockets/
│       ├── redis_subscriber.py       # Redis WebSocket subscriber
│       └── [WebSocket handlers]     # Real-time communication
│
├── docker/
│   └── init.sql/                     # Database initialization scripts
│
├── logs/                             # Application logs
│
├── tests/                            # Test suite
│   ├── test_resume_generation.py
│   ├── test_enum_parsing.py
│   ├── test_requirements.txt
│   └── ...
│
├── env/                              # Python virtual environment
│
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── docker-compose.yml                # Docker compose configuration
├── Dockerfile                        # Docker image build
├── run_celery_worker.py              # Celery worker runner
├── run_celery_beat.py                # Celery beat scheduler runner
└── debug_celery.py                   # Celery debugging script
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9 or higher
- Docker and Docker Compose (for containerized setup)
- PostgreSQL 16 (if not using Docker)
- Redis 7 (if not using Docker)
- Git

### Local Setup (without Docker)

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rolefit.git
cd rolefit/rolefit-backend
```

#### 2. Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file in the `rolefit-backend` directory:
```env
# Database
DATABASE_URL=postgresql://rolefit:secret@localhost:5432/rolefit

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI APIs
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=mixtral-8x7b-32768

# Email (if needed)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Application
APP_NAME=RoleFit
DEBUG=True
```

#### 5. Initialize Database
```bash
# Ensure PostgreSQL is running
psql -U rolefit -d rolefit -f docker/init.sql/init.sql
```

#### 6. Run the Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Setup

#### 1. Build and Run with Docker Compose
```bash
cd rolefit
docker-compose up -d
```

This will start:
- **Backend API** (http://localhost:8000)
- **PostgreSQL Database** (localhost:5432)
- **Redis Cache** (localhost:6379)
- **Celery Worker** (background tasks)

#### 2. View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f postgres
```

#### 3. Stop Services
```bash
docker-compose down
```

## 🏃 Running the Application

### Development Server
```bash
# Standard run
uvicorn main:app --reload

# With specific host and port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Celery Worker (Background Tasks)
```bash
python run_celery_worker.py
# or
celery -A app.core.celery_app worker -l info
```

### Celery Beat (Scheduled Tasks)
```bash
python run_celery_beat.py
# or
celery -A app.core.celery_app beat -l info
```

### Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📡 API Endpoints

### Authentication Endpoints (`/api/v1/auth`)
- `POST /signup` - Register new user
- `POST /login` - User login with email/password
- `POST /refresh-token` - Refresh JWT token
- `POST /logout` - User logout

### User Endpoints (`/api/v1/user`)
- `GET /` - Get current user profile
- `GET /{user_id}` - Get user by ID
- `PUT /{user_id}` - Update user information
- `DELETE /{user_id}` - Delete user account

### Profile Endpoints (`/api/v1/profile`)
- `GET /` - Get user profile
- `POST /` - Create profile
- `PUT /` - Update profile
- `DELETE /` - Delete profile

### Resume Endpoints (`/api/v1/resume`)
- `GET /` - Get all resumes
- `POST /generate` - Generate resume from profile
- `POST /generate-tailored` - Generate tailored resume for job
- `GET /{resume_id}/download` - Download resume as PDF
- `PUT /{resume_id}` - Update resume
- `DELETE /{resume_id}` - Delete resume

### Cover Letter Endpoints (`/api/v1/cover-router`)
- `GET /` - Get all cover letters
- `POST /generate` - Generate cover letter
- `GET /{letter_id}/download` - Download cover letter as PDF
- `PUT /{letter_id}` - Update cover letter
- `DELETE /{letter_id}` - Delete cover letter

### Job Description Endpoints (`/api/v1/job-descriptions`)
- `GET /` - Get all job descriptions
- `POST /` - Create/import job description
- `GET /{jd_id}` - Get specific job description
- `PUT /{jd_id}` - Update job description
- `DELETE /{jd_id}` - Delete job description
- `POST /parse` - Parse and extract job requirements

### Experience Endpoints (`/api/v1/experience`)
- `GET /` - Get all work experiences
- `POST /` - Add new experience
- `PUT /{exp_id}` - Update experience
- `DELETE /{exp_id}` - Delete experience

### Education Endpoints (`/api/v1/academics`)
- `GET /` - Get all education records
- `POST /` - Add new education
- `PUT /{academic_id}` - Update education
- `DELETE /{academic_id}` - Delete education

### Skills Endpoints (`/api/v1/skills`)
- `GET /` - Get all skills
- `POST /` - Add skill
- `PUT /{skill_id}` - Update skill
- `DELETE /{skill_id}` - Delete skill

### Tools/Technologies Endpoints (`/api/v1/tools`)
- `GET /` - Get all tools
- `POST /` - Add tool
- `PUT /{tool_id}` - Update tool
- `DELETE /{tool_id}` - Delete tool

### Projects Endpoints (`/api/v1/project`)
- `GET /` - Get all projects
- `POST /` - Add project
- `PUT /{project_id}` - Update project
- `DELETE /{project_id}` - Delete project

### Publications Endpoints (`/api/v1/publications`)
- `GET /` - Get all publications
- `POST /` - Add publication
- `PUT /{pub_id}` - Update publication
- `DELETE /{pub_id}` - Delete publication

### Resume Extractor Endpoints (`/api/v1/resume-extractor`)
- `POST /upload` - Upload and extract resume from PDF
- `GET /status/{task_id}` - Check extraction status

### Content Endpoints (`/api/v1/content`)
- `GET /{content_id}` - Get generated content (resume/cover letter)

### Health Check Endpoints (`/api/v1/health`)
- `GET /` - Check API health status

### WebSocket Endpoints (`/api/v1/websocket`)
- `WS /connect` - Connect to real-time updates

## 🧩 Core Modules

### Authentication Module (`app/api/v1/auth`)
Handles user authentication, JWT token generation, and password management.
- Email/password registration
- JWT-based authentication
- Secure password hashing with bcrypt
- Token refresh mechanism

### Resume Generation Module (`app/api/v1/resume`)
Core functionality for resume creation and customization.
- **Features**:
  - Multiple resume templates (Sidebar, Bold, Minimalist)
  - Smart resume tailoring based on job descriptions
  - ATS-optimized formatting
  - Real-time PDF generation
  - Version control and storage

- **Templates**:
  - **Bold**: Professional template with emphasis on achievements
  - **Sidebar**: Modern template with sidebar for quick info
  - **Minimalist**: Clean and simple design

### Cover Letter Generation Module (`app/api/v1/cover_letter`)
Automated cover letter creation with AI assistance.
- **Features**:
  - AI-powered content generation using Groq
  - Multiple writing styles
  - Job description matching
  - PDF generation with professional formatting
  - Caching for performance

- **Templates**:
  - **Minimal**: Concise professional format
  - **Bold**: Emphasizes achievements
  - **Creative**: Personalized and engaging style

### Job Description Parsing Module (`app/api/v1/job_description`)
Intelligent parsing and analysis of job descriptions.
- **Features**:
  - Automatic skill extraction
  - Requirement analysis
  - Keyword identification
  - Salary range extraction
  - Technology stack detection

### Resume Extractor Module (`app/api/v1/resume_extractor`)
Automated resume parsing from PDF files.
- **Features**:
  - PDF parsing and text extraction
  - Information structuring
  - Automatic field detection
  - Data validation
  - Error handling for malformed PDFs

### Caching Layer (`app/helpers/redis_cache_helpers.py`)
Redis-based caching for performance optimization.
- **Features**:
  - User authentication cache
  - Resume cache
  - Job description cache
  - Cover letter cache
  - Configurable TTL (Time To Live)

## 🗄️ Database Schema

### Core Tables

#### Users Table
```
id: UUID (Primary Key)
email: String (Unique)
password_hash: String
created_at: Timestamp
updated_at: Timestamp
is_active: Boolean
is_verified: Boolean
```

#### User Profile
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
first_name: String
last_name: String
phone: String
location: String
headline: String
summary: String
profile_picture_url: String
```

#### Experience
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
job_title: String
company: String
employment_type: String
start_date: Date
end_date: Date (nullable)
description: Text
is_current: Boolean
```

#### Academic
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
school: String
degree: String
field_of_study: String
start_date: Date
end_date: Date
grade: String (nullable)
activities: Text (nullable)
```

#### Skills
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
skill_name: String
proficiency_level: Enum (Beginner, Intermediate, Advanced, Expert)
endorsements: Integer (default: 0)
```

#### Tools/Technologies
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
tool_name: String
experience_level: String
years_of_experience: Integer
```

#### Projects
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
project_name: String
description: Text
technologies_used: String[] (array)
start_date: Date
end_date: Date (nullable)
project_url: String (nullable)
```

#### Job Descriptions
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
job_title: String
company: String
job_description: Text
required_skills: String[] (array)
preferred_skills: String[] (array)
imported_at: Timestamp
saved_at: Timestamp
```

#### Generated Documents
```
id: UUID (Primary Key)
user_id: UUID (Foreign Key)
job_description_id: UUID (Foreign Key, nullable)
document_type: Enum (Resume, CoverLetter)
template_type: String
content_json: JSON
generated_at: Timestamp
file_path: String
status: Enum (Processing, Completed, Failed)
```

## ⚙️ Async Processing with Celery

### What is Celery?
Celery is a distributed task queue that allows the application to execute long-running operations asynchronously.

### Configured Tasks

1. **Resume PDF Generation**
   - Generates resume PDF in background
   - Notifies user via WebSocket when complete
   - Stores file for download

2. **Cover Letter PDF Generation**
   - Generates cover letter PDF asynchronously
   - Supports multiple templates
   - Real-time progress updates

3. **Resume Extraction from PDF**
   - Parses uploaded resume files
   - Extracts and structures information
   - Validates extracted data

4. **Job Description Parsing**
   - Parses job postings
   - Extracts skills and requirements
   - Identifies key technologies

### Running Celery Components

```bash
# Start worker
python run_celery_worker.py

# Start scheduler (for periodic tasks)
python run_celery_beat.py

# Monitor tasks (in another terminal)
celery -A app.core.celery_app events
```

## 💾 Caching Strategy

### Redis Cache Implementation

The application uses Redis for caching with the following strategy:

1. **Authentication Cache**
   - Cache authenticated user objects
   - TTL: 30 minutes
   - Invalidated on logout or password change

2. **User Data Cache**
   - Cache user profile, skills, experiences
   - TTL: 15 minutes
   - Invalidated on profile update

3. **Job Description Cache**
   - Cache parsed job descriptions
   - TTL: 1 hour
   - Invalidated on JD update

4. **Resume/Cover Letter Cache**
   - Cache generated documents
   - TTL: 2 hours
   - Invalidated on content update

### Cache Functions

```python
# Get cached value
value = await get_cache(key)

# Set cached value with TTL
await set_cache(key, value, ttl=300)

# Delete cached value
await delete_cache(key)

# Invalidate user cache
await invalidate_user_cache(user_id)
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/rolefit

# Redis Configuration
REDIS_URL=redis://localhost:6379

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq AI Configuration
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=mixtral-8x7b-32768

# Application Settings
APP_NAME=RoleFit
DEBUG=False
LOG_LEVEL=INFO

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

### Application Settings
Key configuration files:
- `app/core/celery_app.py` - Celery configuration
- `app/core/cors.py` - CORS policy setup
- `app/core/logger.py` - Logging configuration
- `app/db/db.py` - Database configuration

## 👨‍💻 Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_resume_generation.py

# Run with coverage
pytest --cov=app tests/
```

### Code Structure Best Practices

1. **Service Layer**: Business logic in `*_service.py` files
2. **Router Layer**: API endpoints in `*_router.py` files
3. **Schema Layer**: Data validation in `schema/` directory
4. **Response Layer**: Response formatting in `response/` directory
5. **Models**: Database models in `models/` directory

### Adding New Features

1. Create model in `app/models/`
2. Create schema in `app/schema/`
3. Create response schema in `app/response/`
4. Create service in `app/api/v1/[feature]/`
5. Create router in `app/api/v1/[feature]/`
6. Add route to `app/api/v1/router.py`

### Debugging

Enable debug logging:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

View logs:
```bash
# Docker logs
docker-compose logs -f backend

# Local logs
tail -f logs/app.log
```

## 📊 Performance Considerations

1. **Database Queries**: Use efficient queries with proper indexing
2. **Caching**: Leverage Redis for frequently accessed data
3. **PDF Generation**: Offload to Celery workers
4. **File Storage**: Store PDFs efficiently with proper cleanup
5. **API Rate Limiting**: Consider implementing rate limits for public endpoints

## 🔐 Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Password Hashing**: bcrypt with salt for password security
3. **CORS**: Configurable CORS policy
4. **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
5. **Input Validation**: Pydantic schema validation on all inputs
6. **Error Handling**: Custom error handlers prevent information leakage

## 📝 API Response Format

### Success Response
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "John Doe"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/feature-name`
2. Commit changes: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/feature-name`
4. Create Pull Request

## 📄 License

[Your License Here]

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Contact: support@rolefit.com

## 🚀 Deployment

### Production Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Update `SECRET_KEY` with strong random value
- [ ] Configure production database
- [ ] Configure production Redis instance
- [ ] Set up SSL/TLS certificates
- [ ] Configure proper CORS origins
- [ ] Set up logging and monitoring
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Load test the application

### Recommended Hosting
- **API Server**: AWS ECS, Google Cloud Run, or Heroku
- **Database**: AWS RDS PostgreSQL
- **Cache**: AWS ElastiCache Redis
- **File Storage**: AWS S3
- **Task Queue**: Celery with managed Redis

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Version**: 1.0.0  
**Last Updated**: May 2026  
**Maintainer**: RoleFit Team
