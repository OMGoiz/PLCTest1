from datetime import datetime


def today_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d")
