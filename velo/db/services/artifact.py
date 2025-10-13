from datetime import datetime
from typing import List
from velo.db.conn import Session
from velo.db.models import Artifact
from velo.types.artifact import CreateArtifact, ReadArtifact
from sqlalchemy import desc, select, update


class ArtifactService:
    def __init__(self):
        self.session = Session

    def create(self, artifact: CreateArtifact) -> int | None:
        new_task = Artifact(
            task_id=artifact.task_id,
            campaign_id=artifact.campaign_id,
            type=artifact.type,
            file_path=artifact.file_path,
            version=artifact.version,
            created_at=datetime.now()
        )
        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        return new_task.id

    def read_by_id(self, id: int) -> ReadArtifact | None:
        statement = (
            select(Artifact)
            .where(Artifact.id == id)
            .order_by(desc(Artifact.created_at))
        )
        response = self.session.scalars(statement).first()

        if response is not None:
            return ReadArtifact.model_validate(
                response
            )

    def readAll_by_campaign_id(self, campaign_id: int) \
            -> List[ReadArtifact] | None:
        statement = (
            select(Artifact)
            .where(Artifact.campaign_id == campaign_id)
            .order_by(desc(Artifact.created_at))
        )
        response = self.session.scalars(statement).all()

        return [ReadArtifact.model_validate(c) for c in response]

    def update_by_id(self, id: int, **updates) -> None:
        updates["updated_at"] = datetime.now()
        statement = (
            update(Artifact)
            .where(Artifact.id == id)
            .values(**updates)
            .execution_options(synchronize_session="fetch")
        )
        self.session.execute(statement)
        self.session.commit()

    def delete_by_id(self, id: int) -> bool:
        artifact = self.session.scalar(
            select(Artifact)
            .where(Artifact.id == id)
        )
        if not artifact:
            return False

        self.session.delete(artifact)
        self.session.commit()
        return True
