# Machine Learning & Predictive Analytics Documentation

## 1. Machine Learning Objectives
The Machine Learning layer adds responsible, reproducible predictive analytics to the Task Management Platform. It answers four core questions:
1. **Is this task likely to be completed late?** (Overdue Binary Classification: `is_late`)
2. **How long is this task likely to take?** (Completion Time Regression: `completion_days`)
3. **What factors contribute to task completion risk?** (Interpretable Feature Importance)
4. **Can task-level risk be displayed responsibly to users?** (AI Task Risk Prediction Card on Task Details)

---

## 2. Preventing Data Leakage
To prevent data leakage, training targets and features are constructed with strict temporal boundaries:
* **Excluded Post-Completion Attributes**: `completed_at`, `actual_hours`, `status`, `updated_at`, post-completion audit logs.
* **Included Prediction-Time Features**:
  - `priority` (LOW, MEDIUM, HIGH, CRITICAL)
  - `category_id` (Task category)
  - `user_id` (Assigned user)
  - `department` (User department)
  - `estimated_hours` (Initial estimated duration)
  - `days_to_deadline` ($\text{deadline} - \text{created\_at}$ in days)
  - `user_task_count` (Historical assigned volume)
  - `user_completion_rate` (Historical user completion percentage)

---

## 3. Dataset Summary & Targets

### Overdue Classification Target (`is_late`)
* **Definition**: $1$ if task status is `COMPLETED` and $\text{completed\_at} > \text{deadline}$; $0$ if completed on or before deadline.
* **Class Distribution**:
  - Total Completed Historical Records: **445**
  - Late Tasks ($y=1$): **132** ($29.66\%$)
  - On-Time Tasks ($y=0$): **313** ($70.34\%$)

### Completion Duration Regression Target (`completion_days`)
* **Definition**: $\text{completed\_at} - \text{created\_at}$ in days for completed tasks.
* **Mean Duration**: $3.45$ days (Std Dev: $2.82$ days).

---

## 4. Models & Evaluation Metrics

### Overdue Classification Model Evaluation

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Selected |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **RandomForestClassifier** | **0.9554** | **0.9118** | **0.9394** | **0.9254** | **0.9898** | ✅ Selected |
| **LogisticRegression** | 0.8839 | 0.7812 | 0.7576 | 0.7692 | 0.9125 | Candidate |

* **Selection Rationale**: `RandomForestClassifier` with `class_weight='balanced'` achieved the highest F1-score ($0.9254$) and Recall ($0.9394$), minimizing false negatives for overdue risk.

### Completion Duration Regression Model Evaluation

| Model | MAE (Days) | RMSE (Days) | R² Score | Selected |
| :--- | :---: | :---: | :---: | :---: |
| **RandomForestRegressor** | **0.7597** | **1.6186** | **0.6844** | ✅ Selected |
| **LinearRegression** | 1.1245 | 2.1030 | 0.4820 | Candidate |

* **Selection Rationale**: `RandomForestRegressor` achieved the lowest Mean Absolute Error ($0.7597$ days $\approx 18$ hours prediction error margin) and highest $R^2$ ($0.6844$).

---

## 5. Feature Importance Analysis

1. **`days_to_deadline`** ($50.14\%$): Strongest predictor of late completion risk. Tight deadlines relative to estimated hours significantly increase overdue risk.
2. **`estimated_hours`** ($13.10\%$): Tasks with higher estimated effort carry higher variance in completion duration.
3. **`priority`** ($9.11\%$): High and Critical priority tasks exhibit distinct completion velocities.
4. **`category_id`** ($7.10\%$): Development and Infrastructure categories take longer than Documentation or Testing.
5. **`department`** ($4.48\%$): Departmental workload capacity influences completion velocity.

---

## 6. RESTful Machine Learning Endpoints

| Endpoint | Method | Description | Request Payload | Response |
| :--- | :--- | :--- | :--- | :--- |
| `/api/ml/predict-overdue` | POST | Predict overdue probability & risk level | `priority`, `category_id`, `user_id`, `estimated_hours`, `deadline` | `late_probability`, `risk_level` (`LOW`/`MEDIUM`/`HIGH`) |
| `/api/ml/predict-completion-time` | POST | Predict completion duration in days | `priority`, `category_id`, `user_id`, `estimated_hours` | `predicted_completion_days` |
| `/api/ml/model-info` | GET | Retrieve model version & metadata | None | `classification_model`, `regression_model`, `metrics` |
| `/api/ml/feature-importance` | GET | Retrieve ranked feature importances | None | `classification_importance`, `regression_importance` |
| `/api/ml/health` | GET | Check ML model load status | None | `status`, `models_loaded` |
