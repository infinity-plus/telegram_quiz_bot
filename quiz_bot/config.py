#!/usr/bin/python3

from os import environ


class Config:
    api: str = environ.get("api", "None")
    sheet1: str = environ.get("sheet1", "None")
    sheet2: str = environ.get("sheet2", "None")
    heroku: str = environ.get("heroku", "None")
    PORT: int = int(environ.get('PORT', 5000))
