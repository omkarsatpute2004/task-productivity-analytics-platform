"""Development Seed Data Script for Task Management & Productivity Analytics Platform.

Behavior:
This script clears existing development seed data and recreates fresh, realistic sample data.
Marked for DEVELOPMENT USE ONLY.

Generates:
- 30+ users (varied roles, departments, password hashes)
- 8 default categories
- 1,000+ realistic tasks covering 12 explicit analytics edge cases
- 3,000+ task activity audit logs
"""
import os
import sys
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.task_activity import TaskActivity, ActivityType

# Development-only password hash
DEV_PASSWORD_HASH = "pbkdf2_sha256$260000$dev_salt_string$dev_hashed_password_for_testing_only"

DEPARTMENTS = ["Engineering", "Product", "Quality Assurance", "DevOps", "UX Design", "Analytics", "Operations"]
FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia",
               "Kevin", "Laura", "Marcus", "Nora", "Oliver", "Paula", "Quinn", "Rachel", "Sam", "Tina",
               "Ulysses", "Victoria", "Will", "Xena", "Yusuf", "Zoe", "Aaron", "Bella", "Chris", "Daisy"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

CATEGORY_NAMES = [
    ("Development", "Software engineering, bug fixes, and feature implementations"),
    ("Testing", "Manual testing, automated test suite maintenance, and QA validation"),
    ("Reporting", "Business intelligence reports, metrics compilation, and dashboard updates"),
    ("Documentation", "API specifications, system architecture documentation, and user guides"),
    ("Meeting", "Team standups, cross-functional alignment, and client reviews"),
    ("Research", "Technology evaluations, architecture spikes, and feasibility studies"),
    ("Maintenance", "Dependency upgrades, server patching, and technical debt reduction"),
    ("Other", "Miscellaneous operational and administrative tasks"),
]

TASK_VERBS = ["Implement", "Refactor", "Test", "Document", "Audit", "Optimize", "Fix", "Design", "Review", "Deploy"]
TASK_NOUNS = ["authentication module", "user settings page", "analytics pipeline", "database indexes",
              "billing service", "logging middleware", "notification queue", "search API", "export feature",
              "security vulnerabilities", "onboarding flow", "dashboard layout", "container deployment"]


