from pydantic import BaseModel
import typing


class PgClass(BaseModel):
    oid: int
    relname: str
    relnamespace: int
    reltype: int
    reloftype: int
    relowner: int
    relam: int
    relfilenode: int
    reltablespace: int
    relpages: int
    reltuples: float
    relallvisible: int
    reltoastrelid: int
    relhasindex: bool
    relisshared: bool
    relpersistence: str
    relkind: str
    relnatts: int
    relchecks: int
    relhasrules: bool
    relhastriggers: bool
    relhassubclass: bool
    relrowsecurity: bool
    relforcerowsecurity: bool
    relispopulated: bool
    relreplident: str
    relispartition: bool
    relfrozenxid: int
    relminmxid: int
    relacl: typing.Optional[str]
    reloptions: typing.Optional[str]
