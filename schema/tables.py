from pydantic import BaseModel
import typing
from schema.columns import Column
from schema.pg_class import PgClass


class Tables(BaseModel):

	table_catalog: str
	table_schema: str
	table_name: str
	table_type: str
	self_referencing_column_name: typing.Optional[str]
	reference_generation: typing.Optional[str]
	user_defined_type_catalog: typing.Optional[str]
	user_defined_type_schema: typing.Optional[str]
	user_defined_type_name: typing.Optional[str]
	is_insertable_into: typing.Optional[str]
	is_typed: typing.Optional[str]
	commit_action: typing.Optional[str]
	columns: typing.List[Column] = []
	table_class: typing.Optional[PgClass] = None
