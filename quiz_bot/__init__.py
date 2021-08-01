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
PORT: int = int(environ.get('PORT', 5000))
