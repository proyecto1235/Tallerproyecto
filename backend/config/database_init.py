"""
Database initialization module - Creates database, tables, and seeds data if they don't exist
"""
import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from config.settings import settings

def get_sql_scripts():
    """Get paths to SQL scripts"""
    # Try multiple possible locations, prioritize backend/scripts first
    possible_paths = [
        # Backend scripts (priority)
        Path(__file__).parent.parent / "scripts" / "001-create-tables.sql",
        Path(__file__).parent.parent / "scripts" / "002-seed-data.sql",
        # Root scripts
        Path(__file__).parent.parent.parent / "scripts" / "001-create-tables.sql",
        Path(__file__).parent.parent.parent / "scripts" / "002-seed-data.sql",
        # Relative paths
        Path("backend/scripts/001-create-tables.sql"),
        Path("backend/scripts/002-seed-data.sql"),
        Path("scripts/001-create-tables.sql"),
        Path("scripts/002-seed-data.sql"),
    ]
    
    scripts = {}
    for path in possible_paths:
        if path.exists():
            if "001" in str(path):
                if "create_tables" not in scripts:
                    scripts["create_tables"] = path
            elif "002" in str(path):
                if "seed_data" not in scripts:
                    scripts["seed_data"] = path
    
    return scripts

def database_exists(db_name: str) -> bool:
    """Check if database exists"""
    try:
        # Connect to default postgres database to check
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database="postgres"
        )
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        return exists
    except Exception as e:
        print(f"Error checking if database exists: {e}")
        return False

def create_database(db_name: str):
    """Create database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        try:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
        except psycopg2.Error as e:
            if "already exists" in str(e).lower():
                print(f"  [OK] Database '{db_name}' already exists")
            else:
                raise
        
        cursor.close()
        conn.close()
        print(f"[OK] Database '{db_name}' is ready")
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def table_exists(cursor, table_name: str) -> bool:
    """Check if a table exists"""
    try:
        cursor.execute(
            """
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = %s AND table_schema = 'public'
            """,
            (table_name,)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking if table exists: {e}")
        return False

def execute_sql_file(file_path: Path) -> bool:
    """Execute SQL file against the database"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        cursor = conn.cursor()
        
        # Read and execute SQL file
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Execute all commands in the script
        # Split by semicolon to execute statements one by one (better error handling)
        statements = sql_script.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:  # Only execute non-empty statements
                try:
                    cursor.execute(statement)
                except psycopg2.Error as e:
                    # Log the error but continue with other statements
                    # This allows INSERT conflicts to be skipped while still creating tables
                    error_msg = str(e).lower()
                    if "conflict" in error_msg or "already exists" in error_msg:
                        # These are expected errors in seed scripts
                        pass
                    else:
                        print(f"  [WARN] Warning in SQL execution: {e}")
        
        conn.commit()
        
        cursor.close()
        conn.close()
        print(f"[OK] Executed: {file_path.name}")
        return True
    except Exception as e:
        print(f"Error executing SQL file {file_path}: {e}")
        return False

def data_exists(table_name: str) -> bool:
    """Check if data exists in a table"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"Error checking if data exists: {e}")
        return False

def initialize_database():
    """
    Initialize database:
    1. Create database if it doesn't exist
    2. Create tables if they don't exist
    3. Seed data if tables are empty
    """
    print("\n" + "="*50)
    print("Database Initialization Starting...")
    print("="*50)
    
    # Step 1: Create database
    print("\n[1/3] Checking/Creating Database...")
    if not database_exists(settings.postgres_db):
        print(f"  Creating database '{settings.postgres_db}'...")
        if not create_database(settings.postgres_db):
            print("  [ERROR] Failed to create database")
            return False
    else:
        print(f"  [OK] Database '{settings.postgres_db}' already exists")
    
    # Step 2: Get SQL scripts
    scripts = get_sql_scripts()
    
    # Step 3: Create tables if needed
    print("\n[2/3] Checking/Creating Tables...")
    if "create_tables" in scripts:
        try:
            conn = psycopg2.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            cursor = conn.cursor()
            
            # Check if main table exists
            if table_exists(cursor, "users"):
                print("  [OK] Tables already exist")
            else:
                print("  Creating tables...")
                cursor.close()
                conn.close()
                if execute_sql_file(scripts["create_tables"]):
                    print("  [OK] Tables created successfully")
                else:
                    print("  [ERROR] Failed to create tables")
                    return False
            
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception as e:
            print(f"  [ERROR] Error checking tables: {e}")
            return False
    else:
        print("  [WARN] create-tables script not found at expected locations")
        print("    Searching in: backend/scripts/ or scripts/")
    
    # Step 4: Seed data if empty
    print("\n[3/3] Checking/Seeding Data...")
    if "seed_data" in scripts:
        try:
            if data_exists("users"):
                print("  [OK] Data already exists (seed skipped)")
            else:
                print("  Seeding initial data...")
                if execute_sql_file(scripts["seed_data"]):
                    print("  [OK] Data seeded successfully")
                else:
                    print("  [WARN] Seed had some issues, but continuing...")
        except Exception as e:
            print(f"  Error checking/seeding data: {e}")
    else:
        print("  [WARN] seed-data script not found at expected locations")
        print("    Searching in: backend/scripts/ or scripts/")
    
    print("\n" + "="*50)
    print("[OK] Database initialization complete!")
    print("="*50 + "\n")
    
    return True
