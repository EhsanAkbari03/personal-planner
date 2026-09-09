import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")


if not DATABASE_URL:
    raise ValueError(
        "POSTGRES_URL not found in env file. "
    )


def get_db():
    return psycopg.connect(DATABASE_URL)