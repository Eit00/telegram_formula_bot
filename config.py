# Конфиг проекта
import os


BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOTFATHER_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./raffle.db")


# Доступ к простой админке (примитивная защита через секрет; можно заменить на auth)
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "change-me")