import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Find the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load database credentials
load_dotenv(PROJECT_ROOT / ".env")

def get_connection():

    connection = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    return connection