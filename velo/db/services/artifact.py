from datetime import datetime
from typing import List
from velo.db.conn import DBConn
from velo.db.models import Artifact
from velo.types.artifact import CreateArtifact, ReadArtifact
from sqlalchemy import desc, select


class ArtifactService:
    def __init__(self):
        self.session = DBConn().session()

    def create(self, artifact: CreateArtifact) -> int | None:
        new_task = Artifact(
            task_id=artifact.task_id,
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
