# Client Search Implementation Plan

This document outlines the plan for implementing the client search functionality within the IronMonkey Risk Research platform.

## 1. Requirements

- **Searchable fields:** Client Name, Industry, Location (City and Country)
- **Partial matching:** Supported (case-insensitive)
- **Filtering:** By Industry and Country

## 2. Database Considerations

### 2.1 Tables and Columns

The following tables and columns will be used for the search functionality:

- `clients.organizations`:
  - `name`
  - `industry`
- `clients.locations`:
  - `city`
  - `country`

### 2.2 Indexes

Ensure the following indexes exist:

- `clients.organizations.name`
- `clients.organizations.industry`
- `clients.locations.city`
- `clients.locations.country`

If any of these indexes are missing, they should be created.

### 2.3 Query

A `JOIN` query between `clients.organizations` and `clients.locations` will be used to combine search criteria. The `ILIKE` operator will be used for case-insensitive partial matching.

## 3. API Design

### 3.1 Endpoint

A new RESTful endpoint will be created:

- `GET /api/v1/clients/search`

### 3.2 Request Parameters

The following request parameters will be supported:

- `query`: (string, optional) The search term. This will be used to search across client name, industry, and city.
- `industry`: (string, optional) Filter results by industry.
- `country`: (string, optional) Filter results by country.

### 3.3 Response Format

The API will return a JSON response in the following format:

```json
{
  "status": "success",
  "data": [
    {
      "id": 123,
      "name": "IronMonkey Risk Research",
      "industry": "Technology",
      "locations": [
        {
          "city": "New York",
          "country": "USA"
        }
      ]
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "per_page": 10
  }
}
```

## 4. Frontend Design

### 4.1 Search Input

A single input field will be provided for the main search query (`query` parameter).

### 4.2 Filters

Dropdown menus will be used for filtering:

- Industry dropdown
- Country dropdown

### 4.3 Results Display

Search results will be displayed in a table with the following columns:

- Client Name
- Industry
- Locations (City, Country)

## 5. Implementation

### 5.1 Blueprint

The functionality will be implemented within the `Client` blueprint (`app/blueprints/client/`).

### 5.2 Routes

A new route will be added to `app/blueprints/client/routes.py` to handle the `/api/v1/clients/search` endpoint.

### 5.3 Service

A new service function (e.g., `search_clients`) will be created, likely within `app/services/client_service.py` or a similar appropriate location. This function will handle the database query and data processing.

### 5.4 Templates

A new template may be created in `app/templates/client/`, or an existing template may be modified to display the search interface and results.

## 6. Testing

### 6.1 Unit Tests

Unit tests will be written to cover the search service function (`search_clients`).

### 6.2 Integration Tests

Integration tests will be written to verify the functionality of the API endpoint (`/api/v1/clients/search`).

### 6.3 End-to-End Tests

End-to-end tests will be written to cover the complete search workflow, from the frontend interface to the database and back.
