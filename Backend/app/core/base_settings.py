import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import (
	BaseSettings, EmailStr, PostgresDsn, validator,
)


class Settings(BaseSettings):
	DEBUG: bool = False
	# DOCKER_MODE = Optional[bool] = True
	
	""" APPLICATION SETTINGS """
	""" Server Settings"""
	API_PREFIX: Optional[str]
	PROJECT_NAME: Optional[str]
	""" JWT SETTINGS"""
	SECRET_KEY: Optional[str]
	ACCESS_TOKEN_EXPIRATION_MINUTES: Optional[int]
	ALGORITHM: Optional[str]
	
	""" Email Settings"""
	SMTP_TLS: Optional[bool]
	SMTP_PORT: Optional[int]
	SMTP_HOST: Optional[str]
	SMTP_USER: Optional[str]
	SMTP_PASSWORD: Optional[str]
	EMAILS_FROM_NAME:Optional[str]
	EMAILS_FROM_EMAIL: Optional[EmailStr]
	EMAIL_RESET_TOKEN_EXPIRE_HOURS: Optional[int]
	EMAIL_TEMPLATES_DIR: Optional[str]
	SERVER_HOST: Optional[str]
	EMAILS_ENABLED: bool = False
	
	@validator("EMAILS_ENABLED", pre=True)
	def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
		return bool(
			values.get("SMTP_HOST")
			and values.get("SMTP_PORT")
			and values.get("EMAILS_FROM_EMAIL")
		)
	
	""" Postgresql Settings """
	POSTGRES_SERVER: str
	POSTGRES_USER: str
	POSTGRES_PASSWORD: str
	POSTGRES_DB: str
	SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
	
	""" Sqlite3 """
	DATABASE_USER: Optional[str]
	DATABASE_PASSWORD: Optional[str]
	
	@validator('SQLALCHEMY_DATABASE_URI', pre=True)
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
	"""     CORS_CONFIGS    """
	ALLOWED_HEADERS: List[str] = []
	ALLOWED_METHODS: List[str] = []
	ALLOWED_CREDENTIALS: bool = False
	ALLOWED_ORIGINS: Optional[List[str]] = []
	DATABASE_URL: Optional[str] = None
	
	@validator("DATABASE_URL", pre=True)
	def get_arman(cls, v: Optional[str], values: Dict[str, Any]):
		return v
	
	ALLOWED_HOSTS: List[str]


# @validator("BACKEND_CORS_ORIGINS", pre=True)
# def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
# 	if isinstance(v, str) and not v.startswith("["):
# 		return [i.strip() for i in v.split(",")]
# 	elif isinstance(v, (list, str)):
# 		return v
# 	raise ValueError(v)


a = os.environ.get("DOCKER_MODE")
if a or a == "True":
	settings = Settings()
else:
	settings = Settings(_env_file=Path(__name__).resolve().parent.parent.parent / ".env")
