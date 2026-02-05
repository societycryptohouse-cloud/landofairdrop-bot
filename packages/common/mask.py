def mask_wallet(addr: str, left: int = 4, right: int = 4) -> str:
    addr = (addr or "").strip()
    if len(addr) <= left + right + 3:
        return addr
    return f"{addr[:left]}...{addr[-right:]}"
