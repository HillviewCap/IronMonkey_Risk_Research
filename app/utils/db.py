import os
import psycopg2
from psycopg2 import pool
from urllib.parse import quote_plus

_connection_pool = None


def get_db_connection():
    global _connection_pool

    if _connection_pool is None:
        try:
            required_vars = [
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_DB",
            ]
            missing = [var for var in required_vars if not os.environ.get(var)]
            if missing:
                raise RuntimeError(
                    f"Missing database configuration: {', '.join(missing)}"
                )

            # URL-encode password and construct connection string
            encoded_password = quote_plus(os.environ["POSTGRES_PASSWORD"])
            conn_string = (
                f"postgresql://{os.environ['POSTGRES_USER']}:{encoded_password}@"
                f"{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/"
                f"{os.environ['POSTGRES_DB']}"
            )

            print(f"Initializing connection pool to {os.environ['POSTGRES_HOST']}")
            _connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1, maxconn=20, dsn=conn_string
            )

            # Validate connection
            test_conn = _connection_pool.getconn()
            test_conn.cursor().execute("SELECT 1")
            _connection_pool.putconn(test_conn)
            print("Database connection validated successfully")

        except psycopg2.OperationalError as e:
            print(f"CRITICAL: Database connection failed - {str(e)}")
            raise
        except Exception as e:
            print(f"Configuration error: {str(e)}")
            raise

    return _connection_pool.getconn()


def release_db_connection(conn):
    if _connection_pool:
        _connection_pool.putconn(conn)


def close_all_connections():
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
    _connection_pool = None


def connection_healthcheck():
    try:
        conn = get_db_connection()
        conn.cursor().execute("SELECT 1")
        release_db_connection(conn)
        return True
    except Exception as e:
        print(f"Database health check failed: {str(e)}")
        return False
