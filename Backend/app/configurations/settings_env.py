import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import (
	AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator,
)


class Settings(BaseSettings):
	DEBUG: bool = False
	# DOCKER_MODE = Optional[bool] = False
	""" APPLICATION SETTINGS """
	""" Server Settings"""
	API_PREFIX: Optional[str]
	
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
	EMAILS_FROM_EMAIL: Optional[EmailStr]
	
	""" Postgresql Settings """
	POSTGRES_SERVER: Optional[str]
	POSTGRES_USER: Optional[str]
	POSTGRES_PASSWORD: Optional[str]
	POSTGRES_DB: Optional[str]
	""" Sqlite3 """
	DATABASE_URL: Optional[str]
	DATABASE_USER: Optional[str]
	DATABASE_PASSWORD: Optional[str]
	
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
	settings = Settings(_env_file=Path(__name__).resolve().parent / "configurations/.env")
