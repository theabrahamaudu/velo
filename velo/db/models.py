from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List
from velo.types.task import ReadTask as T
from velo.types.artifact import ReadArtifact as A


class Base(DeclarativeBase):
    pass


class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    request_text: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    tasks: Mapped[List[T]] = relationship(
        "Task",
        back_populates="campaign"
    )
    artifacts: Mapped[List[A]] = relationship(
        "Artifact",
        back_populates="campaign"
    )


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    campaign_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("campaigns.id"),
        nullable=False
    )
    tool_name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    output_json: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)

    campaign = relationship("Campaign", back_populates="tasks")
    artifacts: Mapped[List[A]] = relationship(
        "Artifact",
        back_populates="task"
    )


class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    task_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tasks.id"),
        nullable=False
    )
    campaign_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("campaigns.id"),
        nullable=False
    )
    type: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=True)
    version: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)

    campaign = relationship("Campaign", back_populates="artifacts")
    task = relationship("Task", back_populates="artifacts")
