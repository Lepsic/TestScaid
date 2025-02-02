"""Получение коннектов к базе"""
import typing

from settings.settings import PostgresDsn
import asyncpg
from asyncpg.pool import PoolAcquireContext
from contextlib import asynccontextmanager


class Connector:
	pool: asyncpg.pool = None
	dsn: str

	def __init__(self, dsn: PostgresDsn):
		self.dsn = dsn.get_dsn()


	@asynccontextmanager
	async def get_connection(self) -> typing.AsyncGenerator[PoolAcquireContext, None]:
		if self.pool is None:
			self.pool = await asyncpg.create_pool(dsn=self.dsn)
		async with self.pool.acquire() as connection:
			yield connection

