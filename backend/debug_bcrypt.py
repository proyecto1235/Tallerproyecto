import bcrypt

def test_verify():
    password = "admin123"
    pwd_hash = "$2b$12$bGM8zs/InGnD1y8CjoqEgOdxJFEhAjfib2/jZckpnA3p0mhd/fpiW"

    try:
        result = bcrypt.checkpw(password.encode("utf-8"), pwd_hash.encode("utf-8"))
        print(f"Verification result: {result}")
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_verify()
