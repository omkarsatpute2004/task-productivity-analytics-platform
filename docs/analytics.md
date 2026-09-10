# Phase 3: Analytics Engine Documentation

## Overview
The Analytics Engine processes task management data stored in PostgreSQL using Python 3.11, Pandas, NumPy, and SciPy. It exposes RESTful APIs via FastAPI for high-performance productivity insights, descriptive statistics, outlier detection, and workload distributions.

---

## Key Performance Indicators (KPIs) & Formulas

### 1. Summary KPIs
* **Total Tasks ($N$)**: Total count of task records.
* **Completion Rate ($\%$)**:
  $$\text{Completion Rate} = \left( \frac{\text{Completed Tasks}}{N} \right) \times 100$$
* **On-Time Completion Rate ($\%$)**:
  $$\text{On-Time Rate} = \left( \frac{\text{Tasks completed on or before deadline}}{\text{Completed Tasks}} \right) \times 100$$
* **Average Completion Days**:
  $$\bar{D}_{\text{completion}} = \frac{1}{M} \sum_{i=1}^{M} (t_{\text{completed}, i} - t_{\text{created}, i}) \text{ in days}$$
  *(where $M$ is the count of completed tasks)*.

### 2. Overdue Definition
* **Incomplete Overdue**: Task with status $\notin \{\text{COMPLETED}, \text{CANCELLED}\}$ where $\text{deadline} < \text{current\_timestamp}$.
* **Completed Late**: Task with status $=\text{COMPLETED}$ where $\text{completed\_at} > \text{deadline}$.

### 3. Estimation Metrics
* **Estimation Error ($\Delta_{i}$)**:
  $$\Delta_{i} = \text{actual\_hours}_{i} - \text{estimated\_hours}_{i}$$
  * $\Delta_{i} > 0$: Underestimated task (took longer than anticipated).
  * $\Delta_{i} < 0$: Overestimated task (took less time than anticipated).
* **Estimation Error Percentage**:
  $$\text{Percentage Error}_{i} = \left( \frac{\text{actual\_hours}_{i} - \text{estimated\_hours}_{i}}{\text{estimated\_hours}_{i}} \right) \times 100$$

### 4. Descriptive Statistics & Outlier Detection
* **Percentiles**: $P_{25}, P_{50} (\text{Median}), P_{75}, P_{90}$.
* **Interquartile Range (IQR)**:
  $$\text{IQR} = P_{75} - P_{25}$$
  $$\text{Lower Bound} = P_{25} - 1.5 \times \text{IQR}$$
  $$\text{Upper Bound} = P_{75} + 1.5 \times \text{IQR}$$
  * Any value falling outside $[\text{Lower Bound}, \text{Upper Bound}]$ is flagged as an outlier.

---

## Analytics Service Architecture

1. **SQL Layer (`app.analytics.queries`)**: Executes parameterized SQL queries fetching real records joining `tasks`, `users`, and `categories`.
2. **Data Cleaning Pipeline (`app.analytics.cleaning`)**: Deduplicates records, parses ISO timestamps to UTC, handles missing values, and validates non-negative hours.
3. **Feature Engineering (`app.analytics.features`)**: Derives computed fields (`completion_days`, `is_overdue`, `is_late`, `is_on_time`, `estimation_error`).
4. **Statistical Calculations (`app.analytics.statistics`)**: Computes mean, median, standard deviation, percentiles, Pearson correlation coefficients, and IQR outliers.
5. **Analytics Service (`app.analytics.service`)**: Integrates pipeline components with Role-Based Access Control (RBAC). Non-admin users access only their assigned/scoped tasks, while Admins view system-wide and departmental aggregations.

---

## FastAPI REST Endpoints Summary

| Endpoint | Method | Description | RBAC Scope |
| :--- | :--- | :--- | :--- |
| `/api/analytics/summary` | GET | Overall system/user productivity summary KPIs | User (Self) / Admin (System) |
| `/api/analytics/status-distribution` | GET | Counts and percentages by status | User (Self) / Admin (System) |
| `/api/analytics/priority` | GET | Metrics grouped by priority (LOW..CRITICAL) | User (Self) / Admin (System) |
| `/api/analytics/categories` | GET | Category productivity breakdown | User (Self) / Admin (System) |
| `/api/analytics/users` | GET | Neutral user productivity metrics | Admin (All) / User (Dept) |
| `/api/analytics/departments` | GET | Productivity aggregated by department | Admin / User |
| `/api/analytics/completion-trend` | GET | Daily, weekly, or monthly time series trend | User (Self) / Admin (System) |
| `/api/analytics/overdue` | GET | Overdue analysis by priority and category | User (Self) / Admin (System) |
| `/api/analytics/workload` | GET | Open workload counts & high priority tasks per user | Admin / User |
| `/api/analytics/estimation` | GET | Estimated vs actual hours, error %, stats, outliers | User (Self) / Admin (System) |
