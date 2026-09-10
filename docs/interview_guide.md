# Task Management & Productivity Analytics Platform — Technical Interview Preparation Guide

This document provides concise, technically accurate answers to key architectural, engineering, statistical, and machine learning interview questions about this platform.

---

### 1. What problem does this project solve?
It provides an end-to-end task management and productivity analytics solution that helps teams manage daily tasks, track productivity metrics, audit completion rates, and proactively predict task overdue risks and completion durations using historical productivity patterns.

---

### 2. Why did you choose PostgreSQL?
PostgreSQL 17 was chosen for its ACID compliance, robust constraint enforcement (`CHECK`, `FOREIGN KEY`, `UNIQUE`), strong indexing capabilities (B-tree indexes on `status`, `user_id`, `category_id`, `deadline`), and native analytical window function support (`OVER(PARTITION BY...)`).

---

### 3. Why FastAPI?
FastAPI was selected for its high performance (built on Starlette and Pydantic V2), native asynchronous support (`async/await`), automatic OpenAPI (`/api/docs`) schema generation, and strict data validation using Pydantic models.

---

### 4. Why React?
React 18 with TypeScript and Vite provides component-driven UI modularity, strict type safety, fast build times, responsive DOM rendering, and seamless integration with visualization tools like Recharts.

---

### 5. How does the backend work?
The backend follows a layered REST architecture:
1. **Routing (`app/api/`)**: Enforces HTTP paths and Dependency Injection (`get_db`, `get_current_user`).
2. **Services (`app/services/`)**: Enforces business logic (auth, task state transitions, audit logging).
3. **Analytics & ML Engine (`app/ml/`, `sql/`)**: Executes SQL analytical queries and scikit-learn model inference.
4. **Data Layer (`app/models/`, `app/db/`)**: SQLAlchemy 2.x ORM models mapped to PostgreSQL database tables.

---

### 6. How did you design the database?
The database schema consists of four core entities:
- `users`: Stores user identity, hashed passwords, departments, and roles (`ADMIN`, `USER`).
- `categories`: Taxonomical grouping for tasks.
- `tasks`: Core domain model tracking priority, status, estimated/actual hours, deadlines, and completion timestamps.
- `task_activity`: Immutable audit log capturing all status updates and attribute mutations.

---

### 7. How did you calculate completion rate?
$$ \text{Completion Rate (\%)} = \left( \frac{\text{Completed Tasks}}{\text{Total Assigned Tasks}} \right) \times 100 $$
Calculated via SQL aggregations `COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*)` and verified with Pandas in the backend analytics service.

---

### 8. How did you identify overdue tasks?
Overdue tasks are identified by comparing the deadline timestamp against the completion timestamp or current time:
- Incomplete tasks: `status != 'COMPLETED' AND deadline < CURRENT_TIMESTAMP`
- Historically completed late tasks: `status == 'COMPLETED' AND completed_at > deadline`

---

### 9. Why Pandas and NumPy?
Pandas and NumPy were used in the analytics layer for fast vectorised matrix operations, descriptive statistical distributions (mean, median, standard deviation, P25-P90 percentiles), Pearson correlation coefficients, and IQR outlier filtering on estimated vs actual hours.

---

### 10. Why Random Forest?
Random Forest (ensemble of decision trees with bagging) handles non-linear feature interactions (such as tight deadlines combined with high estimated hours), handles mixed categorical/numerical features without linearity assumptions, and naturally resists overfitting through tree averaging.

---

### 11. Why compare Logistic Regression?
Logistic Regression was evaluated as a linear baseline classifier. Comparing it against Random Forest demonstrated that task overdue risk relies on non-linear feature boundaries, as Random Forest increased accuracy from **65.18%** to **95.54%** and ROC-AUC from **0.6548** to **0.9898**.

---

### 12. Why compare Linear Regression?
Linear Regression was evaluated as a continuous linear baseline. It yielded an $R^2$ of **-0.0426** (worse than mean prediction due to non-linear execution patterns), whereas `RandomForestRegressor` achieved an $R^2$ of **0.6844** and an MAE of **0.7597 days** ($\approx 18$ hours).

