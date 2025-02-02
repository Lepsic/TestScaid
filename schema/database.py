import typing
from pydantic import BaseModel
import schema


class Database(BaseModel):
	"""класс базы данных. Сущность через которую мы можем получать все данные из бд и проводить атомарные операции"""

	tables: typing.List[schema.Tables] = []

