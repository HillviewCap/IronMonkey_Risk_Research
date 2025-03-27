# Dashboard and Navigation Implementation Plan

## Goal

To implement a post-login dashboard page summarizing recent activity and add a top header navigation menu for accessing key application sections (Dashboard, Clients, Risk, Admin, Logout).

## Detailed Plan

**1. Create Dashboard Blueprint & Route:**

*   Create the directory structure:
    *   `app/blueprints/dashboard/`
    *   `app/blueprints/dashboard/templates/`
    *   `app/blueprints/dashboard/templates/dashboard/`
*   Create `app/blueprints/dashboard/__init__.py`: Define `dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')`.
*   Create `app/blueprints/dashboard/routes.py`:
    *   Import necessary modules (`Blueprint`, `render_template`, `login_required`, `url_for`).
    *   Define the blueprint instance (`dashboard_bp`).
    *   Create a route `@dashboard_bp.route('/')` decorated with `@login_required`.
    *   The route function `index()` will render `dashboard/index.html`.
*   Create `app/blueprints/dashboard/templates/dashboard/index.html`:
    *   Extend `base.html`.
    *   Include a title like `{% block title %}Dashboard - IronMonkey{% endblock %}`.
    *   Inside `{% block content %}`, add a heading (e.g., `<h1>Dashboard</h1>`) and placeholder sections for "Recent Activity Summary" (e.g., using `div`s with headings like "Recent Clients", "Open Risks").

**2. Register Dashboard Blueprint:**

*   Modify `app/__init__.py`:
    *   Add `from app.blueprints.dashboard import dashboard_bp`.
    *   Register the blueprint: `app.register_blueprint(dashboard_bp, url_prefix='/dashboard')`.

**3. Modify Base Template (`app/templates/base.html`):**

*   **Line 12:** Change `href="{{ url_for('client.dashboard') }}"` to `href="{{ url_for('dashboard.index') }}"`.
*   **Lines 14-16:** Replace the existing `nav` content inside the `{% if current_user.is_authenticated %}` block with the new navigation links, styled with Tailwind:
    ```html
    <nav>
        {% if current_user.is_authenticated %}
            <a href="{{ url_for('dashboard.index') }}" class="text-gray-600 hover:text-blue-600 ml-4">Dashboard</a>
            <a href="{{ url_for('client.client_list') }}" class="text-gray-600 hover:text-blue-600 ml-4">Clients</a>
            <a href="{{ url_for('risk.risk_list') }}" class="text-gray-600 hover:text-blue-600 ml-4">Risk</a>
            <a href="{{ url_for('admin.index') }}" class="text-gray-600 hover:text-blue-600 ml-4">Admin</a>
            <a href="{{ url_for('auth.logout') }}" class="text-gray-600 hover:text-blue-600 ml-4">Logout</a>
        {% else %}
            <a href="{{ url_for('auth.login') }}" class="text-gray-600 hover:text-blue-600">Login</a>
            <a href="{{ url_for('auth.register') }}" class="text-gray-600 hover:text-blue-600 ml-4">Register</a>
        {% endif %}
    </nav>
    ```
    *(Note: Assumes route names `client.client_list`, `risk.risk_list`, `admin.index`. These might need adjustment if the actual route names differ).*

**4. Adjust Routing and Redirects:**

*   **Modify `app/__init__.py` (lines 98-100):**
    *   Import `current_user` from `flask_login`.
    *   Change the `index()` function:
        ```python
        @app.route('/')
        def index():
            if current_user.is_authenticated:
                return redirect(url_for('dashboard.index'))
            return redirect(url_for('auth.login'))
        ```
*   **Modify `app/blueprints/auth/routes.py`:**
    *   **Line 42:** Change `redirect(url_for("client.dashboard"))` to `redirect(url_for("dashboard.index"))`.
    *   **Line 102:** Change `next_page = url_for("client.dashboard")` to `next_page = url_for("dashboard.index")`.
    *   **Line 141:** Change `redirect(url_for("client.dashboard"))` to `redirect(url_for("dashboard.index"))`.
    *   **Line 185:** Change `redirect(url_for("client.dashboard"))` to `redirect(url_for("dashboard.index"))`.
    *   **Line 195:** Change `redirect(url_for("client.dashboard"))` to `redirect(url_for("dashboard.index"))`.

## Visual Plan (Mermaid Diagram)

```mermaid
graph TD
    subgraph User Flow
        A[User Accesses Root /] --> B{Authenticated?};
        B -- Yes --> C[Redirect to /dashboard];
        B -- No --> D[Redirect to /auth/login];
        D --> E[Login Form];
        E -- Submit --> F{Authentication Successful?};
        F -- Yes --> C;
        F -- No --> E;
        C --> G[Render Dashboard View];
    end

    subgraph Implementation Steps
        H[1. Create Dashboard Blueprint (routes, template)] --> I[2. Register Blueprint in app/__init__.py];
        I --> J[3. Modify base.html: Add Header & Nav Menu];
        J --> K[4. Update Root Route & Login Redirects];
    end

    subgraph Components
        L[app/__init__.py]
        M[app/blueprints/dashboard/*]
        N[app/templates/base.html]
        O[app/blueprints/auth/routes.py]
    end

    H -.-> M;
    I -.-> L;
    J -.-> N;
    K -.-> L;
    K -.-> O;
    G -.-> N;
    G -.-> M;