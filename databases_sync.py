import asyncio
import typing
from postgress import query_executor, query_storage
from postgress.connector import Connector
import schema
import settings


class DatabaseSync:
	source_database: schema.Database
	target_database: schema.Database

	def __init__(self):
		self.source_database_executor = query_executor.QueryExecutor(
			connector=Connector(
				dsn=settings.settings.SOURCE_DATABASE,
			)
		)
		self.target_database_executor = query_executor.QueryExecutor(
			connector=Connector(
				dsn=settings.settings.TARGET_DATABASE,
			)
		)
		self.source_database = schema.Database()
		self.target_database = schema.Database()

	@staticmethod
	async def fetch_database_status(executor: query_executor.QueryExecutor, database: schema.Database):
		loop = asyncio.get_event_loop()
		database.tables = await executor.read_tables()
		tasks = []
		for table in database.tables:
			tasks.append(
				loop.create_task(
					executor.read_column(
						cmd=schema.ReadColumnsCommand(
							table_name=table.table_name,
							table_schema=table.table_schema,
						)
					)
				)
			)

		await asyncio.gather(*tasks)
		for table, task in zip(database.tables, tasks):
			table.columns = task.result()

		tasks.clear()

		for table in database.tables:
			tasks.append(
				loop.create_task(
					executor.read_class_by_table(
						cmd=schema.ReadClassTable(
							table_name=table.table_name,
							table_schema=table.table_schema,
						)
					)
				)
			)
		await asyncio.gather(*tasks)
		for table, task in zip(database.tables, tasks):
			table.table_class = task.result()

		for table in database.tables:
			for column in table.columns:
				column.attribute = await executor.read_attribute_by_column(
					cmd=schema.ReadAttributeColumn(
						oid=table.table_class.oid,
						column_name=column.column_name,
					)
				)
				column.constraint = await executor.read_constraint_by_column(
					cmd=schema.ReadConstraintByColumn(
						attnum=column.attribute.attnum,
						conrelid=table.table_class.oid,
					)
				)

	async def fetch_data(self):
		await asyncio.gather(
			self.fetch_database_status(
				executor=self.source_database_executor,
				database=self.source_database
			),
			self.fetch_database_status(
				executor=self.target_database_executor,
				database=self.target_database,
			)
		)

	async def sync_databases(self):
		create_table_commands = []
		create_column_commands = []
		create_constraint_commands = []

		source_tables = {table.table_name: table for table in self.source_database.tables}
		target_tables = {table.table_name: table for table in self.target_database.tables}

		# Find missing tables in the target database
		for table_name, source_table in source_tables.items():
			if table_name not in target_tables:
				columns = [
					schema.CreateColumnCommand(
						table_name=table_name,
						name=column.column_name,
						data_type=column.data_type,
						is_nullable=column.is_nullable == 'YES',
						default_value=column.column_default,
						is_primary_key=any(
							constraint.constraint_type == 'PRIMARY KEY' for constraint in column.constraint),
						is_unique=any(constraint.constraint_type == 'UNIQUE' for constraint in column.constraint),
						is_indexed=any(constraint.constraint_type == 'INDEX' for constraint in column.constraint),
					)
					for column in source_table.columns
				]
				create_table_commands.append(schema.CreateTableCommand(name=table_name, columns=columns))

		#  ищем таблицы которых не хватает
		for table_name, target_table in target_tables.items():
			if table_name in source_tables:
				source_table = source_tables[table_name]
				source_columns = {column.column_name: column for column in source_table.columns}
				target_columns = {column.column_name: column for column in target_table.columns}

				for column_name, source_column in source_columns.items():
					if column_name not in target_columns:
						create_column_commands.append(
							schema.CreateColumnCommand(
								table_name=table_name,
								name=column_name,
								data_type=source_column.data_type,
								is_nullable=source_column.is_nullable == 'YES',
								default_value=source_column.column_default,
								is_primary_key=any(constraint.constraint_type == 'PRIMARY KEY' for constraint in
												   source_column.constraint),
								is_unique=any(
									constraint.constraint_type == 'UNIQUE' for constraint in source_column.constraint),
								is_indexed=any(
									constraint.constraint_type == 'INDEX' for constraint in source_column.constraint),
							)
						)

				# ищем constraint которых не хватает
				for column_name, source_column in source_columns.items():
					if column_name in target_columns:
						target_column = target_columns[column_name]
						for source_constraint in source_column.constraint:
							if source_constraint not in target_column.constraint:
								create_constraint_commands.append(
									schema.CreateConstraintCommand(
										table_name=table_name,
										constraint_name=source_constraint.constraint_name,
										constraint_type=schema.ConstraintTypeEnum(source_constraint.constraint_type),
										column_name=column_name,
										reference_table=source_constraint.reference_table,
										reference_column=source_constraint.reference_column,
										check_expression=source_constraint.check_expression,
									)
								)
		await asyncio.gather(
			*[
				self.target_database_executor.execute(
					query_storage.QueryStorage.create_table(cmd=cmd)
				)
				for cmd in create_table_commands
			]
		)
		await asyncio.gather(
			*[
				self.target_database_executor.execute(
					query_storage.QueryStorage.create_column(cmd=cmd)
				)
				for cmd in create_column_commands
			]
		)
		await asyncio.gather(
			*[
				self.target_database_executor.execute(
					query_storage.QueryStorage.create_constraint(cmd=cmd)
				)
				for cmd in create_constraint_commands
			]
		)


async def pipeline():
	instance = DatabaseSync()
	await instance.fetch_data()


if __name__ == "__main__":
	asyncio.run(pipeline())
