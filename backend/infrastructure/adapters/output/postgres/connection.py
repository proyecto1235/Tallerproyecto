import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Generator
from config.settings import settings

class PostgresConnection:
    """PostgreSQL connection manager"""
    
    _pool = None
    
    @classmethod
    def init_pool(cls):
        """Initialize connection pool"""
        if cls._pool is None:
            cls._pool = SimpleConnectionPool(
                1,
                20,
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
            )
    
    @classmethod
    def close_pool(cls):
        """Close connection pool"""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
    
    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator:
        """Get a connection from the pool"""
        if cls._pool is None:
            cls.init_pool()
        
        conn = cls._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cls._pool.putconn(conn)
    
    @classmethod
    @contextmanager
    def get_cursor(cls):
        """Get a cursor from a pooled connection"""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
