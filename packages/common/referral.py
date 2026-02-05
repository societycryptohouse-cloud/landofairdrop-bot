import hashlib


def make_ref_code(telegram_user_id: int) -> str:
    h = hashlib.sha256(str(telegram_user_id).encode()).hexdigest()
    return h[:8]
