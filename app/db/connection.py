"""
Centralized database connection for CEDOP app.

Provides db_connect() function for all database operations.
"""
import os
from typing import Optional
import psycopg


def db_connect(schema: Optional[str] = None) -> psycopg.Connection:
    """
    Return a database connection using environment variables.

    Environment variables used:
        PGHOST: Database host (default: localhost)
        PGPORT: Database port (default: 5432)
        PGDATABASE: Database name (default: cedop)
        PGUSER: Database user
        PGPASSWORD: Database password

    Args:
        schema: If provided, sets search_path to this schema plus public.
                E.g., schema="cdop" sets search_path to "cdop, public".

    Returns:
        psycopg.Connection: An open database connection.

    Example:
        conn = db_connect()
        conn = db_connect(schema="cdop")
    """
    conn = psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "cedop"),
        user=os.environ.get("PGUSER"),
        password=os.environ.get("PGPASSWORD"),
    )
    if schema:
        conn.execute(f"SET search_path TO {schema}, public")
    return conn
