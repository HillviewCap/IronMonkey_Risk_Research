# Client Onboarding Workflow Implementation Plan

## 1. Overview

This document outlines the plan for implementing a client onboarding workflow within the IronMonkey Risk Research platform. The goal is to create a user-friendly form to capture essential client information based on the Enhanced Geopolitical Cyber Risk Assessment Framework and integrate it with the existing backend infrastructure.

## 2. Data Requirements

The onboarding form will capture the following information:

*   **Organization Details (`Client` model):**
    *   `name`: (Required) Organization's legal name.
    *   `industry`: (Required) Select from a predefined list based on framework categories (Critical, High-Impact, Support).
    *   `website`: (Optional) Company website URL.
    *   `description`: (Optional) Brief description of the organization.
    *   `public_profile_summary`: (Optional, New Field) Text area to capture initial notes on public stance/profile.
*   **Primary Contact (`ClientContact` model):**
    *   `first_name`: (Required)
    *   `last_name`: (Required)
    *   `email`: (Required)
    *   `phone`: (Optional)
    *   `position`: (Optional)
    *   (This contact will be marked as `is_primary=True`).
*   **Primary Location (`ClientLocation` model):**
    *   `name`: (Required, Default: "Headquarters")
    *   `address`: (Optional)
    *   `city`: (Optional)
    *   `state`: (Optional)
    *   `country`: (Required) Select from a list.
    *   `postal_code`: (Optional)
    *   (This location will be marked as `location_type="HQ"`).

## 3. Onboarding Workflow

1.  User navigates to `/clients/onboard`.
2.  A single-page form is rendered with sections for Organization, Contact, and Location.
3.  User fills and submits the form (POST request).
4.  Backend validates the submitted data.
5.  **If valid:**
    *   `ClientService` creates `Client`, `ClientContact`, and `ClientLocation` records.
    *   Database transaction is committed.
    *   User is redirected to the new client's detail page (e.g., `/clients/<client_id>`).
6.  **If invalid:**
    *   The onboarding form is re-rendered with validation errors displayed.

## 4. Backend Implementation

*   **Models (`app/models/client.py`):**
    *   Add `public_profile_summary = db.Column(db.Text)` to the `Client` model.
    *   Generate and apply a database migration.
*   **Forms (`app/blueprints/client/forms.py` - New File):**
    *   Create `ClientOnboardingForm(FlaskForm)` with fields matching data requirements.
    *   Implement appropriate validators (e.g., `DataRequired`, `Email`, `URL`, `Length`).
    *   Use `SelectField` for `industry` and `country`, populating choices appropriately.
*   **Routes (`app/blueprints/client/routes.py`):**
    *   Add route `@client_bp.route('/clients/onboard', methods=['GET', 'POST'])`.
    *   Handle `GET` request: Instantiate form, render `client/onboard_client.html`.
    *   Handle `POST` request: Instantiate form with `request.form`, validate. If valid, call service function and redirect. If invalid, re-render template with form.
*   **Services (`app/services/client_service.py`):**
    *   Add function `create_client_with_details(form_data)`:
        *   Accepts validated form data.
        *   Creates `Client`, `ClientContact` (with `is_primary=True`), and `ClientLocation` (with `location_type="HQ"`) instances.
        *   Adds instances to the `db.session` and commits.
        *   Includes error handling (e.g., `try...except` block for DB operations).
        *   Returns the created `Client` object.

## 5. Frontend Implementation

*   **Templates (`app/templates/client/onboard_client.html` - New File):**
    *   Create a Jinja2 template inheriting from `base.html` (or equivalent).
    *   Use WTForms macros or manual rendering to display the `ClientOnboardingForm`.
    *   Structure the form using `<fieldset>` or `<div>` sections for Organization, Contact, and Location.
    *   Apply Tailwind CSS classes for styling according to `docs/conventions.md`.
    *   Ensure proper display of validation errors.
    *   Include a submit button.

## 6. Workflow Diagram

```mermaid
graph LR
    A[User Navigates to /clients/onboard] --> B{Render Onboarding Form};
    B --> C[User Fills Form];
    C --> D{User Submits Form (POST)};
    D --> E{Backend Validates Data};
    E -- Invalid --> B;
    E -- Valid --> F[Service Creates Client, Contact, Location];
    F --> G[Database Commit];
    G --> H[Redirect to Client Detail Page];

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#ccf,stroke:#333,stroke-width:2px
    style H fill:#cfc,stroke:#333,stroke-width:2px