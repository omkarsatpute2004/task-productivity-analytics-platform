# Task Management & Productivity Analytics Platform

A complete end-to-end full-stack web application for **Task Management**, **Productivity Analytics**, and **Machine Learning Predictive Intelligence** built with **PostgreSQL**, **FastAPI**, **SQLAlchemy**, **Pandas**, **NumPy**, **scikit-learn**, and **React + TypeScript + Tailwind CSS**.

---

## 🎯 Overview

This platform enables teams to organize daily tasks, monitor department-wide productivity metrics, track execution velocity, analyze estimation errors, and proactively identify task overdue risks using trained Machine Learning classification and regression models.

---

## 🏢 Business Problem

Modern software engineering and project management teams struggle with:
1. **Unpredictable Deadlines**: Tasks often breach deadlines without early warning indicators.
2. **Estimation Error**: Gap between planned estimated hours and actual execution time.
3. **Lack of Productivity Insights**: Inability to identify workload bottlenecks across departments and individual team members.
4. **Reactive Risk Management**: Identifying late tasks *after* they are already overdue rather than predicting risk *at planning time*.

This platform addresses these challenges by combining real-time task management with statistical analytics and scikit-learn predictive models.

---

## ✨ Key Features

### 📋 Task Management & Workflow
- **Task Lifecycle Management**: Full CRUD operations for tasks with priority levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and statuses (`TODO`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).
- **Role-Based Access Control (RBAC)**: Enforces `ADMIN` (system-wide management) vs `USER` (assigned task control) permissions.
- **Audit Logging & Activity Timeline**: Automatic background tracking of task state changes, reassignment history, and timestamp metrics.
- **Filtering & Search**: Dynamic text search, priority filtering, status filtering, category filtering, and paginated tables.

### 📊 Statistical Analytics Engine
- **Productivity KPIs**: Real-time aggregation of total tasks, completion rates, on-time completion percentages, and average completion durations.
- **Descriptive Statistics**: Vectorised statistical metrics (mean, median, std dev, P25-P90 percentiles) for estimated vs actual hours.
- **Outlier & Correlation Analysis**: Pearson correlation coefficient calculations and IQR (Interquartile Range) outlier detection.
- **Visual Analytics**: Interactive Recharts visualizations (Donut status charts, Bar category comparisons, Workload tables, Estimation error trends).

### 🤖 Machine Learning & Predictive Intelligence
- **Overdue Risk Classifier**: Predicts late completion probability and assigns risk levels (`LOW`, `MEDIUM`, `HIGH`) at task creation time.
- **Completion Duration Regressor**: Estimates expected task completion time in days/hours.
- **Feature Importance Breakdown**: Transparent, interpretable ranking of decision factors (`days_to_deadline`, `estimated_hours`, `priority`, `category`, `department`).
- **Data Leakage Safeguards**: Strict exclusion of post-completion attributes (`completed_at`, `actual_hours`, status updates) during feature extraction.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.11+, FastAPI, Pydantic V2, Pydantic Settings, Uvicorn |
| **Database & ORM** | PostgreSQL 17, SQLAlchemy 2.x, Alembic Migrations |
| **Data Science & ML** | Pandas, NumPy, SciPy, scikit-learn 1.9.0, joblib 1.6.0 |
| **Frontend UI** | React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts |
| **Authentication** | JWT (JSON Web Tokens), Passlib / Bcrypt password hashing |
| **Testing & Quality** | pytest, Vitest, Testing Library, Docker |

---

## 🏗️ System Architecture

```text
                                  ┌────────────────────────┐
                                  │   React 18 Frontend    │
                                  │ (TS + Vite + Tailwind) │
                                  └───────────┬────────────┘
                                              │ HTTP / REST (Axios + JWT)
                                              ▼
                                  ┌────────────────────────┐
                                  │    FastAPI REST API    │
                                  │   (Auth + RBAC + ML)   │
                                  └─────┬────────────┬─────┘
                                        │            │
                   ┌────────────────────┘            └────────────────────┐
                   ▼                                                      ▼
┌───────────────────────────────────────┐              ┌─────────────────────────────────────┐
│    Analytics & ML Prediction Engine    │              │       PostgreSQL 17 Database        │
│ (Pandas + NumPy + scikit-learn + Joblib)│              │  (Users, Tasks, Categories, Audit)  │
└───────────────────────────────────────┘              └─────────────────────────────────────┘
```

---

## 📈 Verified Machine Learning Metrics

The machine learning models were trained and evaluated on **445 completed task records** (313 On-Time, 132 Late) using an **80/20 stratified train-test split**:

### 1. Overdue Risk Classifier (`RandomForestClassifier`)
- **Accuracy**: `95.54%`
- **Precision**: `91.18%`
- **Recall**: `93.94%`
- **F1 Score**: `92.54%`
- **ROC-AUC**: **`0.9898`**
- **Confusion Matrix**: `[[76 (TN), 3 (FP)], [2 (FN), 31 (TP)]]`

