import bcrypt
import asyncio

ROUNDS = 12

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=ROUNDS)).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

async def verify_password_async(password: str, password_hash: str) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, verify_password, password, password_hash
    )
