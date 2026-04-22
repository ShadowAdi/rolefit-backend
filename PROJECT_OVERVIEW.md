# RoleFit Backend - Project Overview

## 🚀 Project Summary

**RoleFit** is a comprehensive RESTful API backend built with **FastAPI** for managing professional profiles, experience, skills, projects, and academic records. The system allows users to register, authenticate, and build a complete professional portfolio with structured data management.

---

## 📋 Architecture

### Tech Stack
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy ORM (SQL-based)
- **Authentication**: JWT (JSON Web Tokens)
- **API Version**: v1 (Versioned API structure)
- **Container**: Docker & Docker Compose

### Project Structure
```
app/
├── api/              # API routes and endpoints
│   └── v1/
│       ├── health/   # Health check endpoints
│       ├── auth/     # Authentication endpoints
│       ├── user/     # User management endpoints
│       ├── profile/  # User profile endpoints
│       ├── academics/# Academic records endpoints
│       ├── experience/# Work experience endpoints
│       ├── project/  # Project portfolio endpoints
│       ├── publications/# Publications endpoints
│       ├── skill/    # Skills management endpoints
│       └── tools/    # Tools/Technologies endpoints
├── core/             # Core utilities (CORS, logging, errors)
├── db/               # Database connection and setup
├── dependency/       # Dependency injection
├── models/           # Database models
├── schema/           # Request/Response validation schemas
├── response/         # Response formatters
├── validators/       # Input validation logic
├── helpers/          # Helper functions
└── utils/            # Utility functions
```

---

## 🔌 API Endpoints Overview

### 1. **Health Check** `/health`
**Service**: `HealthService`
- **Purpose**: Monitor API health status
- **Endpoints**:
  - `GET /health` - Get system health status

---

### 2. **Authentication** `/auth`
**Service**: `AuthServiceClass`
- **Purpose**: User authentication and token management
- **Endpoints**:
  - `POST /auth/login` - User login (email + password) → Returns JWT token

---

### 3. **User Management** `/user`
**Service**: `UserService`
- **Purpose**: Handle user account operations
- **Endpoints**:
  - `POST /user/register` - Create new user account
  - `GET /user/me` - Get current authenticated user details
  - `UPDATE /user/{user_id}` - Update user information
  - `DELETE /user/{user_id}` - Delete user account

---

### 4. **Profile** `/profile`
**Service**: `ProfileServiceClass`
- **Purpose**: Manage user professional profile (headline, summary, links)
- **Endpoints**:
  - `POST /profile` - Create user profile
  - `GET /profile/{profile_id}` - Get profile details
  - `GET /profile/user/{user_id}` - Get profile by user ID
  - `PUT /profile/{profile_id}` - Update profile information
  - `DELETE /profile/{profile_id}` - Delete profile

---

### 5. **Skills** `/skills`
**Service**: `SkillServiceClass`
- **Purpose**: Manage technical and professional skills
- **Endpoints**:
  - `POST /skills` - Create new skill
  - `GET /skills/{skill_id}` - Get skill details
  - `GET /skills/user/{user_id}` - List all skills for a user
  - `PUT /skills/{skill_id}` - Update skill information
  - `DELETE /skills/{skill_id}` - Delete skill
  - `POST /skills/user/add` - Add skill to user profile

---

### 6. **Tools/Technologies** `/tools`
**Service**: `ToolServiceClass`
- **Purpose**: Manage tools and technologies used by user
- **Endpoints**:
  - `POST /tools` - Create new tool
  - `GET /tools/{tool_id}` - Get tool details
  - `GET /tools/user/{user_id}` - List all tools for a user
  - `PUT /tools/{tool_id}` - Update tool information
  - `DELETE /tools/{tool_id}` - Delete tool
  - `POST /tools/user/add` - Add tool to user profile

---

### 7. **Experience** `/experience`
**Service**: `ExperienceServiceClass`
- **Purpose**: Manage professional work experience records
- **Endpoints**:
  - `POST /experience` - Create work experience record
  - `GET /experience/{experience_id}` - Get experience details
  - `GET /experience/user/{user_id}` - List all experiences for user
  - `PUT /experience/{experience_id}` - Update experience details
  - `DELETE /experience/{experience_id}` - Delete experience
  
