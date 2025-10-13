from datetime import datetime
from typing import List
from velo.db.conn import Session
from velo.db.models import Campaign
from velo.types.campaign import CreateCampaign, ReadCampaign, ReadFullCampaign
from sqlalchemy import desc, select
from sqlalchemy.orm import joinedload


class CampaignService:
    def __init__(self):
        self.session = Session

    def create(self, campaign: CreateCampaign) -> int | None:
        new_campaign = Campaign(
            chat_id=campaign.chat_id,
            request_text=campaign.request_text,
            created_at=datetime.now()
        )
        self.session.add(new_campaign)
        self.session.commit()
        self.session.refresh(new_campaign)
        return new_campaign.id

    def read_by_chat_id(self, chat_id: int) -> ReadCampaign | None:
        statement = (
            select(Campaign)
            .where(Campaign.chat_id == chat_id)
            .order_by(desc(Campaign.created_at))
        )
        response = self.session.scalars(statement).first()

        if response is not None:
            return ReadCampaign.model_validate(
                response
            )

    def readAll_by_chat_id(self, chat_id: int) -> List[ReadCampaign] | None:
        statement = (
            select(Campaign)
            .where(Campaign.chat_id == chat_id)
            .order_by(desc(Campaign.created_at))
        )
        response = self.session.scalars(statement).all()

        return [ReadCampaign.model_validate(c) for c in response]

    def readFull_by_chat_id(self, chat_id: int) -> ReadFullCampaign | None:
        statement = (
            select(Campaign)
            .where(Campaign.chat_id == chat_id)
            .order_by(desc(Campaign.created_at))
            .options(
                joinedload(Campaign.tasks),
                joinedload(Campaign.artifacts)
            )
        )
        response = self.session.scalars(statement).first()

        if response is not None:
            return ReadFullCampaign.model_validate(
                response
            )

    def delete_by_id(self, id: int) -> bool:
        campaign = self.session.scalar(
            select(Campaign)
            .where(Campaign.id == id)
        )
        if not campaign:
            return False

        self.session.delete(campaign)
        self.session.commit()
        return True
