import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseSettings, EmailStr, PostgresDsn, validator, root_validator


class Settings(BaseSettings):
	class Config:
		env_file = ".env"
	
	DOCKER_MODE: Optional[bool] = True
	BASE_DIR: Optional[Path] = Path(__file__).resolve().parent.parent.parent
	STATICFILES_URL: Optional[str] = "static"
	STATICFILES_ROOT: Path
	
	@validator('STATICFILES_ROOT', pre=True)
	def set_staticfiles_dir(cls, v: str):
		if v:
			user_set_path = Path(__file__).resolve().parent.parent.parent / v
			if user_set_path.exists():
				if user_set_path.is_dir():
					return user_set_path
				else:
					raise ValueError(
						"This path exist and its not a directory, give me "
						"another name or delete that file and run me again"
					)
			else:
				user_set_path.mkdir(exist_ok=True, parents=True)
				return user_set_path
		else:
			app_path: Path = Path(__file__).resolve().parent.parent.parent
			default_path = app_path / 'staticfiles'
			if default_path.exists():
				if default_path.is_dir():
					return default_path
				else:
					raise ValueError(
						"there is a file with staticfiles name in the base directory, "
						"please set staticfiles dir in environment or delete the file"
					)
			else:
				try:
					default_path.mkdir(exist_ok=True, parents=True)
				# Path("/fast_asgi_app/").joinpath('staticfiles').mkdir(exist_ok=True, parents=True)
				except Exception as e:
					raise ValueError(e)
				return default_path
	
	"""APPLICATION SETTINGS"""
	
	DEBUG: bool
	""" Server Settings"""
	API_PREFIX: Optional[str] = None
	PROJECT_HOST_OR_DNS: Optional[str]
	USERS_OPEN_REGISTRATION: Optional[bool] = True
	MAXIMUM_ITEMS_PER_PAGE: Optional[int] = 50
	
	"""     CORS_SETTINGS    """
	ALLOWED_HEADERS: List[str] = []
	ALLOWED_METHODS: List[str] = []
	ALLOWED_CREDENTIALS: bool = False
	ALLOWED_ORIGINS: Optional[List[str]] = []
	DATABASE_URL: Optional[str] = None
	ALLOWED_HOSTS: Optional[List[str]] = ["*"]
	
	@validator("DATABASE_URL", pre=True)
	def get_arman(cls, v: Optional[str], values: Dict[str, Any]):
		return v
	
	""" Cross Site Request Forgery SETTINGS"""
	CSRF_TOKEN_HEADER_NAME: str
	CSRF_TOKEN_COOKIE_NAME: str
	CSRF_TOKEN_COOKIE_PATH: str
	FRONTEND_DOMAIN: str
	CSRF_TOKEN_SECRET: str
	TOKEN_SENSITIVE_COOKIES: Set[str]
	
	@validator("TOKEN_SENSITIVE_COOKIES", pre=True)
	def make_set(cls, v):
		name = set()
		for i in v:
			name.add(i)
		return name
	
	""" JWT SETTINGS"""
	SECRET_KEY: str
	ACCESS_TOKEN_EXPIRATION_MINUTES: int
	ALGORITHM: str
	
	""" Email Settings"""
	SMTP_TLS: Optional[bool]
	SMTP_PORT: Optional[int]
	SMTP_HOST: Optional[str]
	SMTP_USER: Optional[str]
	SMTP_PASSWORD: Optional[str]
	EMAIL_RESET_TOKEN_EXPIRE_HOURS: Optional[int]
	PROJECT_NAME: Optional[str]
	EMAIL_TEMPLATES_DIR: Optional[str]
	SERVER_HOST: Optional[str]
	EMAILS_ENABLED: Optional[bool] = True
	EMAILS_FROM_NAME: Optional[str]
	EMAILS_FROM_EMAIL: Optional[EmailStr] = None
	
	@validator("EMAILS_FROM_NAME")
	def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
		if not v:
			return values["PROJECT_NAME"]
		return v
	
	""" Postgresql Settings """
	POSTGRES_SERVER: str
	POSTGRES_USER: str
	POSTGRES_PASSWORD: str
	POSTGRES_DB: str
	SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
	
	""" Sqlite3 """
	DATABASE_USER: Optional[str]
	DATABASE_PASSWORD: Optional[str]
	
	@validator("SQLALCHEMY_DATABASE_URI", pre=True)
	def assemble_db_connection(cls, v: Optional[str], values: Dict[str, any]) -> any:
		if isinstance(v, str):
			return v
		else:
			return PostgresDsn.build(
				scheme="postgresql",
				host=values.get("POSTGRES_SERVER"),
				user=values.get("POSTGRES_USER"),
				password=values.get("POSTGRES_PASSWORD"),
				path=f"/{values.get('POSTGRES_DB') or ''}",
			)
	
	SQLALCHEMY_ASYNC_DATABASE_URI: Optional[str] = None
	
	@validator("SQLALCHEMY_ASYNC_DATABASE_URI", pre=True)
	def async_assemble_db_connection(
		cls, v: Optional[str], values: Dict[str, any]
	) -> any:
		if isinstance(v, str):
			return v
		else:
			return PostgresDsn.build(
				scheme="postgresql+asyncpg",
				host=values.get("POSTGRES_SERVER"),
				user=values.get("POSTGRES_USER"),
				password=values.get("POSTGRES_PASSWORD"),
				path=f"/{values.get('POSTGRES_DB') or ''}",
			)
	
	""" Gunicorn Configs """
	WORKERS_PER_CORE: Optional[int or bool] = False
	MAX_WORKERS: Optional[int] = 0
	WEB_CONCURRENCY: Optional[int]
	HOST: Optional[str]
	PORT: Optional[int]
	BIND: Optional[bool] = False
	LOG_LEVEL: Optional[str] = None
	ACCESS_LOG: Optional[str] = "-"
	ERROR_LOG: Optional[str] = "-"
	GRACEFUL_TIMEOUT: Optional[int]
	TIMEOUT: Optional[int]
	KEEP_ALIVE: Optional[int]


a = os.environ.get("DOCKER_MODE")
if a or a == "True":
	settings = Settings()
else:
	settings = Settings(
		_env_file=Path(__name__).resolve().parent / "configurations/.env"
	)


@lru_cache
def get_settings():
	return Settings()