---

### 13. How did you prevent data leakage?
Target leakage was strictly prevented by excluding post-completion variables (`completed_at`, `actual_hours`, final `status`, and post-completion audit history) from the feature matrix `FEATURE_COLUMNS`. Features were strictly limited to attributes available at task creation/planning time (`priority`, `category_id`, `user_id`, `department`, `estimated_hours`, `days_to_deadline`, `user_task_count`, `user_completion_rate`).

---

### 14. What features were used?
- `priority`: Categorical task priority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `category_id`: Categorical domain ID.
- `user_id`: Categorical assigned developer ID.
- `department`: Categorical user department.
- `estimated_hours`: Numerical planned effort.
- `days_to_deadline`: Numerical days between creation timestamp and deadline.
- `user_task_count`: Numerical historical task load for the user.
- `user_completion_rate`: Numerical historical completion percentage for the user.

---

### 15. What was the classification performance?
Evaluated on an 80/20 stratified test split of 445 completed task records:
- **Accuracy**: `95.54%`
- **Precision**: `91.18%`
- **Recall**: `93.94%`
- **F1 Score**: `92.54%`
- **ROC-AUC**: `0.9898`
- **Confusion Matrix**: `[[76 (TN), 3 (FP)], [2 (FN), 31 (TP)]]`

---

### 16. What was the regression performance?
Evaluated on an 80/20 test split:
- **MAE (Mean Absolute Error)**: `0.7597 days` ($\approx 18.2$ hours)
- **RMSE (Root Mean Square Error)**: `1.6186 days`
- **$R^2$ Score**: `0.6844`

---

### 17. What does ROC-AUC mean?
ROC-AUC (Receiver Operating Characteristic - Area Under Curve) measures the classifier's ability to discriminate between positive (Late) and negative (On-time) classes across all classification thresholds. A score of `0.9898` indicates near-optimal rank ordering of overdue probabilities.

---

### 18. What does MAE mean?
MAE (Mean Absolute Error) measures the average magnitude of absolute prediction errors in days. An MAE of `0.7597 days` means model duration predictions deviate from actual completion times by approximately 18 hours on average.

---

### 19. What are the limitations?
1. Model trained on a benchmark dataset (445 completed samples).
2. Limited multi-year seasonal telemetry.
3. Static joblib artifacts requiring scheduled retraining scripts rather than real-time streaming updates.

---

### 20. Is the dataset real or synthetic?
The dataset consists of **synthetic benchmark data** generated via `scripts/seed_db.py` (1,051 tasks, 33 users, 8 categories). It realistically models productivity metrics but is disclosed as synthetic demo data.

---

### 21. How would you improve the project with real production data?
1. Ingest streaming telemetry events into Kafka/RabbitMQ.
2. Implement automated model retraining and drift detection (Evidently AI / MLflow).
3. Expand feature engineering with developer commit frequency, PR review time, and holiday calendars.

---

### 22. How would you deploy it?
1. **Database**: Managed PostgreSQL (AWS RDS / GCP Cloud SQL).
2. **Backend**: Containerized FastAPI service on AWS ECS / GCP Cloud Run.
3. **Frontend**: Static Vite production build served via CDN (Cloudflare / Vercel).
4. **CI/CD**: GitHub Actions pipeline executing `pytest`, `npm test`, and Docker image pushes.

---

### 23. What security measures did you implement?
- **Authentication**: JWT token authentication with bcrypt password hashing.
- **Authorization**: Role-Based Access Control (RBAC) restricting admin routes (`/api/users`, category creation) and object-level permissions (users can only access/modify their assigned tasks unless ADMIN).
- **Validation**: Pydantic schemas validating non-negative hours, valid enum values, and ISO timestamps.
- **Data Protection**: Sensitive attributes (`password_hash`) are excluded from API schemas (`response_model`), and CORS headers are explicitly scoped.
