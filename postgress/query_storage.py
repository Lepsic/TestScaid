"""QueryStorage в чем суть. Класс который должен хрнаить в себе sql запросы шаблонные для удаления, полученияб изменения
объектов в базе. У него есть методы которые возвращают sql запросы с заполненными данными из моделей"""
import inspect
import typing
import schema
import functools

command = typing.TypeVar("command", bound=schema.BaseCommandModel)


def check_type(
		fn: typing.Callable[[typing.Optional[command]], str]
):
	@functools.wraps(fn)
	def wrapper(cmd: typing.Optional[command] = None):
		annotations = inspect.getfullargspec(fn).annotations
		if cmd is not None:

			if not isinstance(cmd, schema.BaseCommandModel):
				print(fn.__name__)
				raise ValueError("cmd is not command.")

			if not isinstance(cmd, annotations["cmd"]):
				raise ValueError(f"Expected type: {annotations['cmd']} received type {type(cmd)}")
		return fn(cmd)

	return wrapper


class MetaQueryStorage(type):
	"""Нужен для проверки что исполняемая команда(по которой делается формируется запрос) соотвествует аннотации
	соотвествующей функции. Это вроде можно сделать через pydantic начиная со второй версии,
	но я решил остановиться на таком варианте.
	"""

	def __new__(cls, name, bases, dct):
		for attr_name, attr_value in dct.items():
			if callable(attr_value):
				dct[attr_name] = check_type(attr_value)
		return super().__new__(cls, name, bases, dct)


