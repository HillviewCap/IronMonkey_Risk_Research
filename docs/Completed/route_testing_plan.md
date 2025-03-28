# Flask Route Testing Plan

**Goal:** Create a comprehensive test suite for the Flask application's routes using `pytest` to ensure they function correctly, handle authentication, and respond as expected.

**Testing Strategy:**

*   **Framework:** `pytest` with `pytest-flask` and `pytest-cov`.
*   **Database:** Use a dedicated test database (connection string via `TEST_DATABASE_URI`). Database schema will be created before tests and cleaned up after.
*   **External Services:** Connect to development instances of Redis and Elasticsearch (using existing configurations).
*   **Test Data:** Generate test data dynamically using fixtures and libraries like Faker, supplemented by specific predefined data where necessary.
*   **Coverage:** Aim for equal test coverage across all blueprints, measured using `pytest-cov`.

**Plan Details:**

1.  **Setup Test Environment:**
    *   Create `tests/` directory at the project root.
    *   Create subdirectories mirroring `app/blueprints/` inside `tests/` (`auth/`, `client/`, `risk/`, `admin/`, `api/`, `dashboard/`, `root/`).
    *   Create `tests/conftest.py` for shared fixtures.
    *   *(Optional)* Create `pytest.ini` for `pytest` configuration.

2.  **Core Fixtures (`tests/conftest.py`):**
    *   **`app` fixture:** Creates a Flask app instance configured for testing (`TESTING=True`), using the test database connection and development Redis/Elasticsearch connections.
    *   **`client` fixture:** Provides a Flask test client derived from the `app` fixture.
    *   **`runner` fixture:** Provides a Flask CLI test runner.
    *   **Database Fixtures:** Manage the test database lifecycle (connection, schema creation/deletion, test isolation via transactions or truncation).
    *   **Authentication Fixtures:** Helper fixtures to simulate logged-in users (standard, admin) using the test database and test client.
    *   **Test Data Fixtures:** Fixtures to generate or provide necessary data (users, clients, assessments) in the test database.

3.  **Test Implementation Strategy:**
    *   **Structure:** Place test files within the corresponding blueprint subdirectories in `tests/` (e.g., `tests/auth/test_routes.py`).
    *   **Focus:** Tests should verify:
        *   Correct HTTP status codes (200, 302, 404, 401, 403, 400, etc.).
        *   Redirection targets (`Location` header).
        *   Content rendering (basic checks for key elements/text).
        *   API response structure and data (for JSON endpoints).
        *   Authentication and authorization enforcement (`@login_required`, admin checks).
        *   Handling of valid and invalid input/form data.
        *   Flash messages.
        *   Interactions with the test database and development external services.

4.  **Test Coverage Outline (Equal Priority):**
    *   **Root (`/`):** Test redirection for authenticated/unauthenticated users.
    *   **Auth (`/auth`):** Test login, logout, registration, password reset placeholders, favicon, session debug.
    *   **Client (`/clients`):** Test search page rendering, API search endpoint.
    *   **Risk (`/risk`):** Test dashboard, assessment CRUD, intelligence/scenario placeholders, API endpoints (scoring, findings, recommendations, reports).
    *   **Admin (`/admin`):** Test dashboard, user management placeholders, logs placeholder, settings.
    *   **API (`/api`):** Test placeholder endpoints for clients, assessments, intelligence, dashboard data.
    *   **Dashboard (`/dashboard`):** Test index page rendering.

**Test Structure Visualization:**

```mermaid
graph TD
    A[tests/] --> B(conftest.py);
    A --> C(auth/);
    A --> D(client/);
    A --> E(risk/);
    A --> F(admin/);
    A --> G(api/);
    A --> H(dashboard/);
    A --> I(root/);

    C --> C1(test_routes.py);
    D --> D1(test_routes.py);
    D --> D2(test_api.py);
    E --> E1(test_routes.py);
    E --> E2(test_api.py);
    F --> F1(test_routes.py);
    G --> G1(test_api.py);
    H --> H1(test_routes.py);
    I --> I1(test_root.py);

    subgraph Fixtures [conftest.py]
        B1(app - Test DB, Dev Redis/ES)
        B2(client)
        B3(runner)
        B4(db_setup_teardown - Test DB)
        B5(auth_helpers - Test DB)
        B6(test_data_generators - Test DB)
    end

    style Fixtures fill:#f9f,stroke:#333,stroke-width:2px