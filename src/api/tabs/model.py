from uuid import UUID

from sqlmodel import Field, SQLModel


class TabBase(SQLModel):
    title: str
    version: int


class Tab(TabBase, table=True):
    id: UUID = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
