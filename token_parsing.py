import os
from dotenv import load_dotenv
from typing import Optional
from logger import logger


def get_bot_token(path : str) -> Optional[str]:
    load_dotenv(dotenv_path=path)
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error(f"Не получилось найти .env файл по пути {path}")
        return None
    else:
        return TOKEN