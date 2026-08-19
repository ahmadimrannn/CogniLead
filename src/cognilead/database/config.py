import os
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve PostgreSQL database connection URI from environment
DB_URI = os.getenv("DB_URI")

# Initialize PostgreSQL Connection Pool
pool = ConnectionPool(
  conninfo=DB_URI,
  max_size=10,
  max_idle=180,
  kwargs={
      "autocommit": True,
      "prepare_threshold": 0,
      "row_factory": dict_row,
  },
)

# Initialize LangGraph Postgres Checkpointer
checkpointer = PostgresSaver(pool, serde=JsonPlusSerializer())

# Automatically create necessary checkpoint tables in PostgreSQL if they do not exist
checkpointer.setup()

