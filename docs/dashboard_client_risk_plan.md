# Dashboard Client Risk Overview Implementation Plan

## Goal

To replace the static placeholder data in the "Client Risk Overview" section of the dashboard (`app/blueprints/dashboard/templates/dashboard/index.html`) with dynamic data fetched from the database, showing the top 5 clients with the highest risk scores based on their latest completed assessments.

## Detailed Plan

**1. Define Risk Thresholds & Styling (in `app/blueprints/dashboard/routes.py`)**

*   Establish numerical score ranges and corresponding Tailwind CSS classes:
    *   **High:** 70 - 100 (`text-red-600`)
    *   **Medium:** 40 - 69 (`text-yellow-600`)
    *   **Low:** 0 - 39 (`text-green-600`)

**2. Update Dashboard Route (`app/blueprints/dashboard/routes.py` - `index` function)**

*   **Remove Placeholder:** Delete the static `clients` list.
*   **Import Models/Functions:** Ensure `Client`, `Assessment`, `db` (from `app`), and `desc` (from `sqlalchemy`) are imported.
*   **Fetch Data:**
    *   Implement a SQLAlchemy query to retrieve the top 5 clients and their *most recent completed* assessment.
    *   Join `Client` and `Assessment` tables.
    *   Filter assessments by `status == 'complete'`.
    *   Identify the latest assessment per client (e.g., using a subquery or window function).
    *   Order results by `Assessment.risk_score` descending.
    *   Limit results to 5.
*   **Process Data:**
    *   Iterate through the query results.
    *   For each client/assessment pair, determine the `risk_level` string ("High", "Medium", "Low") and the corresponding `risk_class` based on `assessment.risk_score` and the defined thresholds.
    *   Create a list of dictionaries, each containing: `id`, `name`, `risk_score` (rounded), `risk_level`, `risk_class`, `industry`, `last_assessment_date` (formatted string).
*   **Pass to Template:** Pass the created list of dictionaries to `render_template` as the `clients` variable.

**3. Update Dashboard Template (`app/blueprints/dashboard/templates/dashboard/index.html`)**

*   **Replace Static Rows:** Remove the hardcoded `<tr>...</tr>` elements within the `<tbody>` of the "Client Risk Overview" table.
*   **Add Jinja Loop:** Insert a `{% for client in clients %}` loop around a single `<tr>` structure.
*   **Display Dynamic Data:** Use Jinja expressions (`{{ client.name }}`, etc.) to display data from the `client` dictionary.
*   **Apply Dynamic Styling:** Apply the dynamic CSS class to the risk score table cell: `<td class="... {{ client.risk_class }}">`.
*   **Update Action Links:** Modify `href` attributes:
    *   View: `href="{{ url_for('client.view_client', client_id=client.id) }}"`
    *   Assess: `href="{{ url_for('risk.new_assessment', client_id=client.id) }}"`

## Visual Plan (Mermaid Diagram)

```mermaid
graph TD
    subgraph Data Flow & Processing
        A[DB: clients_organizations] --> F;
        B[DB: risk_assessments] --> F;
        F[routes.py: index()] -- Query --> G{Get Top 5 Clients + Latest Completed Assessment};
        H[Risk Thresholds (0-39, 40-69, 70-100) & CSS Classes (green, yellow, red)] --> I;
        G -- Assessment Data --> I{Determine Risk Level & Class};
        I -- Processed Data --> J[Create `clients` list (dictionaries)];
        J --> K[Pass `clients` to Template];
    end

    subgraph Template Rendering
        L[index.html] --> M{Receive `clients` list};
        M --> N[Loop `{% for client in clients %}`];
        N --> O[Display `client.name`, `client.risk_level`, etc.];
        O --> P[Apply `client.risk_class` to TD];
        P --> Q[Generate Action Links `url_for('client.view_client', client_id=client.id)`, `url_for('risk.new_assessment', client_id=client.id)`];
    end

    K --> L;