-- Human-readable SQL Reference Schema for Task Management & Productivity Analytics Platform
-- NOTE: Alembic migrations in backend/alembic/ remain the authoritative source of truth.

-- Enable UUID extension if required in future
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Create Enums
CREATE TYPE user_role_enum AS ENUM ('ADMIN', 'USER');
CREATE TYPE task_priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE task_status_enum AS ENUM ('TODO', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
CREATE TYPE activity_type_enum AS ENUM (
    'TASK_CREATED', 'TASK_UPDATED', 'STATUS_CHANGED',
    'PRIORITY_CHANGED', 'DEADLINE_CHANGED', 'TASK_COMPLETED', 'TASK_DELETED'
);

-- 2. Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'USER',
    department VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX ix_users_email ON users(email);

-- 3. Categories Table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tasks Table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    priority task_priority_enum NOT NULL DEFAULT 'MEDIUM',
    status task_status_enum NOT NULL DEFAULT 'TODO',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_hours NUMERIC(10, 2) NOT NULL CHECK (estimated_hours >= 0),
    actual_hours NUMERIC(10, 2) CHECK (actual_hours IS NULL OR actual_hours >= 0)
);

CREATE INDEX ix_tasks_user_id ON tasks(user_id);
CREATE INDEX ix_tasks_category_id ON tasks(category_id);
CREATE INDEX ix_tasks_status ON tasks(status);
CREATE INDEX ix_tasks_priority ON tasks(priority);
CREATE INDEX ix_tasks_deadline ON tasks(deadline);
CREATE INDEX ix_tasks_created_at ON tasks(created_at);
CREATE INDEX ix_tasks_completed_at ON tasks(completed_at);

-- 5. Task Activity Table
CREATE TABLE task_activity (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type activity_type_enum NOT NULL,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_task_activity_task_id ON task_activity(task_id);
CREATE INDEX ix_task_activity_user_id ON task_activity(user_id);
CREATE INDEX ix_task_activity_created_at ON task_activity(created_at);
