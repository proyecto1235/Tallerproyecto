"""
Database initialization module - Creates database, tables, and seeds data if they don't exist
"""
import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from config.settings import settings

def find_script(name: str):
    """Find a SQL script by name"""
    base = Path(__file__).parent.parent / "scripts"
    paths = [
        base / name,
        Path("backend/scripts") / name,
        Path("scripts") / name,
    ]
    for p in paths:
        if p.exists():
            return p
    return None

def database_exists(db_name: str) -> bool:
    """Check if database exists"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone() is not None
        cursor.close(); conn.close()
        return exists
    except Exception as e:
        print(f"Error checking if database exists: {e}")
        return False

def create_database(db_name: str):
    """Create database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        try:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        except psycopg2.Error as e:
            if "already exists" not in str(e).lower():
                raise
        cursor.close(); conn.close()
        print(f"[OK] Database '{db_name}' is ready")
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def table_exists(cursor, table_name: str) -> bool:
    """Check if a table exists"""
    try:
        cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = %s AND table_schema = 'public'",
            (table_name,)
        )
        return cursor.fetchone() is not None
    except:
        return False

def execute_sql_file(file_path: Path) -> bool:
    """Execute SQL file against the database"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database=settings.postgres_db
        )
        cursor = conn.cursor()
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        statements = sql_script.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except psycopg2.Error as e:
                    msg = str(e).lower()
                    if "conflict" in msg or "already exists" in msg:
                        pass
                    elif "syntax" in msg:
                        pass
                    else:
                        print(f"  [WARN] {e}")
        conn.commit()
        cursor.close(); conn.close()
        print(f"[OK] Executed: {file_path.name}")
        return True
    except Exception as e:
        print(f"Error executing SQL file {file_path}: {e}")
        return False

def data_exists(table_name: str) -> bool:
    """Check if data exists in a table"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database=settings.postgres_db
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.close(); conn.close()
        return count > 0
    except:
        return False

def initialize_database():
    """
    Initialize database:
    1. Create database
    2. Create tables (001-create-tables.sql)
    3. Seed data (002-seed-data.sql)
    """
    print("\n" + "="*50)
    print("Database Initialization Starting...")
    print("="*50)

    print("\n[1/3] Checking/Creating Database...")
    if not database_exists(settings.postgres_db):
        print(f"  Creating database '{settings.postgres_db}'...")
        if not create_database(settings.postgres_db):
            print("  [ERROR] Failed to create database")
            return False
    else:
        print(f"  [OK] Database '{settings.postgres_db}' already exists")

    script_001 = find_script("001-create-tables.sql")
    script_002 = find_script("002-seed-data.sql")

    print("\n[2/3] Creating Tables...")
    if script_001:
        if execute_sql_file(script_001):
            print("  [OK] Tables created successfully")
        else:
            print("  [ERROR] Failed to create tables")
            return False
    else:
        print("  [WARN] 001-create-tables.sql not found")

    print("\n[3/3] Seeding Data...")
    if script_002:
        try:
            if data_exists("users"):
                print("  [OK] Data already exists (seed skipped)")
            else:
                if execute_sql_file(script_002):
                    print("  [OK] Data seeded successfully")
                else:
                    print("  [WARN] Seed had issues")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  [WARN] 002-seed-data.sql not found")

    print("\n" + "="*50)
    print("[OK] Database initialization complete!")
    print("="*50 + "\n")
    return True