def generate_seed_data():
    if settings.APP_ENV == "production":
        print("ERROR: Seed data script cannot be executed in production environment!", file=sys.stderr)
        sys.exit(1)

    print("Starting database seeding process...")
    db = SessionLocal()

    try:
        # 1. Clean existing seed data in reverse dependency order
        print("Clearing existing development data...")
        db.query(TaskActivity).delete()
        db.query(Task).delete()
        db.query(Category).delete()
        db.query(User).delete()
        db.commit()

        # 2. Seed Categories (8 categories)
        print("Seeding categories...")
        categories = []
        for name, desc in CATEGORY_NAMES:
            cat = Category(
                name=name,
                description=desc,
                created_at=datetime.now(timezone.utc) - timedelta(days=90)
            )
            db.add(cat)
            categories.append(cat)
        db.commit()

        # 3. Seed Users (32 users: 4 ADMINs, 28 USERs)
        print("Seeding 32 users...")
        users = []
        for i in range(32):
            fname = FIRST_NAMES[i % len(FIRST_NAMES)]
            lname = LAST_NAMES[i % len(LAST_NAMES)]
            role = UserRole.ADMIN if i < 4 else UserRole.USER
            dept = DEPARTMENTS[i % len(DEPARTMENTS)]
            user = User(
                name=f"{fname} {lname}",
                email=f"{fname.lower()}.{lname.lower()}{i+1}@example.com",
                password_hash=DEV_PASSWORD_HASH,
                role=role,
                department=dept,
                created_at=datetime.now(timezone.utc) - timedelta(days=90 - (i % 30))
            )
            db.add(user)
            users.append(user)
        db.commit()

        # Category and User maps for weighted distribution
        # Case 9 & 10: User with many tasks vs user with very few tasks
        heavy_user = users[0]
        light_user = users[1]

        # Case 11 & 12: Category with many tasks vs category with relatively few tasks
        heavy_category = categories[0]  # Development
        light_category = categories[7]  # Other

        now = datetime.now(timezone.utc)
        tasks = []

        print("Generating 1,050 tasks with realistic edge cases...")
        for i in range(1, 1051):
            # Select User & Category with skew for Case 9, 10, 11, 12
            if i <= 200:
                task_user = heavy_user
            elif i <= 210:
                task_user = light_user
            else:
                task_user = random.choice(users[2:])

            if i <= 300:
                task_cat = heavy_category
            elif i <= 320:
                task_cat = light_category
            else:
                task_cat = random.choice(categories[1:7])

            # Determine task timeline (created between 60 days ago and 5 days ago)
            created_offset = random.randint(5, 60)
            task_created = now - timedelta(days=created_offset, hours=random.randint(0, 23))

            # Case distribution
            case_type = i % 8

            if case_type == 0:
                # Case 1: Completed before deadline (On-time)
                deadline = task_created + timedelta(days=7)
                completed_at = task_created + timedelta(days=4)
                status = TaskStatus.COMPLETED
                est_hrs = Decimal(random.choice([4, 8, 12, 16]))
                act_hrs = est_hrs - Decimal(random.choice([0.5, 1.0, 2.0]))
            elif case_type == 1:
                # Case 2: Completed after deadline (Late)
                deadline = task_created + timedelta(days=5)
                completed_at = task_created + timedelta(days=8)
                status = TaskStatus.COMPLETED
                est_hrs = Decimal(random.choice([8, 16, 24]))
                act_hrs = est_hrs + Decimal(random.choice([3.0, 5.5, 8.0]))
            elif case_type == 2:
                # Case 3: Pending (TODO) and deadline has passed (Overdue)
                deadline = now - timedelta(days=random.randint(1, 10))
                completed_at = None
                status = TaskStatus.TODO
                est_hrs = Decimal(random.choice([6, 12, 20]))
                act_hrs = None
            elif case_type == 3:
                # Case 4: Pending (TODO) and deadline is in the future
                deadline = now + timedelta(days=random.randint(2, 15))
                completed_at = None
                status = TaskStatus.TODO
                est_hrs = Decimal(random.choice([4, 8, 10]))
                act_hrs = None
            elif case_type == 4:
                # Case 5: In progress
                deadline = now + timedelta(days=random.randint(1, 7))
                completed_at = None
                status = TaskStatus.IN_PROGRESS
                est_hrs = Decimal(random.choice([10, 20, 30]))
                act_hrs = Decimal(random.choice([4.0, 8.5, 12.0]))
            elif case_type == 5:
                # Case 6: Cancelled
                deadline = task_created + timedelta(days=10)
                completed_at = None
                status = TaskStatus.CANCELLED
                est_hrs = Decimal(random.choice([5, 15]))
                act_hrs = Decimal(random.choice([1.0, 2.5]))
            elif case_type == 6:
                # Case 7: High-priority task
                deadline = task_created + timedelta(days=random.randint(3, 10))
                completed_at = task_created + timedelta(days=2) if random.random() > 0.4 else None
                status = TaskStatus.COMPLETED if completed_at else TaskStatus.IN_PROGRESS
                est_hrs = Decimal(random.choice([8, 16, 24]))
                act_hrs = Decimal(random.choice([6.0, 14.0])) if completed_at else Decimal(random.choice([2.0, 4.0]))
            else:
                # Case 8: Critical task
                deadline = task_created + timedelta(days=random.randint(1, 5))
                completed_at = task_created + timedelta(days=1) if random.random() > 0.3 else None
                status = TaskStatus.COMPLETED if completed_at else TaskStatus.IN_PROGRESS
                est_hrs = Decimal(random.choice([12, 24, 40]))
                act_hrs = Decimal(random.choice([10.0, 22.0])) if completed_at else Decimal(random.choice([5.0, 10.0]))

            # Priority assignment
            if case_type == 6:
                priority = TaskPriority.HIGH
            elif case_type == 7:
                priority = TaskPriority.CRITICAL
            else:
                priority = random.choice([TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH, TaskPriority.CRITICAL])

            title = f"{random.choice(TASK_VERBS)} {random.choice(TASK_NOUNS)} (#{i})"
            desc = f"Detailed description for task #{i} assigned to {task_user.name} in category {task_cat.name}."

            task = Task(
                title=title,
                description=desc,
                user_id=task_user.id,
                category_id=task_cat.id,
                priority=priority,
                status=status,
                created_at=task_created,
                updated_at=completed_at or task_created + timedelta(hours=6),
                deadline=deadline,
                completed_at=completed_at,
                estimated_hours=est_hrs,
                actual_hours=act_hrs
            )
            db.add(task)
            tasks.append(task)

            if i % 250 == 0:
                db.commit()
                print(f"  Inserted {i} tasks...")

        db.commit()
        print(f"Total tasks inserted: {len(tasks)}")

        # 4. Seed Task Activities (3,200+ activity records)
        print("Generating 3,200+ task activity logs...")
        activity_count = 0
        for task in tasks:
            # 1. TASK_CREATED activity for every task
            act_created = TaskActivity(
                task_id=task.id,
                user_id=task.user_id,
                activity_type=ActivityType.TASK_CREATED,
                old_value=None,
                new_value=f"Task created with status {task.status.value} and priority {task.priority.value}",
                created_at=task.created_at
            )
            db.add(act_created)
            activity_count += 1

            # 2. STATUS_CHANGED or TASK_COMPLETED if completed/in-progress
            if task.status == TaskStatus.IN_PROGRESS:
                act_status = TaskActivity(
                    task_id=task.id,
                    user_id=task.user_id,
                    activity_type=ActivityType.STATUS_CHANGED,
                    old_value="TODO",
                    new_value="IN_PROGRESS",
                    created_at=task.created_at + timedelta(hours=4)
                )
                db.add(act_status)
                activity_count += 1
            elif task.status == TaskStatus.COMPLETED:
                act_status = TaskActivity(
                    task_id=task.id,
                    user_id=task.user_id,
                    activity_type=ActivityType.STATUS_CHANGED,
                    old_value="IN_PROGRESS",
                    new_value="COMPLETED",
                    created_at=task.completed_at
                )
                act_comp = TaskActivity(
                    task_id=task.id,
                    user_id=task.user_id,
                    activity_type=ActivityType.TASK_COMPLETED,
                    old_value=None,
                    new_value=f"Task completed in {task.actual_hours} hours",
                    created_at=task.completed_at
                )
                db.add(act_status)
                db.add(act_comp)
                activity_count += 2
            elif task.status == TaskStatus.CANCELLED:
                act_cancel = TaskActivity(
                    task_id=task.id,
                    user_id=task.user_id,
                    activity_type=ActivityType.STATUS_CHANGED,
                    old_value="TODO",
                    new_value="CANCELLED",
                    created_at=task.created_at + timedelta(days=2)
                )
                db.add(act_cancel)
                activity_count += 1

            # 3. Optional PRIORITY_CHANGED for high/critical tasks
            if task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]:
                act_prio = TaskActivity(
                    task_id=task.id,
                    user_id=task.user_id,
                    activity_type=ActivityType.PRIORITY_CHANGED,
                    old_value="MEDIUM",
                    new_value=task.priority.value,
                    created_at=task.created_at + timedelta(hours=2)
                )
                db.add(act_prio)
                activity_count += 1

            # 4. Optional TASK_UPDATED activity log
            if random.random() > 0.4:
                act_update = TaskActivity(
                    task_id=task.id,
                    user_id=task.user_id,
                    activity_type=ActivityType.TASK_UPDATED,
                    old_value="Estimated hours: " + str(task.estimated_hours),
                    new_value="Updated task details and timeline",
                    created_at=task.created_at + timedelta(hours=1)
                )
                db.add(act_update)
                activity_count += 1

            if activity_count % 500 == 0:
                db.commit()

        db.commit()
        print(f"Total activity records inserted: {activity_count}")

        print("\nSUCCESS: Seeding completed cleanly!")
        print(f"  Users:      {len(users)}")
        print(f"  Categories: {len(categories)}")
        print(f"  Tasks:      {len(tasks)}")
        print(f"  Activities: {activity_count}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: Database seeding failed: {e}", file=sys.stderr)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    generate_seed_data()
