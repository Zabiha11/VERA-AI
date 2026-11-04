import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    DEBUG = False
    TESTING = False