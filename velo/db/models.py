from sqlalchemy import JSON, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    request_text = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    tool_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    output_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)


class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    type = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    version = Column(Integer)
