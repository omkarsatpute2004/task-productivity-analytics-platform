from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.category import Category
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.task_activity import TaskActivity, ActivityType


def test_duplicate_email_rejected(db: Session):
    """Verify that duplicate user emails trigger an IntegrityError."""
    user1 = User(
        name="John Doe",
        email="test.unique@example.com",
        password_hash="hashed_pw_123",
        role=UserRole.USER,
        department="Engineering"
    )
    db.add(user1)
    db.commit()

    user2 = User(
        name="Jane Doe",
        email="test.unique@example.com",
        password_hash="hashed_pw_456",
        role=UserRole.ADMIN,
        department="Product"
    )
    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_negative_hours_rejected(db: Session):
    """Verify that negative estimated hours violate check constraint."""
    user = User(
        name="Test User",
        email="user.hours@example.com",
        password_hash="hash",
        role=UserRole.USER
    )
    cat = Category(name="Test Category Hours")
    db.add_all([user, cat])
    db.commit()

    task = Task(
        title="Invalid Hours Task",
        user_id=user.id,
        category_id=cat.id,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.TODO,
        deadline=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_hours=Decimal("-5.00")
    )
    db.add(task)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_foreign_key_relationship_works(db: Session):
    """Verify Task -> User and Task -> Category foreign keys and relationships work properly."""
    user = User(
        name="FK User",
        email="fk.user@example.com",
        password_hash="hash",
        role=UserRole.USER
    )
    category = Category(name="FK Category", description="FK test category")
    db.add_all([user, category])
    db.commit()

    task = Task(
        title="FK Relationship Test Task",
        user_id=user.id,
        category_id=category.id,
        priority=TaskPriority.HIGH,
        status=TaskStatus.IN_PROGRESS,
        deadline=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_hours=Decimal("8.00"),
        actual_hours=Decimal("2.50")
    )
    db.add(task)
    db.commit()

    # Query back task
    fetched_task = db.query(Task).filter(Task.id == task.id).first()
    assert fetched_task is not None
    assert fetched_task.user.email == "fk.user@example.com"
    assert fetched_task.category.name == "FK Category"
    assert fetched_task.priority == TaskPriority.HIGH
    assert fetched_task.status == TaskStatus.IN_PROGRESS
    assert fetched_task.estimated_hours == Decimal("8.00")
