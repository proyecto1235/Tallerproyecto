import psycopg2
from config.settings import settings

def fix_passwords():
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db
    )
    cursor = conn.cursor()
    
    # New valid hashes
    updates = [
        ('admin@robolearn.com', '$2b$12$bGM8zs/InGnD1y8CjoqEgOdxJFEhAjfib2/jZckpnA3p0mhd/fpiW'),
        ('teacher@robolearn.com', '$2b$12$JFpw/eFD6s9cDikL1TJsYeExzr.85GpQUS1rvEqnEvJVJ4w/ZMOsC'),
        ('student1@robolearn.com', '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i'),
        ('student2@robolearn.com', '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i'),
        ('student3@robolearn.com', '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i')
    ]
    
    for email, pwd_hash in updates:
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (pwd_hash, email)
        )
        print(f"Updated {email}")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_passwords()
