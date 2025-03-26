# Test Database Setup Plan

This document outlines the plan for configuring dedicated test databases for PostgreSQL and Redis, using connection details from the existing `.env` file.

## Observations

1.  **`.env` File:** Contains connection details for PostgreSQL (`DATABASE_URL`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`) and Redis (`REDIS_URL`, `REDIS_PASSWORD`).
2.  **`config.py`:**
    *   Reads database credentials from environment variables (set by `.env`).
    *   Constructs `SQLALCHEMY_DATABASE_URI` and `REDIS_URL` using these variables for the base `Config`.
    *   Includes a `TestingConfig` class.
    *   Currently, `TestingConfig` hardcodes a different PostgreSQL URI and defaults to the main application's Redis database.

## Confirmed Plan

1.  **Modify `config.py` (`TestingConfig` class):**
    *   **PostgreSQL:** Update `SQLALCHEMY_DATABASE_URI` to use host, port, user, and password from environment variables, but specify the database name `geopolitical_risk_test`.
    *   **Redis:** Add a `REDIS_URL` attribute. This URL will use host, port, and password from environment variables but specify Redis database number `1`.

2.  **Update Test Setup (`tests/conftest.py`):**
    *   Implement Pytest fixtures to automatically:
        *   Create the PostgreSQL test database (`geopolitical_risk_test`) before the test suite runs.
        *   Drop the PostgreSQL test database after the test suite finishes.
        *   Flush the Redis test database (`1`) before each test or the entire suite runs.

## Diagram

```mermaid
graph TD
    A[Load .env Variables] --> B{Read Config};
    B -- FLASK_ENV=testing --> C[Use TestingConfig];
    B -- else --> D[Use Development/Production Config];

    C --> E[Construct Test SQLALCHEMY_DATABASE_URI];
    C --> F[Construct Test REDIS_URL];

    E -- Uses --> G[env: PG_HOST, PG_PORT, PG_USER, PG_PASSWORD];
    E -- Specifies --> H[DB Name: geopolitical_risk_test];

    F -- Uses --> I[env: REDIS_HOST, REDIS_PORT, REDIS_PASSWORD];
    F -- Specifies --> J[Redis DB Number: 1];

    K[tests/conftest.py Fixtures] --> L[Create/Drop PG Test DB];
    K --> M[Flush Redis Test DB];

    subgraph Configuration
        A; B; C; D; E; F; G; H; I; J;
    end

    subgraph Test Execution
        K; L; M;
    end