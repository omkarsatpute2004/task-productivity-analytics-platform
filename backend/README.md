# Phase 1 — Database & Backend Foundation

## Project Overview
**Task Management & Productivity Analytics Platform** — Phase 1 establishes a clean, production-ready PostgreSQL database foundation and FastAPI backend structure designed to support future task management features, authentication, and productivity analytics.

---

## Technology Stack
- **Python**: 3.11+ (Python 3.12 compatible)
- **FastAPI**: Modern web framework for high-performance APIs
- **PostgreSQL**: Relational database (v16+)
- **SQLAlchemy 2.x**: Object Relational Mapper with modern type hints
- **Alembic**: Database migration management
- **Pydantic / Pydantic Settings**: Data validation and environment settings configuration
- **pytest & httpx**: Automated unit & integration test suite

---

## Database Schema & Relationships

The database schema consists of four core relational tables:

```text
USER (users)
  │
  │ 1 : many
  ▼
TASK (tasks) ──(1 : many)──► TASK_ACTIVITY (task_activity)
  ▲
  │ many : 1
  │
CATEGORY (categories)
```

### Tables Summary

1. **`users`**
   - Fields: `id`, `name`, `email` (unique, indexed), `password_hash`, `role` (`ADMIN`, `USER`), `department`, `created_at`, `updated_at`.
   - Stores platform users with role-based attributes and UTC timestamps.

2. **`categories`**
   - Fields: `id`, `name` (unique), `description`, `created_at`.
   - Seeded with default categories: *Development*, *Testing*, *Reporting*, *Documentation*, *Meeting*, *Research*, *Maintenance*, *Other*.

3. **`tasks`**
   - Fields: `id`, `title`, `description`, `user_id` (FK -> `users.id`), `category_id` (FK -> `categories.id`), `priority` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), `status` (`TODO`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`), `created_at`, `updated_at`, `deadline`, `completed_at`, `estimated_hours`, `actual_hours`.
   - Key constraints: Non-negative `estimated_hours` and `actual_hours`.
   - Indexes: `user_id`, `category_id`, `status`, `priority`, `deadline`, `created_at`, `completed_at`.

4. **`task_activity`**
   - Fields: `id`, `task_id` (FK -> `tasks.id`), `user_id` (FK -> `users.id`), `activity_type` (`TASK_CREATED`, `TASK_UPDATED`, `STATUS_CHANGED`, `PRIORITY_CHANGED`, `DEADLINE_CHANGED`, `TASK_COMPLETED`, `TASK_DELETED`), `old_value`, `new_value`, `created_at`.
   - Indexes: `task_id`, `user_id`, `created_at`.

---

## Setup Instructions

### 1. Prerequisites
- Python 3.11+ installed.
- PostgreSQL 16+ running on `localhost:5432`.

### 2. Environment Configuration
Create `.env` file inside `backend/` from `.env.example`:
```bash
cp .env.example .env
```

Ensure your `.env` contains:
```env
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/task_productivity
TEST_DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/task_productivity_test
APP_NAME=Task Management & Productivity Analytics Platform
APP_ENV=development
```

### 3. Create Virtual Environment & Install Dependencies
```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Create PostgreSQL Databases
```sql
CREATE DATABASE task_productivity;
CREATE DATABASE task_productivity_test;
```

### 5. Run Database Migrations (Alembic)
```bash
alembic upgrade head
```

### 6. Seed Development Data
```bash
python scripts/seed_data.py
```
This generates 32 users, 8 categories, 1,050 tasks covering 12 explicit analytics edge cases, and 3,600+ activity log entries.

---

## Running the Backend Server

Start FastAPI with Uvicorn:
```bash
uvicorn app.main:app --reload
```

Interactive API Documentation:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
- **ReDoc**: [http://127.0.0.1:8000/api/redoc](http://127.0.0.1:8000/api/redoc)

Health Check Endpoints:
- `GET /api/health`
- `GET /api/health/db`

---

## Running Automated Tests

Run the automated test suite with pytest:
```bash
pytest
```
