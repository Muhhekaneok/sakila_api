import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import MySQLConnection

load_dotenv()


def _get_env_var(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


def get_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=_get_env_var("DB_HOST"),
        user=_get_env_var("DB_USER"),
        password=_get_env_var("DB_PASSWORD"),
        database=_get_env_var("DB_NAME")
    )


def get_logging_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=_get_env_var("LOG_DB_HOST"),
        user=_get_env_var("LOG_DB_USER"),
        password=_get_env_var("LOG_DB_PASSWORD"),
        database=_get_env_var("LOG_DB_NAME")
    )