### 2. Completion Duration Regressor (`RandomForestRegressor`)
- **MAE (Mean Absolute Error)**: **`0.7597 days`** ($\approx 18.2$ hours execution)
- **RMSE (Root Mean Sq. Error)**: `1.6186 days`
- **$R^2$ Score**: **`0.6844`**

> [!NOTE]
> **Dataset Disclosure**: The dataset consists of **synthetic benchmark data** generated via `scripts/seed_db.py` (1,051 total tasks across 33 users and 8 categories). It realistically models productivity distributions for demonstration and benchmarking.

---

## 📂 Project Structure

```text
task-productivity-platform/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (auth, tasks, analytics, ml)
│   │   ├── core/            # Configuration and security settings
│   │   ├── db/              # SQLAlchemy session and base setup
│   │   ├── ml/              # Scikit-learn feature engineering, models & manager
│   │   ├── models/          # SQLAlchemy ORM database models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── services/        # Business logic services
│   ├── alembic/             # Database migration scripts
│   ├── scripts/             # Seed data & model training scripts
│   ├── tests/               # Pytest automated test suite (52 tests)
│   ├── Dockerfile           # Backend containerization
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (Tasks, Analytics, Common, Layout)
│   │   ├── context/         # React AuthContext
│   │   ├── pages/           # Application pages (Dashboard, Tasks, Analytics, etc.)
│   │   ├── services/        # Axios API services (taskApi, analyticsApi, mlApi)
│   │   └── types/           # TypeScript interface definitions
│   ├── Dockerfile           # Frontend Nginx containerization
│   └── package.json         # Node dependencies
├── models/                  # Serialized joblib ML model artifacts
├── notebooks/               # Jupyter Notebooks (EDA, Stats, ML training)
├── docs/                    # Technical documentation & interview guide
├── sql/                     # Parameterized SQL analytical queries
├── docker-compose.yml       # Local development Docker configuration
├── .env.example             # Safe environment variable template
└── README.md                # Root documentation
```

---

## 🔌 API Endpoints Reference

### Authentication & Users
- `POST /api/auth/register` — Register a new user
- `POST /api/auth/login` — Authenticate and receive JWT access token
- `GET /api/auth/me` — Retrieve current authenticated profile
- `GET /api/users` — Admin list of all users

### Task Management
- `GET /api/tasks` — List tasks with search, priority/status filter, and pagination
- `POST /api/tasks` — Create a new task
- `GET /api/tasks/{id}` — Get detailed task information
- `PUT /api/tasks/{id}` — Update task attributes
- `PATCH /api/tasks/{id}/status` — Update task status and trigger audit log
- `DELETE /api/tasks/{id}` — Delete task (Admin or assigned owner)
- `GET /api/tasks/{id}/activity` — Retrieve immutable task audit timeline

### Analytics APIs
- `GET /api/analytics/summary` — High-level KPI summary
- `GET /api/analytics/status-distribution` — Status percentage breakdown
- `GET /api/analytics/categories` — Category performance metrics
- `GET /api/analytics/users` — Individual developer productivity metrics
- `GET /api/analytics/estimation` — Descriptive statistics and Pearson correlations

### Machine Learning APIs
- `POST /api/ml/predict-overdue` — Predict task late completion risk and risk tier (`LOW`, `MEDIUM`, `HIGH`)
- `POST /api/ml/predict-completion-time` — Predict completion duration in days
- `GET /api/ml/model-info` — Retrieve model metadata, dataset counts, and evaluation metrics
- `GET /api/ml/feature-importance` — Retrieve interpretable feature ranking
- `GET /api/ml/health` — Check ML model pipeline operational status

---

## 🚀 Quick Start Setup Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 17** (or Docker)

### 1. Database Setup
Ensure PostgreSQL is running and create the database:
```sql
CREATE DATABASE task_productivity;
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows Powershell
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations & seed data
alembic upgrade head
python scripts/seed_db.py
python scripts/train_models.py

# Start FastAPI server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🐳 Docker Local Setup (Optional)

Run the full stack via Docker Compose:
```bash
docker-compose up --build
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API Docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## 🧪 Testing Summary

```bash
# Run backend pytest suite
cd backend
.\venv\Scripts\pytest.exe -v

# Run frontend test suite & build validation
cd frontend
npm test
npm run build
```
- **Backend Test Suite**: `52 / 52 Passed` (0 failed)
- **Frontend Test Suite**: `1 / 1 Passed` (0 failed)
- **Build Validation**: TypeScript (`tsc -b`) and Vite production bundle validated.

---

## ⚠️ Known Limitations & Future Improvements

### Limitations
1. **Benchmark Seed Data**: Machine learning models were trained on a 1,051-task synthetic benchmark dataset. High metrics reflect signal within the seed distribution.
2. **Static Artifacts**: Trained models are saved as static `joblib` files and require periodic execution of `train_models.py` rather than streaming online retraining.

### Future Improvements
- Automated CI/CD deployment with GitHub Actions to AWS ECS / GCP Cloud Run.
- Real-time event streaming using Apache Kafka for instant audit logging.
- Advanced hyperparameter tuning (`GridSearchCV`) and MLflow experiment tracking.

---

## 📄 License & Attribution

Built for technical demonstration and portfolio showcase.