**Data Captured**: Company name, job role, tech stack, employment type, location, start/end dates, description

---

### 8. **Academics** `/academics`
**Service**: `AcademicServiceClass`
- **Purpose**: Manage educational background and qualifications
- **Endpoints**:
  - `POST /academics` - Create academic record
  - `GET /academics/{academic_id}` - Get academic details
  - `GET /academics/user/{user_id}` - List all academic records for user
  - `PUT /academics/{academic_id}` - Update academic information
  - `DELETE /academics/{academic_id}` - Delete academic record

**Data Captured**: Degree name, college/university, description, start/end dates, links

---

### 9. **Projects** `/project`
**Service**: `ProjectService`
- **Purpose**: Showcase portfolio projects
- **Endpoints**:
  - `POST /project` - Create new project
  - `GET /project/{project_id}` - Get project details
  - `GET /project/user/{user_id}` - List all projects for user
  - `PUT /project/{project_id}` - Update project information
  - `DELETE /project/{project_id}` - Delete project

**Data Captured**: Title, description, tech stack, links, start/end dates

---

### 10. **Publications** `/publications`
**Service**: `PublicationServiceClass`
- **Purpose**: Manage published articles, research papers, and writings
- **Endpoints**:
  - `POST /publications` - Create publication record
  - `GET /publications/{publication_id}` - Get publication details
  - `GET /publications/user/{user_id}` - List all publications for user
  - `PUT /publications/{publication_id}` - Update publication details
  - `DELETE /publications/{publication_id}` - Delete publication

**Data Captured**: Title, publisher, publication date, authors, description, URL

---

## 🗄️ Database Models

The system includes the following data models:

1. **User** - User account credentials and basic info
2. **Profile** - Professional profile (headline, summary, links)
3. **Academic** - Educational records
4. **Achievement** - Achievements and certifications
5. **Experience** - Work experience history
6. **Project** - Portfolio projects
7. **Publication** - Published articles/papers
8. **Skill** - Technical/professional skills
9. **Tool** - Tools and technologies
10. **UserSkill** - Linking users to skills
11. **UserTool** - Linking users to tools

---

## 🔐 Authentication & Authorization

- **Method**: JWT (JSON Web Tokens)
- **Protected Endpoints**: All profile-related endpoints require authentication via `get_current_user` dependency
- **Token Format**: Bearer token in Authorization header

```
Authorization: Bearer <jwt_token>
```

---

## 📊 Key Features

✅ User registration and authentication  
✅ JWT-based secure authentication  
✅ Comprehensive profile management  
✅ Multi-section portfolio building (projects, experience, academics, publications)  
✅ Skills and tools inventory management  
✅ Structured data with validation  
✅ Error handling and logging  
✅ CORS support  
✅ Docker containerization  
✅ API versioning (v1)  

---

## 🛠️ Technology Stack Details

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic (via FastAPI schemas) |
| Authentication | JWT |
| Database | SQL (PostgreSQL/MySQL compatible) |
| Containerization | Docker & Docker Compose |
| Logging | Custom logger in core module |
| Error Handling | Custom AppError class |

---

## 📌 Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Operation successful",
  "data": {...},
  "timestamp": "2024-04-22T10:30:00Z"
}
```

---

## 🚦 Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## 📝 Running the Application

### Using Docker
```bash
docker-compose up
```

### Using Python (Development)
```bash
python main.py
```

---

## 📦 Dependencies

See `requirements.txt` for complete list of Python packages

---

## 🎯 API Usage Flow

1. **Register** → `POST /user/register` (Create account)
2. **Login** → `POST /auth/login` (Get JWT token)
3. **Create Profile** → `POST /profile` (Set up profile)
4. **Add Content** → Create academic, experience, projects, publications
5. **Manage Skills/Tools** → Add skills and tools to profile
6. **Retrieve Data** → GET endpoints for viewing information

---

## 📞 Support

For questions or issues with the RoleFit backend API, refer to the API documentation endpoints or check the response messages for error details.

---

**Last Updated**: April 2026  
**API Version**: v1  
**Status**: Active Development
