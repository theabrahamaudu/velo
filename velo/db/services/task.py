from datetime import datetime
from typing import List
from velo.db.conn import Session
from velo.db.models import Task
from velo.types.task import CreateTask, ReadTask, ReadFullTask
from sqlalchemy import desc, select, update
from sqlalchemy.orm import joinedload


class TaskService:
    def __init__(self):
        self.session = Session

    def create(self, task: CreateTask) -> int | None:
        new_task = Task(
            campaign_id=task.campaign_id,
            tool_name=task.tool_name,
            status=task.status,
            output_json=task.output_json,
            created_at=datetime.now()
        )
        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        return new_task.id

    def read_by_id(self, id: int) -> ReadTask | None:
        statement = (
            select(Task)
            .where(Task.id == id)
            .order_by(desc(Task.created_at))
        )
        response = self.session.scalars(statement).first()

        if response is not None:
            return ReadTask.model_validate(
                response
            )

    def readAll_by_campaign_id(self, campaign_id: int) \
            -> List[ReadTask] | None:
        statement = (
            select(Task)
            .where(Task.campaign_id == campaign_id)
            .order_by(desc(Task.created_at))
        )
        response = self.session.scalars(statement).all()

        return [ReadTask.model_validate(c) for c in response]

    def readFull_by_id(self, id: int) -> ReadFullTask | None:
        statement = (
            select(Task)
            .where(Task.id == id)
            .order_by(desc(Task.created_at))
            .options(
                joinedload(Task.artifacts)
            )
        )
        response = self.session.scalars(statement).first()

        if response is not None:
            return ReadFullTask.model_validate(
                response
            )

    def update_by_id(self, id: int, **updates) -> None:
        updates["updated_at"] = datetime.now()
        statement = (
            update(Task)
            .where(Task.id == id)
            .values(**updates)
            .execution_options(synchronize_session="fetch")
        )
        self.session.execute(statement)
        self.session.commit()

    def delete_by_id(self, id: int) -> bool:
        task = self.session.scalar(
            select(Task)
            .where(Task.id == id)
        )
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True
