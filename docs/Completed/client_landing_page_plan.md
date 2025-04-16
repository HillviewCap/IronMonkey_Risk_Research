# Client Landing Page Implementation Plan

## 1. Goal

Create a new landing page at `/clients` that lists all clients and provides a quick link to the onboarding form (`/clients/onboard`). Update the main navigation menu to point the "Clients" link to this new page instead of the client search page (`/clients/search`).

## 2. Plan Steps

1.  **Backend Implementation (`app/blueprints/client/routes.py`):**
    *   Define a new route: `@client_bp.route('/clients', methods=['GET'])`.
    *   Create a view function named `client_landing`.
    *   Inside `client_landing`:
        *   Import the `Client` model: `from app.models.client import Client`.
        *   Query the database to retrieve all clients, ordered by name: `clients = Client.query.order_by(Client.name).all()`.
        *   Render a new template `client/landing.html`, passing the `clients` list to it.

2.  **Frontend Implementation (New Template: `app/templates/client/landing.html`):**
    *   Create the file `app/templates/client/landing.html`.
    *   Make it inherit from the base template (`{% extends 'base.html' %}`).
    *   Set the title block (`{% block title %}Client Landing{% endblock %}`).
    *   In the content block (`{% block content %}`):
        *   Add a heading (e.g., `<h1>Client Landing</h1>`).
        *   Add a prominent button styled with Tailwind CSS linking to the onboarding page: `<a href="{{ url_for('client.onboard_client') }}" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Onboard New Client</a>`. (Adjust styling based on `docs/conventions.md` and existing styles).
        *   Add a section/table to display the list of clients retrieved in the view function.
        *   Iterate through the `clients` list (`{% for client in clients %}`).
        *   For each client, display their name and potentially other key info (like industry).
        *   Make each client's name a link to their detail page: `<a href="{{ url_for('client.client_detail', client_id=client.id) }}">{{ client.name }}</a>`.
        *   Apply appropriate Tailwind CSS for layout and styling (e.g., using a table or styled list).

3.  **Navigation Update (`app/templates/base.html`):**
    *   Open the `app/templates/base.html` file.
    *   Locate the navigation item that currently links to the client search page (`/clients/search` or likely `url_for('client.client_search')`). It might look something like `<a href="{{ url_for('client.client_search') }}">Client Search</a>`.
    *   Change the `href` attribute to point to the new landing page view function: `href="{{ url_for('client.client_landing') }}"`.
    *   Update the link text from "Client Search" to "Clients": `<a>Clients</a>`.

## 3. Workflow Diagram

```mermaid
graph TD
    A[User Clicks "Clients" in Nav Menu] --> B{Request GET /clients};
    B --> C[client_landing View Function];
    C --> D[Query DB: Get All Clients];
    D --> E[Render client/landing.html Template];
    E --> F[Display Landing Page];
    F -- Contains --> G["Onboard New Client" Button (Links to /clients/onboard)];
    F -- Contains --> H[List of Clients (Names link to /clients/<id>)];

    I[User Clicks "Onboard New Client"] --> J{Request GET /clients/onboard};
    K[User Clicks a Client Name] --> L{Request GET /clients/<id>};

    style C fill:#ccf,stroke:#333,stroke-width:2px
    style E fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#cfc,stroke:#333,stroke-width:2px