class QueryStorage(metaclass=MetaQueryStorage):
	"""Хранилище запросов к бд.
	Да я знаю про защиту от sql инъекций в asycpg
	Тут ее нет потому что этот функционал не подразумевает использования через api
	"""

	## Операции создания на уровне бд ##

	@staticmethod
	def create_table(cmd: schema.CreateTableCommand):
		columns_sql = ", ".join([
			f"{column.name} {column.data_type} {'NOT NULL' if not column.is_nullable else ''} "
			f"{'PRIMARY KEY' if column.is_primary_key else ''} "
			f"{'UNIQUE' if column.is_unique else ''} "
			f"{'DEFAULT {column.default_value}' if column.default_value else ''}"
			for column in cmd.columns
		])
		query = f"""
		create table {cmd.name}
		(
			{columns_sql}
		);
		"""
		return query

	@staticmethod
	def create_column(cmd: schema.CreateColumnCommand):
		query = f"""
			alter table {cmd.table_name}
			add column {cmd.name} {cmd.data_type} {'NOT NULL' if not cmd.is_nullable else ''}
			{'DEFAULT ' + cmd.default_value if cmd.default_value else ''};
		"""
		return query

	@staticmethod
	def create_index(cmd: schema.CreateIndexCommand):
		query = f"""
			create {'unique ' if cmd.is_unique else ''}index {cmd.index_name}
			on {cmd.table_name}
			using {cmd.index_type.value} ({cmd.column_name});
		"""
		return query

	@staticmethod
	def create_constraint(cmd: schema.CreateConstraintCommand) -> str:

		if cmd.constraint_type == schema.ConstraintTypeEnum.CHECK:
			query = f"""alter table {cmd.table_name}
			alter table {cmd.table_name}
			add constraint {cmd.constraint_name}
			check ({cmd.check_expression});
			"""
		if cmd.constraint_type == schema.ConstraintTypeEnum.FOREIGN_KEY:
			query = f"""
				alter table {cmd.table_name}
				add constraint {cmd.constraint_name}
				foreign key ({cmd.column_name})
				references {cmd.reference_table} ({cmd.reference_column});
			"""

		if cmd.constraint_type == schema.ConstraintTypeEnum.UNIQUE:
			query = f"""
				alter table {cmd.table_name}
				add constraint {cmd.constraint_name}
				unique ({cmd.column_name});
			"""
		if cmd.constraint_type == schema.ConstraintTypeEnum.PRIMARY_KEY:
			"""
				alter table {constraint.table_name}
				add constraint {constraint.constraint_name}
				primary key ({constraint.column_name});
			"""

		return query

	## Операции чтения на уровне бд ##

	@staticmethod
	def read_tables() -> str:
		"""Читаем все таблицы. Рассматриваю все табличные пространства, кроме внутренних"""
		query = f"""
			select
				table_catalog,
				table_schema,
				table_name,
				table_type,
				self_referencing_column_name,
				reference_generation,
				user_defined_type_catalog,
				user_defined_type_schema,
				user_defined_type_name,
				is_insertable_into,
				is_typed,
				commit_action
			from information_schema.tables
			where table_schema not in ('pg_catalog', 'information_schema')
		"""
		return query

	@staticmethod
	def read_columns(cmd: schema.ReadColumnsCommand) -> str:
		"""Читаем строк по таблицам"""
		query = f"""
		select table_catalog,
			table_schema,
			table_name,
			column_name,
			ordinal_position,
			column_default,
			is_nullable,
			data_type,
			character_maximum_length,
			character_octet_length,
			numeric_precision,
			numeric_precision_radix,
			numeric_scale,
			datetime_precision,
			interval_type,
			interval_precision,
			character_set_catalog,
			character_set_schema,
			character_set_name,
			collation_catalog,
			collation_schema,
			collation_name,
			domain_catalog,
			domain_schema,
			domain_name,
			udt_catalog,
			udt_schema,
			udt_name,
			scope_catalog,
			scope_schema,
			scope_name,
			maximum_cardinality,
			dtd_identifier,
			is_self_referencing,
			is_identity,
			identity_generation,
			identity_start,
			identity_increment,
			identity_maximum,
			identity_minimum,
			identity_cycle,
			is_generated,
			generation_expression,
			is_updatable
		from information_schema.columns
		where table_schema = '{cmd.table_schema}' and table_name = '{cmd.table_name}'
		"""
		return query

	@staticmethod
	def read_class_by_table(cmd: schema.ReadClassTable):
		"""Получаем pg_class для конкретной таблицы.
		Это нужно для получение атрибутов для столбцов
		В целом скорее есть еще какие-то кейсы которые я не рассматриваю
		"""
		query = f"""
		select 
			c.oid,
			c.relname,
			c.relnamespace,
			c.reltype,
			c.reloftype,
			c.relowner,
			c.relam,
			c.relfilenode,
			c.reltablespace,
			c.relpages,
			c.reltuples,
			c.relallvisible,
			c.reltoastrelid,
			c.relhasindex,
			c.relisshared,
			c.relpersistence,
			c.relkind,
			c.relnatts,
			c.relchecks,
			c.relhasrules,
			c.relhastriggers,
			c.relhassubclass,
			c.relrowsecurity,
			c.relforcerowsecurity,
			c.relispopulated,
			c.relreplident,
			c.relispartition,
			c.relfrozenxid,
			c.relminmxid,
			c.relacl,
			c.reloptions
		from pg_class c
		join pg_namespace n on c.relnamespace = n.oid
		where n.nspname = '{cmd.table_schema}'
		and c.relname = '{cmd.table_name}'
		"""
		return query

	@staticmethod
	def read_attribute_column(cmd: schema.ReadAttributeColumn):
		query = f"""
			select
				attrelid,
				attname,
				atttypid,
				attstattarget,
				attlen,
				attnum,
				attndims,
				attcacheoff,
				atttypmod,
				attbyval,
				attstorage,
				attalign,
				attnotnull,
				atthasdef,
				attidentity,
				attgenerated,
				attisdropped,
				attislocal,
				attinhcount,
				attcollation,
				attacl,
				attoptions,
				attfdwoptions
			from pg_attribute
			where attname = '{cmd.column_name}' and attrelid = '{cmd.oid}'
		"""
		return query


	@staticmethod
	def read_constraint_by_column(cmd: schema.ReadConstraintByColumn):
		"""Читаем constraint. Читаем по oid таблицы и attnum поля"""
		query = f"""
			select 
				conname,
				connamespace,
				conrelid,
				conindid,
				contype,
				condeferrable,
				condeferred,
				convalidated,
				conkey,
				confkey,
				confrelid,
				confupdtype,
				confdeltype,
				confmatchtype,
				conislocal,
				coninhcount,
				connoinherit
			from
				pg_constraint
			where conrelid = '{cmd.conrelid}' and {cmd.attnum} = ANY (conkey::int[]);
		"""
		return query


