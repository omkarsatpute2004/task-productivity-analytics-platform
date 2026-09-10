-- =============================================================================
-- Task Management & Productivity Analytics Platform
-- Analytical SQL Queries Reference
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Summary Productivity KPIs
-- Extracts overall task volume, completed tasks, overdue tasks, and completion rate.
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN t.status = 'TODO' THEN 1 END) AS pending_tasks,
    COUNT(CASE WHEN t.status = 'IN_PROGRESS' THEN 1 END) AS in_progress_tasks,
    COUNT(CASE WHEN t.status = 'CANCELLED' THEN 1 END) AS cancelled_tasks,
    COUNT(CASE WHEN (t.status NOT IN ('COMPLETED', 'CANCELLED') AND CURRENT_TIMESTAMP > t.deadline) 
                 OR (t.status = 'COMPLETED' AND t.completed_at > t.deadline) THEN 1 END) AS overdue_tasks,
    ROUND(
        (COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END)::NUMERIC / NULLIF(COUNT(t.id), 0)) * 100.0, 
        2
    ) AS completion_rate_percentage,
    ROUND(
        AVG(CASE WHEN t.status = 'COMPLETED' THEN EXTRACT(EPOCH FROM (t.completed_at - t.created_at))/86400.0 END)::NUMERIC,
        2
    ) AS average_completion_days
FROM tasks t;

-- -----------------------------------------------------------------------------
-- 2. Status Distribution Breakdown
-- -----------------------------------------------------------------------------
SELECT 
    t.status,
    COUNT(t.id) AS task_count,
    ROUND(
        (COUNT(t.id)::NUMERIC / (SELECT COUNT(*) FROM tasks)) * 100.0,
        2
    ) AS percentage
FROM tasks t
GROUP BY t.status
ORDER BY task_count DESC;

-- -----------------------------------------------------------------------------
-- 3. Priority Level Analysis
-- -----------------------------------------------------------------------------
SELECT 
    t.priority,
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN (t.status NOT IN ('COMPLETED', 'CANCELLED') AND CURRENT_TIMESTAMP > t.deadline) 
                 OR (t.status = 'COMPLETED' AND t.completed_at > t.deadline) THEN 1 END) AS overdue_tasks,
    ROUND(
        (COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END)::NUMERIC / NULLIF(COUNT(t.id), 0)) * 100.0, 
        2
    ) AS completion_rate,
    ROUND(AVG(t.estimated_hours)::NUMERIC, 2) AS avg_estimated_hours,
    ROUND(AVG(t.actual_hours)::NUMERIC, 2) AS avg_actual_hours
FROM tasks t
GROUP BY t.priority
ORDER BY 
    CASE t.priority 
        WHEN 'CRITICAL' THEN 1 
        WHEN 'HIGH' THEN 2 
        WHEN 'MEDIUM' THEN 3 
        WHEN 'LOW' THEN 4 
    END;

-- -----------------------------------------------------------------------------
-- 4. Category Productivity & Volume
-- -----------------------------------------------------------------------------
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS completed_tasks,
    ROUND(
        (COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END)::NUMERIC / NULLIF(COUNT(t.id), 0)) * 100.0, 
        2
    ) AS completion_rate,
    SUM(t.estimated_hours) AS total_estimated_hours,
    SUM(t.actual_hours) AS total_actual_hours
FROM categories c
LEFT JOIN tasks t ON c.id = t.category_id
GROUP BY c.id, c.name
ORDER BY total_tasks DESC;

-- -----------------------------------------------------------------------------
-- 5. User Productivity Metrics (Neutral Performance Measures)
-- -----------------------------------------------------------------------------
SELECT 
    u.id AS user_id,
    u.name AS user_name,
    u.department,
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN (t.status NOT IN ('COMPLETED', 'CANCELLED') AND CURRENT_TIMESTAMP > t.deadline) 
                 OR (t.status = 'COMPLETED' AND t.completed_at > t.deadline) THEN 1 END) AS overdue_tasks,
    ROUND(
        (COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END)::NUMERIC / NULLIF(COUNT(t.id), 0)) * 100.0, 
        2
    ) AS completion_rate,
    ROUND(
        (COUNT(CASE WHEN t.status = 'COMPLETED' AND t.completed_at <= t.deadline THEN 1 END)::NUMERIC / NULLIF(COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END), 0)) * 100.0,
        2
    ) AS on_time_completion_rate,
    SUM(t.actual_hours) AS total_actual_hours
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.name, u.department
ORDER BY completion_rate DESC;

