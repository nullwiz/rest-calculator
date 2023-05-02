import re
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    hashed_password = generate_password_hash(password)
    return hashed_password


def check_password(password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, password)


def is_password_valid(password: str) -> bool:
    # Password requirements:
    # - At least 8 characters
    # - At least one digit
    # - At least one special character
    if len(password) < 8:
        return False

    if not re.search(r'\d', password):
        return False

    if not re.search(r'[@$!%*?&]', password):
        return False

    return True
