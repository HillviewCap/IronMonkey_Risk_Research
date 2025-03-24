# IronMonkey Risk Research Coding and Documentation Conventions

This document outlines the coding, documentation, and design conventions for the IronMonkey Risk Research platform. Following these conventions ensures consistency, maintainability, and readability across the project.

## 1. Python Coding Conventions

### 1.1 Code Style

- Follow PEP 8 style guide for all Python code
- Use Black code formatter with default settings
- Maximum line length: 88 characters (Black default)
- Use 4 spaces for indentation (no tabs)
- Use snake_case for function and variable names
- Use CamelCase for class names
- Use UPPER_CASE for constants

### 1.2 Imports

- Group imports in the following order, separated by a blank line:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Alphabetize imports within each group
- Use absolute imports rather than relative imports

Example:
```python
# Standard library imports
import json
import os
from datetime import datetime, timedelta

# Third-party imports
from flask import Blueprint, render_template, request
from sqlalchemy import Column, Integer, String

# Local application imports
from app.models.user import User
from app.services.elasticsearch import ElasticsearchService
```

### 1.3 Docstrings

- Use Google-style docstrings for functions, classes, and modules
- All public functions, classes, and methods should have docstrings
- Include parameter types and return types

Example:
```python
def get_client_risk_profile(client_id: int, assessment_date: datetime = None) -> dict:
    """
    Retrieve a client's risk profile.
    
    Args:
        client_id: The ID of the client
        assessment_date: Optional date to retrieve historical profile
    
    Returns:
        A dictionary containing the risk profile data
        
    Raises:
        ValueError: If client_id is invalid
    """
    # Function implementation
```

### 1.4 Exception Handling

- Be specific with exception types, avoid bare `except:` clauses
- Always include meaningful error messages
- Use logging instead of print statements
- Chain exceptions with `raise ... from ...` when re-raising

Example:
```python
try:
    client = get_client(client_id)
except DatabaseError as e:
    logger.error(f"Database error retrieving client {client_id}: {str(e)}")
    raise ClientRetrievalError(f"Could not retrieve client {client_id}") from e
```

## 2. Database Conventions

### 2.1 Table Naming

- Use plural nouns for table names (e.g., `users`, `clients`)
- Prefix tables with their schema name (e.g., `clients.organizations`)
- Use snake_case for table names
- For junction tables, combine both entity names (e.g., `user_roles`)

### 2.2 Column Naming

- Use snake_case for column names
- Use descriptive names that indicate the purpose of the column
- For foreign keys, use `entity_id` format (e.g., `client_id`)
- Include standard columns in all tables:
  - `id`: Primary key
  - `created_at`: Creation timestamp
  - `updated_at`: Last update timestamp

### 2.3 Database Schema

- Use PostgreSQL schemas to organize tables by domain:
  - `clients`: Client-related tables
  - `users`: User and authentication tables
  - `risk`: Risk assessment tables
  - `app`: Application configuration tables

### 2.4 Indexes

- Create indexes for columns frequently used in WHERE clauses
- Always index foreign key columns
- Use composite indexes for columns frequently queried together
- Name indexes consistently using format: `idx_tablename_columnname`

## 3. HTML/CSS Conventions

### 3.1 Tailwind CSS Usage

- Use Tailwind utility classes directly in HTML elements
- For repeated component styles, use `@apply` in CSS or extract to components
- Follow mobile-first approach for responsive design
- Maintain consistent spacing and sizing values
- Organize Tailwind classes in the following order:
  1. Layout (display, position, width, height)
  2. Typography (font, text)
  3. Spacing (margin, padding)
  4. Appearance (colors, background, borders)
  5. Interactive states (hover, focus)

Example:
```html
<button class="
  block w-full         <!-- Layout -->
  text-sm font-medium  <!-- Typography -->
  py-2 px-4            <!-- Spacing -->
  bg-blue-600 text-white rounded-md <!-- Appearance -->
  hover:bg-blue-700 focus:outline-none focus:ring-2 <!-- States -->
">
  Submit
</button>
```

### 3.2 Template Organization

- Store templates in blueprint-specific directories
- Use Jinja2 template inheritance with a base layout
- Keep template logic minimal, prefer moving logic to view functions
- Use consistent naming for template blocks

### 3.3 Form Styling

- Use consistent form field styling throughout the application
- Include proper label, input, and error message structure
- Always provide accessible label elements
- Use appropriate input types and validation attributes

## 4. JavaScript Conventions

### 4.1 Code Style

- Use ES6+ syntax
- Follow Airbnb JavaScript Style Guide
- Use camelCase for variables and functions
- Use PascalCase for classes
- Use semicolons at the end of statements

### 4.2 DOM Interaction

- Prefer dataset attributes for data storage over custom attributes
- Use event delegation for dynamic elements
- Use descriptive class names for JavaScript hooks
- Minimize direct DOM manipulation

