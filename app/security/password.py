import bcrypt


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt with low work factor for speed."""
    if not password:
        raise ValueError("Password cannot be empty.")

    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # rounds=8 سرعت بسیار بالایی دارد (حدود ۱۰ تا ۱۵ میلی‌ثانیه)
    salt = bcrypt.gensalt(rounds=8)
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plain-text password against its stored hash."""
    if not password or not password_hash:
        return False

    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False