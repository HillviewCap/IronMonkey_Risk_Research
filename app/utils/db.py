import os
import psycopg2
from psycopg2 import pool
from urllib.parse import quote_plus, urlparse
from flask import current_app, has_app_context # Import Flask context helpers

_connection_pool = None


def get_db_connection():
    global _connection_pool
    # print("DEBUG: get_db_connection called.") # Removed debug

    if _connection_pool is None:
        # print("DEBUG: Connection pool is None, attempting initialization.") # Removed debug
        try:
            conn_string = None
            db_host_for_log = "Unknown"
            
            # Prioritize Flask app config if available (for testing)
            if has_app_context() and 'SQLALCHEMY_DATABASE_URI' in current_app.config:
                # print("DEBUG: Using SQLALCHEMY_DATABASE_URI from app config.") # Removed debug
                conn_string = current_app.config['SQLALCHEMY_DATABASE_URI']
                try:
                    parsed_uri = urlparse(conn_string)
                    db_host_for_log = parsed_uri.hostname or "Unknown"
                except Exception:
                    pass # Ignore parsing errors for logging
            else:
                # Fallback to environment variables
                # print("DEBUG: Using environment variables for DB connection.") # Removed debug
                required_vars = [
                    "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST",
                    "POSTGRES_PORT", "POSTGRES_DB"
                ]
                missing = [var for var in required_vars if not os.environ.get(var)]
                if missing:
                    raise RuntimeError(f"Missing database configuration: {', '.join(missing)}")

                encoded_password = quote_plus(os.environ["POSTGRES_PASSWORD"])
                db_host_for_log = os.environ['POSTGRES_HOST']
                conn_string = (
                    f"postgresql://{os.environ['POSTGRES_USER']}:{encoded_password}@"
                    f"{db_host_for_log}:{os.environ['POSTGRES_PORT']}/"
                    f"{os.environ['POSTGRES_DB']}"
                )

            if not conn_string:
                 raise RuntimeError("Could not determine database connection string.")

            print(f"Initializing connection pool to {db_host_for_log}")
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

    # Return connection from pool
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
