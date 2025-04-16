# Phase 3 Completion Plan: Risk Assessment Engine Frontend & Testing

## 1. Overview

This plan outlines the remaining tasks required to complete Phase 3 of the IronMonkey Risk Research platform, focusing on implementing the interactive frontend components for the Risk Assessment Engine and ensuring comprehensive testing. This plan incorporates the project conventions defined in `docs/conventions.md`.

**Goal:** Deliver a functional and tested Risk Assessment Engine module, including interactive user interfaces for managing assessments, findings, and recommendations, and calculating risk scores based on the Enhanced Framework v2.0.

## 2. Frontend Implementation (Flask Templates + JavaScript)

**Status:** Partially Complete

**Goal:** Create interactive frontend components within `app/templates/risk/` using JavaScript (ES6+, Airbnb style guide) and Fetch API, styled with Tailwind CSS according to conventions.

**Tasks:**

- **Assessment List (`app/blueprints/risk/templates/risk/list.html`):**
  - ✅ Implement dynamic filtering (Client, Status, Type, Score Range, Framework Category) using JavaScript (Alpine.js).
  - ✅ AJAX calls use Fetch API and handle standard API JSON responses.
- **Assessment Detail (`app/blueprints/risk/templates/risk/detail.html`):**
  - ✅ Implement modals/forms for adding/editing Findings. Use Fetch API to POST data to the refactored `/api/v1/risk-assessments/{id}/findings` endpoint and PUT data to `/api/v1/findings/{id}` for editing. Handle standard JSON responses.
  - ✅ Implement modals/forms for adding/editing Recommendations. Use Fetch API to POST data to the refactored `/api/v1/findings/{id}/recommendations` endpoint and PUT data to `/api/v1/recommendations/{id}` for editing. Handle standard JSON responses.
  - ✅ Implement button/mechanism to trigger score calculation via POST to the refactored `/api/v1/risk-assessments/{id}/calculate-score` endpoint. Handle standard JSON responses.
  - ✅ Display calculated scores (`overall_score`, `framework_scores`) dynamically using Alpine.js without page reload.
  - ✅ Implement button/link to trigger report generation via GET to the refactored `/api/v1/risk-assessments/{id}/report` endpoint.
- **Assessment Create/Edit (`app/blueprints/risk/templates/risk/edit.html`):**
  - ✅ Ensure forms follow HTML/CSS conventions for structure and styling using Tailwind CSS.
  - ✅ Implement API interaction for editing via `PUT /api/v1/risk-assessments/{id}` using Alpine.js and Fetch API.
- **Code Style:** Ensure all new HTML/CSS/JS adheres to `docs/conventions.md`.

## 3. API Refactoring & Consistency

**Status:** Complete

**Goal:** Ensure API endpoints used by the frontend follow conventions for structure, naming (`/api/v1/...`), and responses (standard JSON).

**Tasks:**

- ✅ **Refactor Existing Endpoints:** Update routes in `app/blueprints/risk/routes.py` to use the `/api/v1/` prefix and consistent resource naming.
- ✅ **Implement Missing Endpoints:** Create necessary RESTful endpoints (GET list/detail, PUT update) following conventions.
- ✅ **Standardize Responses:** Ensure all API endpoints return the standard JSON structure (`status`, `data`/`error`, `meta`).
- ✅ **Backend Code Style:** Ensure backend Python code adheres to PEP 8, Black, Google docstrings, logging, and exception handling conventions. _(Helper function and new endpoints follow conventions)_.

## 4. Testing

**Status:** Pending

**Goal:** Ensure features work correctly and reliably, following testing conventions.

**Tasks:**

- **Unit Tests (`tests/risk/`):**
  - ⏳ Write tests for `ScoringService` covering various scenarios.
  - Follow naming convention: `test_thing_being_tested_condition`.
  - Use AAA pattern (Arrange, Act, Assert).
- **Integration Tests (`tests/api/` or `tests/risk/`):**
  - ✅ Test all refactored/new API endpoints with valid/invalid data, checking HTTP status codes and standard JSON responses.
  - ✅ Test web routes for rendering and form submission.
  - Follow naming convention.
  - Use AAA pattern.
- **End-to-End Tests (Manual or Automated):**
  - ⏳ Verify user workflows: Create assessment -> Add findings -> Add recommendations -> Calculate score -> Generate report.

## 5. Documentation Update

**Status:** Partially Complete

**Goal:** Reflect the final implementation status and decisions in project documentation, following conventions.

**Tasks:**

- ⏳ Update `docs/phase3_risk_assessment_plan.md` "Implementation Progress" section.
- ⏳ Ensure any new code has appropriate Google-style docstrings.
- ⏳ Update `CHANGELOG.md` upon completion.
- ✅ This plan document (`docs/phase3_completion_plan.md`) created and updated.

## 6. Diagrammatic Overview

```mermaid
graph TD
    subgraph Phase 3 Completion Plan (Convention Aligned)
        direction LR
        A[Frontend Implementation] --> B(API Refactoring & Consistency);
        A --> C(Testing);
        B --> C;
        C --> D(Documentation Update);

        subgraph A [Frontend (Flask Templates + JS)]
            style A fill:#ccffcc
            A1[✅ Assessment List Filters]
            A2[✅ Assessment Detail Modals (Finding/Rec - Add)]
            A3[✅ Score Calculation Trigger/Display]
            A4[✅ Report Generation Trigger]
            A5[✅ Assessment Detail Modals (Edit)]
            A6[✅ Assessment Edit Page API]
        end

        subgraph B [API Refactoring & Consistency]
            style B fill:#ccffcc
            B1[✅ Refactor API URLs to /api/v1/...]
            B2[✅ Implement Missing Endpoints (GET/PUT)]
            B3[✅ Ensure Standard JSON Responses]
            B4[✅ Ensure Python Conventions]
        end

        subgraph C [Testing]
             style C fill:#ffffcc
            C1[⏳ Unit Tests (ScoringService)]
            C2[⏳ Integration Tests (API/Routes)]
            C3[⏳ E2E Tests (Workflows)]
            C4[Ensure Test Conventions]
        end

         subgraph D [Documentation Update]
             style D fill:#ffffcc
             D1[⏳ Update phase3_risk_assessment_plan.md]
             D2[⏳ Ensure Docstrings]
             D3[⏳ Update CHANGELOG.md]
             D4[✅ Create phase3_completion_plan.md]
         end
    end
```

## 7. Current Status & Next Steps (As of March 27, 2025 ~15:35 UTC)

- **Completed:**
  - API endpoints refactored to `/api/v1/` structure.
  - Missing GET/PUT endpoints for assessments, findings, and recommendations added.
  - API responses standardized to JSON format (`status`, `data`/`error`, `meta`).
  - Frontend implementation completed:
    - Dynamic filtering in assessment list view.
    - Add/edit modals for Findings and Recommendations in detail view.
    - Dynamic score calculation and display without page reload.
    - Report generation functionality.
    - Assessment edit page converted to use API endpoints via Fetch.
    - All forms styled according to conventions using Tailwind CSS.
- **Next Steps:**
  - **Testing:** Begin implementation of Unit tests for `ScoringService` and Integration tests for the API endpoints as per Section 4.
  - **Documentation:** Update related documentation (`phase3_risk_assessment_plan.md`, docstrings, `CHANGELOG.md`).
