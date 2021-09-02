from os import environ
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"),
              logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

TOKEN: str = environ.get("TOKEN", "None")
SHEET1: str = environ.get("SHEET1", "None")
SHEET2: str = environ.get("SHEET2", "None")
HEROKU: str = environ.get("HEROKU", "None")
OWNER: int = int(environ.get("OWNER", 0))
PORT: int = int(environ.get('PORT', 5000))
DB_URI: str = environ.get("DATABASE_URL", "None")
if DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)
