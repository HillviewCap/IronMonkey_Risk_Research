import os
import psycopg2
from psycopg2 import pool

_connection_pool = None

def get_db_connection():
    """
    Returns a database connection from the connection pool.
    Creates the pool if it doesn't exist.
    Prioritizes DATABASE_URL environment variable if set.
    """
    global _connection_pool

    if _connection_pool is None:
        try:
            db_url = os.environ.get('DATABASE_URL')
            if db_url:
                _connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 20, db_url
                )
            else:
                _connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 20,
                    user=os.environ.get('POSTGRES_USER'),
                    password=os.environ.get('POSTGRES_PASSWORD'),
                    host=os.environ.get('POSTGRES_HOST'),
                    port=os.environ.get('POSTGRES_PORT'),
                    database=os.environ.get('POSTGRES_DB')
                )
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
            raise

    return _connection_pool.getconn()

def release_db_connection(conn):
    """
    Releases a database connection back to the connection pool.
    """
    if _connection_pool:
      _connection_pool.putconn(conn)

def close_all_connections():
    """Closes all connections in the pool"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
    _connection_pool = None