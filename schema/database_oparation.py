import typing
from enum import Enum
from pydantic import BaseModel


class ConstraintTypeEnum(Enum):
	CHECK = "check"
	FOREIGN_KEY = "foreign key"
	UNIQUE = "unique"
	PRIMARY_KEY = "primary key"

class IndexTypeEnum(Enum):
	BTREE = 'btree'
	HASH = 'hash'
	GIST = 'gist'
	GIN = 'gin'
	BRIN = 'brin'
	SPGIST = 'spgist'



class BaseCommandModel(BaseModel):
	"""Базовый класс для комманд по операциям с бд"""


class CreateColumnCommand(BaseCommandModel):
	table_name: str
	name: str
	data_type: str
	is_nullable: bool = True
	default_value: typing.Optional[str] = None
	is_primary_key: bool = False
	is_unique: bool = False
	is_indexed: bool = False


class CreateTableCommand(BaseCommandModel):
	name: str
	columns: typing.List[CreateColumnCommand]


class CreateConstraintCommand(BaseCommandModel):
	table_name: str
	constraint_name: str
	constraint_type: ConstraintTypeEnum
	column_name: typing.Optional[str] = None
	reference_table: typing.Optional[str] = None
	reference_column: typing.Optional[str] = None
	check_expression: typing.Optional[str] = None


class CreateIndexCommand(BaseCommandModel):
	table_name: str
	column_name: str
	index_name: str
	index_type: IndexTypeEnum = IndexTypeEnum.BTREE
	is_unique: bool = False


# Read operation

class ReadColumnsCommand(BaseCommandModel):
	table_name: str
	table_schema: str


class ReadClassTable(BaseCommandModel):
	table_name: str
	table_schema: str


class ReadAttributeColumn(BaseCommandModel):
	oid: int  # это идентификатор таблицы(на самом деле не только таблицы, но еще и constraint, view и тд
	column_name: str


class ReadConstraintByColumn(BaseCommandModel):
	attnum: int  # порядковый номер(хз как это работает но постгря мэчит индексы по атрибуту столбца)
	conrelid: int  # он же oid


