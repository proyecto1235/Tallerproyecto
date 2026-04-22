from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_verify():
    password = "admin123"
    # The hash I just put in the DB
    pwd_hash = "$2b$12$bGM8zs/InGnD1y8CjoqEgOdxJFEhAjfib2/jZckpnA3p0mhd/fpiW"
    
    try:
        result = pwd_context.verify(password, pwd_hash)
        print(f"Verification result: {result}")
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_verify()
