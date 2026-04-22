#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a PostgreSQL y el estado de la BD
Ejecutar desde: backend/
python scripts/test_db_connection.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from config.database_init import (
    database_exists,
    table_exists,
    data_exists,
    PostgresConnection
)
import psycopg2

def test_connection():
    """Test basic PostgreSQL connection"""
    print("\n" + "="*60)
    print("PRUEBA 1: Conexión a PostgreSQL")
    print("="*60)
    
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✓ Conexión exitosa!")
        print(f"  PostgreSQL: {version[0].split(',')[0]}")
        cursor.close()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"✗ Error de conexión: {e}")
        print(f"  Host: {settings.postgres_host}:{settings.postgres_port}")
        print(f"  Usuario: {settings.postgres_user}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False

def test_database():
    """Test database existence"""
    print("\n" + "="*60)
    print("PRUEBA 2: Base de Datos")
    print("="*60)
    
    if database_exists(settings.postgres_db):
        print(f"✓ Base de datos '{settings.postgres_db}' existe")
        return True
    else:
        print(f"✗ Base de datos '{settings.postgres_db}' NO existe")
        print("  Se creará automáticamente al iniciar el backend")
        return False

def test_tables():
    """Test table existence"""
    print("\n" + "="*60)
    print("PRUEBA 3: Tablas")
    print("="*60)
    
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        cursor = conn.cursor()
        
        # Check main tables
        tables_to_check = ["users", "modules", "exercises", "enrollments", "progress"]
        all_exist = True
        
        for table in tables_to_check:
            if table_exists(cursor, table):
                print(f"  ✓ Tabla '{table}' existe")
            else:
                print(f"  ✗ Tabla '{table}' NO existe")
                all_exist = False
        
        cursor.close()
        conn.close()
        
        if not all_exist:
            print("  → Las tablas se crearán automáticamente al iniciar el backend")
        
        return all_exist
    except psycopg2.OperationalError:
        print(f"✗ No se puede conectar a '{settings.postgres_db}' (BD no existe)")
        print("  → Se creará automáticamente al iniciar el backend")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_data():
    """Test data existence"""
    print("\n" + "="*60)
    print("PRUEBA 4: Datos (Seed)")
    print("="*60)
    
    try:
        if data_exists("users"):
            print("✓ Los datos se han cargado correctamente")
            
            # Show some stats
            conn = psycopg2.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"  Usuarios en BD: {user_count}")
            
            cursor.close()
            conn.close()
            return True
        else:
            print("✗ No hay datos (BD vacía)")
            print("  → Los datos se cargarán automáticamente al iniciar el backend")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "█"*60)
    print("VERIFICACIÓN DE BASE DE DATOS - Robolearn")
    print("█"*60)
    
    results = {
        "Conexión PostgreSQL": test_connection(),
        "Base de Datos": test_database(),
        "Tablas": test_tables(),
        "Datos": test_data(),
    }
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {test}")
    
    print(f"\nResultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n✓ ¡Todo está listo! Puedes iniciar el backend sin problemas.")
    elif passed == 0:
        print("\n✗ Asegúrate que PostgreSQL está corriendo e intenta de nuevo.")
    else:
        print("\n⚠ Algunos componentes no existen pero se crearán automáticamente al iniciar.")
    
    print("\nPara iniciar el backend:")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")
    
    print("\n" + "█"*60 + "\n")

if __name__ == "__main__":
    main()
