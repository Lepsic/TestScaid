from pydantic import BaseModel
from typing import Optional


class PgConstraint(BaseModel):
    conname: str
    connamespace: int
    conrelid: int
    conindid: Optional[int]
    contype: str
    condeferrable: bool
    condeferred: bool
    convalidated: bool
    conkey: Optional[list[int]]
    confkey: Optional[list[int]]
    confrelid: Optional[int]
    confupdtype: Optional[str]
    confdeltype: Optional[str]
    confmatchtype: Optional[str]
    conislocal: bool
    coninhcount: int
    connoinherit: bool
