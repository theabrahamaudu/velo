from datetime import datetime
from typing import List
from velo.db.conn import DBConn
from velo.db.models import Task
from velo.types.task import CreateTask, ReadTask, ReadFullTask
from sqlalchemy import desc, select
from sqlalchemy.orm import joinedload


class TaskService:
    def __init__(self):
        self.session = DBConn().session()

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