### 4.3 AJAX Requests

- Use Fetch API for AJAX requests
- Always handle error states
- Provide loading states for better user experience
- Use Promise chains or async/await consistently

## 5. Blueprint Organization

### 5.1 Structure

Each blueprint should follow this structure:
```
/blueprint_name/
  __init__.py       # Blueprint definition
  routes.py         # Route handlers
  forms.py          # Form definitions (if needed)
  /templates/
    /blueprint_name/ # Blueprint-specific templates
```

### 5.2 Naming Conventions

- Blueprint variable names should end with `_bp` (e.g., `auth_bp`)
- Route function names should be descriptive of the action and resource
- Group related endpoints with consistent prefixes

Example:
```python
# Good route naming
@client_bp.route('/clients')
def client_list():
    # ...

@client_bp.route('/clients/<int:client_id>')
def client_detail(client_id):
    # ...

@client_bp.route('/clients/<int:client_id>/edit')
def client_edit(client_id):
    # ...
```

## 6. API Conventions

### 6.1 Endpoint Structure

- Use RESTful resource naming in plural form
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Include API version in the URL path (e.g., `/api/v1/clients`)
- Use kebab-case for URL paths (e.g., `/api/v1/risk-assessments`)

### 6.2 Response Format

- Use consistent JSON structure for all API responses
- Include status, data, and metadata in responses
- Use appropriate HTTP status codes
- Return descriptive error messages

Example response:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Example Client",
    "industry": "Technology"
  },
  "meta": {
    "timestamp": "2025-03-23T14:35:42Z"
  }
}
```

### 6.3 Error Handling

- Return appropriate HTTP status codes for errors
- Include error code, message, and details in error responses
- Use consistent error format across all API endpoints

Example error response:
```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested client was not found",
    "details": "Client ID 123 does not exist"
  },
  "meta": {
    "timestamp": "2025-03-23T14:35:42Z"
  }
}
```

## 7. Documentation Conventions

### 7.1 Code Documentation

- Document all functions, classes, and modules
- Focus documentation on "why" and "how", not just "what"
- Keep docstrings up to date with code changes
- Include examples for complex functions

### 7.2 Markdown Style

- Use ATX-style headers (`#` for headers, not underlines)
- Use ordered lists for sequential items
- Use unordered lists for non-sequential items
- Include table of contents for longer documents
- Use backticks for inline code and code blocks
- Use appropriate heading levels (don't skip levels)

### 7.3 API Documentation

- Document all API endpoints
- Include parameters, request body, and responses
- Provide example requests and responses
- Use consistent formatting for all endpoint documentation

### 7.4 Changelog

- Maintain a CHANGELOG.md file
- Follow the [Keep a Changelog](https://keepachangelog.com/) format
- Group changes by type (Added, Changed, Fixed, Removed)
- Link version numbers to git tags or releases

## 8. Git Workflow

### 8.1 Branch Naming

- Feature branches: `feature/short-description`
- Bug fix branches: `fix/issue-description`
- Release branches: `release/version-number`
- Hotfix branches: `hotfix/issue-description`

### 8.2 Commit Messages

- Write descriptive commit messages
- Use the imperative mood in commit messages (e.g., "Add feature" not "Added feature")
- Reference issue numbers where applicable
- Follow this format:
  ```
  [Component] Short summary (50 chars or less)

  More detailed explanatory text, if necessary.
  ```

### 8.3 Pull Requests

- Create descriptive pull request titles
- Include detailed description of changes
- Link to relevant issues
- Ensure all tests pass before merging
- Require code review before merging

## 9. Testing Conventions

### 9.1 Test Organization

- Organize tests to mirror the application structure
- Name test files with `test_` prefix
- Group tests by feature or class
- Write both unit and integration tests

### 9.2 Test Naming

- Test function names should be descriptive of what they test
- Follow the pattern `test_thing_being_tested_condition`
- Make test names readable as sentences

Example:
```python
def test_user_authentication_with_valid_credentials():
    # ...

def test_user_authentication_with_invalid_password():
    # ...
```

### 9.3 Test Structure

- Use AAA pattern (Arrange, Act, Assert)
- Keep tests independent and isolated
- Use fixtures for common setup
- Write clear assertion messages

## 10. Logging Conventions

### 10.1 Log Levels

- ERROR: System errors, exceptions, and failures
- WARNING: Notable events that may indicate problems
- INFO: General operational information
- DEBUG: Detailed information for debugging purposes

### 10.2 Log Format

- Include timestamp, log level, module, and message
- For errors, include stack traces where appropriate
- Include relevant context (e.g., user ID, request ID)
- Format JSON logs for machine readability

### 10.3 Log Message Style

- Write clear, descriptive messages
- Include relevant variable values
- Use consistent message format
- Avoid logging sensitive information
