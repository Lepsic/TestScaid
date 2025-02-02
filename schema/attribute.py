from pydantic import BaseModel
from typing import Optional


class PgAttribute(BaseModel):
    attrelid: int
    attname: str
    atttypid: int
    attstattarget: Optional[int]
    attlen: int
    attnum: int  # номер атрибута. Учавствует в constraint
    attndims: int
    attcacheoff: Optional[int]
    atttypmod: int
    attbyval: bool
    attstorage: str
    attalign: str
    attnotnull: bool
    atthasdef: bool
    attidentity: str
    attgenerated: str
    attisdropped: bool
    attislocal: bool
    attinhcount: int
    attcollation: Optional[int]
    attacl: Optional[str]
    attoptions: Optional[str]
    attfdwoptions: Optional[str]
