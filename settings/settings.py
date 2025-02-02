"""Работаю с env используя pydantic"""
from pydantic_settings import BaseSettings
from dotenv import find_dotenv

__all__ = [
	"get_setting",
	"Settings",
	"PostgresDsn"
]


class _Setting(BaseSettings):

	class Config:

		env_file_encoding = "utf-8"
		arbitrary_types_allowed = True
		case_sensitive = True
		env_nested_delimiter = "__"


class PostgresDsn(_Setting):
	HOST: str
	PORT: int
	USER: str
	PASSWORD: str
	DATABASE: str
	SCHEMA: str = "psql"

	def get_dsn(self) -> str:
		return f"{self.SCHEMA}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"


class Settings(_Setting):
	SOURCE_DATABASE: PostgresDsn
	TARGET_DATABASE: PostgresDsn




def get_setting(env_file=".env") -> Settings:
	return Settings(_env_file=find_dotenv(env_file))
