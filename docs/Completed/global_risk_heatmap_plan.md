# Plan: Global Risk Heatmap Implementation

This plan outlines the steps to implement a global risk heatmap on the dashboard page, displaying event counts aggregated by country for the last 90 days using Leaflet.js.

## 1. Backend Development (Flask/Python) [COMPLETED]

- **File:** `app/blueprints/dashboard/routes.py`
- **Action:** Define a new API endpoint `/api/global-risk-heatmap`.
- **Logic:**
  - Use `app.services.elasticsearch.base.ElasticsearchService`.
  - Construct an Elasticsearch aggregation query for the `events` index:
    - Filter by `event_date` or `timestamp` for the last 90 days.
    - Use a `terms` aggregation on the `country.keyword` field to get event counts. _(Note: Changed from `country` to `country.keyword` during implementation to fix fielddata error)_
  - Process results into a JSON object: `{"CountryName": count, ...}`.
    - _Note:_ Ensure country names are compatible with the chosen GeoJSON. Normalization might be needed.
  - Return the JSON response. Handle potential errors.

## 2. Frontend Development (HTML/JavaScript/Tailwind) [COMPLETED]

### 2.1 Base Template Modification [COMPLETED]

- **File:** `app/templates/base.html`
- **Action:** Add template blocks for page-specific assets:
  - Inside `<head>`: `{% block head_extra %}{% endblock %}`
  - Before `</body>`: `{% block scripts %}{% endblock %}`

### 2.2 Dashboard Template Modification [COMPLETED]

- **File:** `app/blueprints/dashboard/templates/dashboard/index.html`
- **Action:**
  - Locate the existing "Global Risk Heatmap" placeholder `div` (around line 19).
  - Add `id="global-risk-map"` to this `div`.
  - Use the new template blocks:
    - In `{% block head_extra %}`: Add Leaflet CSS CDN link.
    ```html
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
      crossorigin=""
    />
    ```
    - In `{% block scripts %}`:
      - Add Leaflet JS CDN link.
      ```html
      <script
        src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""
      ></script>
      ```
      - Add a script tag for the custom map logic.
      ```html
      <script src="{{ url_for('static', filename='js/dashboard_map.js') }}"></script>
      ```

### 2.3 Map JavaScript Implementation [COMPLETED]

- **File:** `app/static/js/dashboard_map.js` (Create this file)
- **Action:**
  - Add an event listener (e.g., `DOMContentLoaded`) to run the map code.
  - **Fetch API Data:** Use `fetch` to get data from `/dashboard/api/global-risk-heatmap`. _(Note: URL corrected to include blueprint prefix during implementation)_
  - **Fetch GeoJSON:** Use `fetch` to get country boundaries from `/static/data/world-countries.geojson` (or similar).
  - **Initialize Map:** Create a Leaflet map instance targeting `#global-risk-map`. _(Note: Added check to prevent re-initialization during implementation)_
  - **Create Choropleth Layer:**
    - Use `L.geoJSON` with the fetched GeoJSON data.
    - Define a `style` function:
      - Match GeoJSON country features with API data (using country name/code).
      - Set `fillColor` based on event count using a color scale (e.g., yellow to red).
      - Define default style for countries with no data.
    - Define `onEachFeature` function:
      - Bind a tooltip (`bindTooltip`) or popup (`bindPopup`) showing country name and event count.
  - **Add Legend:** Create a custom Leaflet control (`L.control`) to display the color scale legend.
  - **Error Handling:** Implement basic error handling for fetch requests.

### 2.4 GeoJSON Data [COMPLETED]

- **Action:** Obtain a suitable GeoJSON file containing world country boundaries (e.g., from Natural Earth, geojson.xyz).
- **Placement:** Save the file as `app/static/data/world-countries.geojson`.
  - _Note:_ Ensure the properties within the GeoJSON (e.g., `properties.name`, `properties.iso_a3`) are usable for matching against the API data.

## 3. Styling (Tailwind/CSS) [COMPLETED]

- **File:** `app/static/src/input.css` (or directly in HTML via Tailwind classes)
- **Action:**
  - Ensure the `#global-risk-map` container has appropriate height (e.g., `h-96` or similar). _(Note: Added inline `style="height: 384px;"` during implementation to resolve display issue)_
  - Style the map legend and tooltips/popups as needed using CSS or Tailwind within the JS.

## Summary of New/Modified Files:

- `app/blueprints/dashboard/routes.py` (Modified)
- `app/templates/base.html` (Modified)
- `app/blueprints/dashboard/templates/dashboard/index.html` (Modified)
- `app/static/js/dashboard_map.js` (New)
- `app/static/data/world-countries.geojson` (New)
- `docs/global_risk_heatmap_plan.md` (New)
