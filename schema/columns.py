from pydantic import BaseModel
import typing
from schema.constraint import PgConstraint
from schema.attribute import PgAttribute


class Column(BaseModel):
	table_catalog: str
	table_schema: str
	table_name: str
	column_name: str
	ordinal_position: int
	column_default: typing.Optional[str]
	is_nullable: str
	data_type: str
	character_maximum_length: typing.Optional[int]
	character_octet_length: typing.Optional[int]
	numeric_precision: typing.Optional[int]
	numeric_precision_radix: typing.Optional[int]
	numeric_scale: typing.Optional[int]
	datetime_precision: typing.Optional[int]
	interval_type: typing.Optional[str]
	interval_precision: typing.Optional[int]
	character_set_catalog: typing.Optional[str]
	character_set_schema: typing.Optional[str]
	character_set_name: typing.Optional[str]
	collation_catalog: typing.Optional[str]
	collation_schema: typing.Optional[str]
	collation_name: typing.Optional[str]
	domain_catalog: typing.Optional[str]
	domain_schema: typing.Optional[str]
	domain_name: typing.Optional[str]
	udt_catalog: typing.Optional[str]
	udt_schema: typing.Optional[str]
	udt_name: typing.Optional[str]
	scope_catalog: typing.Optional[str]
	scope_schema: typing.Optional[str]
	scope_name: typing.Optional[str]
	maximum_cardinality: typing.Optional[int]
	dtd_identifier: typing.Optional[str]
	is_self_referencing: typing.Optional[str]
	is_identity: typing.Optional[str]
	identity_generation: typing.Optional[str]
	identity_start: typing.Optional[str]
	identity_increment: typing.Optional[str]
	identity_maximum: typing.Optional[str]
	identity_minimum: typing.Optional[str]
	identity_cycle: typing.Optional[str]
	is_generated: typing.Optional[str]
	generation_expression: typing.Optional[str]
	is_updatable: typing.Optional[str]
	attribute: typing.Optional[PgAttribute] = None
	constraint: typing.List[PgConstraint] = []
