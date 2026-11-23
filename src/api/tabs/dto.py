from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from src.api.tabs.model import TabBase

title_validation = Field(min_length=1, max_length=30)


class TabIn(BaseModel):
    id: UUID
    title: str = title_validation


class TabOut(TabBase):
    id: UUID


class TabUpdate(SQLModel):
    title: str = title_validation
