"""Project Management models for Eli Claw SaaS."""

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import enum

from app.core.database import Base


class TaskStatus(str, enum.Enum):
    """Task status options."""
    BACKLOG = "backlog"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs_review"
    NEEDS_CLIENT_APPROVAL = "needs_client_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Campaign(Base):
    """SEO campaign model for organizing related tasks."""
    
    __tablename__ = "campaigns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    campaign_type: Mapped[str] = mapped_column(String(100), nullable=False)  # technical_seo, content, local_seo, etc.
    status: Mapped[str] = mapped_column(String(50), default="active")
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="campaigns")
    tasks = relationship("Task", back_populates="campaign", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="campaign", cascade="all, delete-orphan")


class Milestone(Base):
    """Milestone model for tracking major campaign checkpoints."""
    
    __tablename__ = "milestones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="milestones")


class Task(Base):
    """Task model for SEO work execution."""
    
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_task_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)  # audit, content, technical, etc.
    status: Mapped[str] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.BACKLOG, index=True)
    priority: Mapped[str] = mapped_column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    effort_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)  # hours
    actual_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impact_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    assigned_to: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    blocked_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("recommendations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    campaign = relationship("Campaign", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    assignee = relationship("User", backref="assigned_tasks")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")


class Subtask(Base):
    """Subtask model for breaking down tasks."""
    
    __tablename__ = "subtasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="subtasks")


class TaskComment(Base):
    """Comment model for task discussions."""
    
    __tablename__ = "task_comments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", backref="task_comments")


class TaskAttachment(Base):
    """Attachment model for task files."""
    
    __tablename__ = "task_attachments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploader = relationship("User", backref="task_attachments")
