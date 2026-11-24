from typing import TypedDict
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class InfoField(SQLModel):
    id: UUID
    title: str = Field(max_length=50)
    content: str = Field(max_length=500)


class StoredInfoField(TypedDict):
    id: str
    title: str
    content: str


class TabContent(SQLModel, table=True):
    tab_id: UUID = Field(primary_key=True, foreign_key="tab.id")
    items: list[StoredInfoField] = Field(default_factory=list, sa_type=JSONB)
