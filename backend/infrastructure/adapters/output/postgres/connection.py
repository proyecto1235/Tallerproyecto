import psycopg2
from psycopg2.pool import SimpleConnectionPool, ThreadedConnectionPool
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
import asyncio
from config.settings import settings

class PostgresConnection:
    """PostgreSQL connection manager with configurable pool"""

    _pool = None

    @classmethod
    def init_pool(cls):
        """Initialize connection pool"""
        if cls._pool is None:
            cls._pool = ThreadedConnectionPool(
                settings.db_pool_min,
                settings.db_pool_max,
                host=settings.postgres_host,
                port=settings.postgres_port,
                dbname=settings.postgres_db,
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

    @classmethod
    @asynccontextmanager
    async def async_cursor(cls) -> AsyncGenerator:
        """Async cursor that runs DB operations in a thread pool executor
        to avoid blocking the event loop under high concurrency."""
        loop = asyncio.get_event_loop()
        conn = await loop.run_in_executor(None, cls._pool.getconn)
        try:
            cursor = await loop.run_in_executor(None, conn.cursor)
            try:
                yield cursor
            finally:
                await loop.run_in_executor(None, cursor.close)
            await loop.run_in_executor(None, conn.commit)
        except Exception as e:
            await loop.run_in_executor(None, conn.rollback)
            raise e
        finally:
            await loop.run_in_executor(None, cls._pool.putconn, conn)