-- -----------------------------------------------------------------------------
-- 6. Departmental Breakdown
-- -----------------------------------------------------------------------------
SELECT 
    u.department,
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS completed_tasks,
    ROUND(
        (COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END)::NUMERIC / NULLIF(COUNT(t.id), 0)) * 100.0, 
        2
    ) AS completion_rate,
    COUNT(CASE WHEN (t.status NOT IN ('COMPLETED', 'CANCELLED') AND CURRENT_TIMESTAMP > t.deadline) 
                 OR (t.status = 'COMPLETED' AND t.completed_at > t.deadline) THEN 1 END) AS overdue_tasks,
    SUM(t.estimated_hours) AS total_estimated_hours,
    SUM(t.actual_hours) AS total_actual_hours
FROM users u
JOIN tasks t ON u.id = t.user_id
WHERE u.department IS NOT NULL
GROUP BY u.department
ORDER BY total_tasks DESC;

-- -----------------------------------------------------------------------------
-- 7. Monthly Completion Trend Time Series
-- -----------------------------------------------------------------------------
SELECT 
    TO_CHAR(t.created_at, 'YYYY-MM') AS month_period,
    COUNT(t.id) AS tasks_created,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) AS tasks_completed,
    ROUND(
        (COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END)::NUMERIC / NULLIF(COUNT(t.id), 0)) * 100.0, 
        2
    ) AS completion_rate
FROM tasks t
GROUP BY TO_CHAR(t.created_at, 'YYYY-MM')
ORDER BY month_period ASC;

-- -----------------------------------------------------------------------------
-- 8. Overdue Tasks Analysis
-- -----------------------------------------------------------------------------
SELECT 
    t.id AS task_id,
    t.title,
    u.name AS assigned_user,
    c.name AS category_name,
    t.priority,
    t.status,
    t.deadline,
    t.completed_at,
    CASE 
        WHEN t.status = 'COMPLETED' AND t.completed_at > t.deadline THEN 'COMPLETED_LATE'
        WHEN t.status NOT IN ('COMPLETED', 'CANCELLED') AND CURRENT_TIMESTAMP > t.deadline THEN 'INCOMPLETE_OVERDUE'
    END AS overdue_type
FROM tasks t
JOIN users u ON t.user_id = u.id
JOIN categories c ON t.category_id = c.id
WHERE (t.status NOT IN ('COMPLETED', 'CANCELLED') AND CURRENT_TIMESTAMP > t.deadline)
   OR (t.status = 'COMPLETED' AND t.completed_at > t.deadline)
ORDER BY t.deadline ASC;

-- -----------------------------------------------------------------------------
-- 9. Open Workload Distribution
-- -----------------------------------------------------------------------------
SELECT 
    u.id AS user_id,
    u.name AS user_name,
    COUNT(t.id) AS total_assigned_tasks,
    COUNT(CASE WHEN t.status NOT IN ('COMPLETED', 'CANCELLED') THEN 1 END) AS open_tasks,
    COUNT(CASE WHEN t.status NOT IN ('COMPLETED', 'CANCELLED') AND t.priority = 'HIGH' THEN 1 END) AS high_priority_open,
    COUNT(CASE WHEN t.status NOT IN ('COMPLETED', 'CANCELLED') AND t.priority = 'CRITICAL' THEN 1 END) AS critical_priority_open,
    COUNT(CASE WHEN t.status NOT IN ('COMPLETED', 'CANCELLED') AND CURRENT_TIMESTAMP > t.deadline THEN 1 END) AS overdue_open
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.name
ORDER BY open_tasks DESC;

-- -----------------------------------------------------------------------------
-- 10. Estimated vs Actual Hours Estimation Analysis
-- -----------------------------------------------------------------------------
SELECT 
    ROUND(SUM(t.estimated_hours)::NUMERIC, 2) AS total_estimated_hours,
    ROUND(SUM(t.actual_hours)::NUMERIC, 2) AS total_actual_hours,
    ROUND(AVG(t.estimated_hours)::NUMERIC, 2) AS avg_estimated_hours,
    ROUND(AVG(t.actual_hours)::NUMERIC, 2) AS avg_actual_hours,
    ROUND(SUM(t.actual_hours - t.estimated_hours)::NUMERIC, 2) AS total_estimation_error,
    ROUND(AVG(t.actual_hours - t.estimated_hours)::NUMERIC, 2) AS avg_estimation_error,
    COUNT(CASE WHEN t.actual_hours > t.estimated_hours THEN 1 END) AS underestimated_count,
    COUNT(CASE WHEN t.actual_hours < t.estimated_hours THEN 1 END) AS overestimated_count
FROM tasks t
WHERE t.estimated_hours IS NOT NULL AND t.actual_hours IS NOT NULL;
