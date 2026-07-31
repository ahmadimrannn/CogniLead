import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

DB_URI = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost:5432/lead_db")

def get_db_connection():
    return psycopg.connect(DB_URI, row_factory=dict_row)