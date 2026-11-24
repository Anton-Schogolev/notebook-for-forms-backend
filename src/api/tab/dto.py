from pydantic import BaseModel

from src.api.tab.model import InfoField
from src.api.tabs.dto import TabOut


class TabDetailOut(TabOut):
    content: list[InfoField]


class TabContentUpdate(BaseModel):
    content: list[InfoField]
