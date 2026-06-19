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
        try:
            cursor.execute(sql_script)
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
    2. Create schema + procedures (001-init.sql)
    3. Seed base data (002-seed-data.sql)
    4. Seed massive data if empty (003-seed-massive.sql)
    5. Update module educational content
    """
    print("\n" + "="*50)
    print("Database Initialization Starting...")
    print("="*50)

    # Step 1: Create database
    print("\n[1/5] Checking/Creating Database...")
    if not database_exists(settings.postgres_db):
        if not create_database(settings.postgres_db):
            print("  [ERROR] Failed to create database")
            return False

    # Step 2: Create schema + stored procedures
    print("\n[2/5] Creating Schema and Stored Procedures...")
    script_001 = find_script("001-init.sql")
    if script_001:
        try:
            conn = psycopg2.connect(
                host=settings.postgres_host, port=settings.postgres_port,
                user=settings.postgres_user, password=settings.postgres_password,
                database=settings.postgres_db
            )
            cursor = conn.cursor()
            with open(script_001, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            cursor.execute(sql_content)
            conn.commit()
            cursor.close()
            conn.close()
            print("  [OK] Schema and procedures created")
        except Exception as e:
            print(f"  [ERROR] Failed to create schema: {e}")
            return False
    else:
        print("  [WARN] 001-init.sql not found")

    # Step 3: Seed base data
    print("\n[3/5] Seeding Base Data...")
    script_002 = find_script("002-seed-data.sql")
    if script_002:
        try:
            if data_exists("users"):
                print("  [OK] Data already exists (seed skipped)")
            else:
                if execute_sql_file(script_002):
                    print("  [OK] Base data seeded successfully")
                else:
                    print("  [WARN] Seed had issues")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  [WARN] 002-seed-data.sql not found")

    # Step 3b: Seed massive data (only in development, skipped in production)
    print(f"\n[3b/5] Seeding Massive Test Data... (env: {settings.app_env})")
    if settings.app_env == "production":
        print("  [SKIP] Skipped in production (APP_ENV=production)")
    else:
        script_003 = find_script("003-seed-massive.sql")
        if script_003:
            if execute_sql_file(script_003):
                print("  [OK] Massive data seeded")
            else:
                print("  [WARN] Massive seed had issues (may already exist)")
        else:
            print("  [WARN] 003-seed-massive.sql not found, skipping")

    # Step 3c: Seed teacher data
    print(f"\n[3c/5] Seeding Teacher Data...")
    script_004 = find_script("004-seed-teacher-data.sql")
    if script_004:
        if execute_sql_file(script_004):
            print("  [OK] Teacher data seeded")
        else:
            print("  [WARN] Teacher seed had issues")
    else:
        print("  [WARN] 004-seed-teacher-data.sql not found, skipping")

    # Step 4: Enable pgvector
    print("\n[5/6] Enabling pgvector Extension...")
    script_005 = find_script("005-enable-pgvector.sql")
    if script_005:
        if execute_sql_file(script_005):
            print("  [OK] pgvector enabled")
        else:
            print("  [WARN] pgvector setup had issues")
    else:
        print("  [WARN] 005-enable-pgvector.sql not found")

    print("\n" + "="*50)
    print("[OK] Database initialization complete!")
    print("="*50 + "\n")
    return True

