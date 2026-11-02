import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "cycle_ai")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def get_db_url() -> str:
    """Retorna a URL de conexão para o SQLAlchemy."""
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_engine():
    """Retorna uma instância da engine SQLAlchemy com pool configurado."""
    return create_engine(
        get_db_url(),
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )


def get_connection():
    """Retorna uma conexão bruta psycopg2 configurada com autocommit desativado por padrão."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def get_dict_cursor(conn):
    """Retorna um cursor psycopg2 que devolve resultados como dicionários."""
    return conn.cursor(cursor_factory=RealDictCursor)

