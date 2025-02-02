import functools
import inspect
import typing
from typing import Awaitable, Callable
import asyncpg
import pydantic

from postgress.connector import Connector
from pydantic import BaseModel
import schema
from postgress.query_storage import QueryStorage

model = typing.TypeVar("model", bound=BaseModel)
command = typing.TypeVar("command", bound=schema.BaseCommandModel)



def parse_to_pydantic(
		fn: Callable[..., Awaitable[model]]
) -> Callable[..., Awaitable[model]]:
	"""Преобразование моделей к пиндантику(тип к которому приводим берем из аннотаций"""

	@functools.wraps(fn)
	async def wrapper(*args, **kwargs):
		try:
			annotations = inspect.getfullargspec(fn).annotations["return"]
			adapter = pydantic.TypeAdapter(annotations)
			record: typing.Union[asyncpg.Record, typing.List[asyncpg.Record]] = await fn(*args, **kwargs)
			try:
				if issubclass(list, typing.get_origin(annotations)):
					for r in range(len(record)):
						record[r] = dict(record[r])
					return adapter.validate_python(record)
			except TypeError:
				pass
			print(record)
			return adapter.validate_python(dict(record))
		except Exception as error:
			print(error)
			raise error

	return wrapper


class QueryExecutor:
	"""Класс для отправки запросов к бд"""
	def __init__(self, connector: Connector):
		self.connector = connector



	async def fetch(
			self,
			statement: typing.Union[str, typing.Callable],
			many=True,
	) -> model:  #typing.Union[asyncpg.Record, typing.List[asyncpg.Record]]: - закоменченая аннотация - корректная
		"""Запрос с возвратом данных( в контексте класса - это read запросы к базе)"""
		if callable(statement):
			statement = statement()
		async with self.connector.get_connection() as cursor:
			if many:
				return await cursor.fetch(statement)
			return await cursor.fetchrow(statement)


	async def execute(
		self,
		statement: typing.Union[str, typing.Callable],
	) -> None:
		"""Запрос который не возвращает данные"""
		if callable(statement):
			statement = statement()
		async with self.connector.get_connection() as cursor:
			await cursor.execute(statement)

	@parse_to_pydantic
	async def read_tables(self) -> typing.List[schema.Tables]:
		return await self.fetch(statement=QueryStorage.read_tables())

	@parse_to_pydantic
	async def read_column(self, cmd: schema.ReadColumnsCommand) -> typing.List[schema.Column]:
		return await self.fetch(statement=QueryStorage.read_columns(cmd=cmd))

	@parse_to_pydantic
	async def read_class_by_table(self, cmd: schema.ReadClassTable) -> schema.PgClass:
		return await self.fetch(QueryStorage.read_class_by_table(cmd=cmd), many=False)

	@parse_to_pydantic
	async def read_attribute_by_column(self, cmd: schema.ReadAttributeColumn) -> schema.PgAttribute:
		return await self.fetch(QueryStorage.read_attribute_column(cmd=cmd), many=False)

	@parse_to_pydantic
	async def read_constraint_by_column(self, cmd: schema.ReadConstraintByColumn) -> typing.List[schema.PgConstraint]:
		return await self.fetch(QueryStorage.read_constraint_by_column(cmd=cmd))
