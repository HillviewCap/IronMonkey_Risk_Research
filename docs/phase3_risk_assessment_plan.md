# Phase 3: Risk Assessment Engine Implementation Plan (Updated: March 26, 2025)

## 1. Overview & Goals

This phase focuses on building the core engine for conducting, managing, and reporting on geopolitical and cyber risk assessments within the IronMonkey platform.

**Goals:**

*   Implement structured workflows for creating and managing risk assessments, aligned with the Enhanced Geopolitical Cyber Risk Assessment Framework (v2.0).
*   Develop flexible scoring models based explicitly on the framework's methodology.
*   Enable detailed tracking and management of identified findings within the framework's context.
*   Provide a system for generating and tracking mitigation recommendations derived from framework-based risks.
*   Integrate assessment data with reporting capabilities, reflecting the framework structure.
*   Utilize Elasticsearch for efficient querying and analysis of assessment data.

## 2. Assessment Workflows

*   **Requirements:**
    *   Ability to create new assessments linked to specific clients.
    *   Define assessment types/templates reflecting framework scope (e.g., Full Framework Assessment, Targeted Conflict Assessment, Ad-hoc).
    *   Capture structured data related to framework phases: Conflict Analysis, Cyber Power Assessment, Organizational Exposure.
    *   Track assessment status (Draft, In Progress, Review, Completed).
    *   Assign assessments to analysts.
    *   Link assessments to relevant geopolitical events or cyber threats (Phase 4 dependency).
*   **Database:**
    *   Utilize `risk.assessments` table (defined in `system_architecture.md`).
    *   Add columns for `assessment_type`, `status`, `assigned_user_id`, `client_id`.
*   **API Endpoints (`/api/v1/assessments`):**
    *   `POST /`: Create new assessment.
    *   `GET /`: List assessments (with filters for client, status, user).
    *   `GET /{id}`: Retrieve assessment details.
    *   `PUT /{id}`: Update assessment metadata (status, assignee).
*   **Services:**
    *   `AssessmentService`: Logic for managing assessment lifecycle.
*   **Frontend:**
    *   Assessment dashboard/list view.
    *   Form for creating/editing assessments.
    *   Detailed assessment view page.
*   **Testing:** Unit tests for service logic, integration tests for API endpoints.

## 3. Finding Management

*   **Requirements:**
    *   Ability to add findings to a specific assessment.
    *   Categorize findings based on framework elements (e.g., Geopolitical Conflict, Cyber Actor Type, Org Exposure Type) and potentially framework attack types (Destruction, Disruption, Intelligence, Influence).
    *   Assign severity/risk level (e.g., Low, Medium, High, Critical).
    *   Describe the finding, its impact, and affected assets, linking back to specific framework data points where possible (e.g., specific conflict, actor, business relationship).
    *   Track finding status (Open, Mitigating, Resolved, Accepted).
*   **Database:**
    *   Utilize `risk.findings` table.
    *   Ensure columns for `assessment_id`, `category`, `severity`, `description`, `impact`, `status`.
    *   Consider a join table for linking findings to specific `client.assets`.
*   **API Endpoints (`/api/v1/assessments/{assessment_id}/findings`):**
    *   `POST /`: Add a finding to an assessment.
    *   `GET /`: List findings for an assessment.
    *   `GET /{finding_id}`: Retrieve finding details.
    *   `PUT /{finding_id}`: Update finding details/status.
*   **Services:**
    *   `FindingService`: Logic for managing findings.
*   **Frontend:**
    *   Section within the assessment detail view to list/add/edit findings.
*   **Elasticsearch:**
    *   Findings data will be nested within the `risk_assessments` index (as shown in `system_architecture.md`). Ensure mapping supports filtering/aggregation by category, severity, status.
*   **Testing:** Unit tests for service logic, integration tests for API, Elasticsearch indexing verification.

## 4. Recommendation System

*   **Requirements:**
    *   Ability to add recommendations linked to specific findings.
    *   Describe the recommended action.
    *   Assign priority (e.g., Low, Medium, High).
    *   Track implementation status (Not Started, In Progress, Completed, Rejected).
    *   Assign responsibility (optional).
*   **Database:**
    *   Utilize `risk.recommendations` table.
    *   Ensure columns for `finding_id`, `description`, `priority`, `status`, `assigned_user_id` (optional).
*   **API Endpoints (`/api/v1/findings/{finding_id}/recommendations`):**
    *   `POST /`: Add a recommendation to a finding.
    *   `GET /`: List recommendations for a finding.
    *   `GET /{recommendation_id}`: Retrieve recommendation details.
    *   `PUT /{recommendation_id}`: Update recommendation details/status.
*   **Services:**
    *   `RecommendationService`: Logic for managing recommendations.
*   **Frontend:**
    *   Section within the finding detail view (or assessment view) to list/add/edit recommendations.
*   **Elasticsearch:**
    *   Recommendation data nested within findings in the `risk_assessments` index.
*   **Testing:** Unit tests for service logic, integration tests for API.

## 5. Scoring Models (Based on Enhanced Framework v2.0)

*   **Core Principle:** Risk scoring will be derived from the intersection of the framework's core components: Geopolitical Conflict/Tensions, Cyber Power Capabilities, and Organizational Connection, adjusted by Industry Profiles, Connection Analysis, and Amplification Factors.

*   **Requirements:**
    *   Implement scoring logic reflecting the framework's methodology (Intersection, Amplification).
    *   Capture necessary framework data points associated with each assessment.
    *   Allow configuration of scoring weights, thresholds, and amplification factors (potentially via admin interface or config files).
    *   Calculate risk scores at multiple levels (e.g., Overall Assessment, Specific Conflict Scenario, Finding Level).
    *   Store calculated scores and potentially the contributing factor values for transparency.

*   **Data Model (Database/Input):**
    *   **Assessment Linkage:** Assessments (`risk.assessments`) need mechanisms to link to specific Conflicts, Cyber Actors/Capabilities, and Organizational Exposure data points relevant to the assessment scope.
    *   **Framework Data Storage (Potential New Tables/Schemas or reliance on Phase 4):**
        *   `intelligence.conflicts`: Store details on geopolitical conflicts (ID, Name, Type, Intensity, Phase, Involved Actors). (Likely Phase 4)
        *   `intelligence.cyber_actors`: Store details on state/non-state actors (ID, Name, Type [GOV, APT, etc.], Capabilities, Sophistication, Historical Activity). (Likely Phase 4)
        *   `intelligence.attack_patterns`: Store details on common TTPs, potentially linked to actors. (Likely Phase 4)
    *   **Organizational Data (Leverage `client` schema):**
        *   `clients.organizations`: Industry.
        *   `clients.locations`: Physical presence (Country, City, Proximity to conflict zones).
        *   `clients.assets`: Criticality, Type, Location, Infrastructure Dependencies.
        *   `clients.relationships`: Business network connections (Suppliers, Partners).
        *   Need mechanism to capture Public Profile/Stance if relevant.
    *   **Framework Configuration Tables:**
        *   `risk.industry_profiles`: Store baseline risk levels/vulnerabilities per industry (Critical, High-Impact, Support).
        *   `risk.connection_types`: Define direct, indirect, reputational connection types and their potential impact.
        *   `risk.amplification_factors`: Store primary (Intensity, Proximity, Sector, Stance) and secondary factors (Infra Dependency, Supply Chain, Data Sensitivity, Regulatory) with associated weighting or impact rules.
    *   **Score Storage:**
        *   Add `risk_score` (overall) and potentially `framework_scores` (JSONB containing component scores) to `risk.assessments`.
        *   Consider adding score contributions to `risk.findings`.

*   **Scoring Logic (High-Level):**
    *   For a given assessment scope (e.g., Client X vs. Conflict Y):
        1.  Identify relevant Conflict characteristics (Intensity, etc.).
        2.  Identify relevant Cyber Actor capabilities (Sophistication, Intent).
        3.  Identify relevant Organizational Exposure points (Physical Presence, Business Links, Digital Footprint, Public Stance).
        4.  Determine baseline risk based on Client's Industry Profile.
        5.  Evaluate Connection Type (Direct, Indirect, Reputational) between Org Exposure and Conflict/Actor.
        6.  Apply Amplification Factors based on context (Proximity, Stance, Dependencies, etc.).
        7.  Calculate final score based on a configurable algorithm (e.g., weighted sum, matrix lookup, rule engine) combining these inputs.

*   **API Endpoints:**
    *   `POST /api/v1/assessments/{id}/calculate-score`: Trigger score calculation based on associated framework data.
    *   Assessment GET endpoints (`/api/v1/assessments/{id}`) should return calculated scores.

*   **Services:**
    *   `ScoringService`: Major refactoring required. Needs functions to:
        *   Fetch relevant framework data by utilizing existing backend services that query Elasticsearch (e.g., for ACLED events/actors, MITRE techniques based on `docs/backend-elastic-cli.md`).
        *   Fetch relevant client/asset data (from DB/Client services).
        *   Apply configured scoring rules/weights/matrices based on the framework.
        *   Persist calculated scores.
    *   Potential need for a `FrameworkConfigService` to manage scoring configurations.

*   **Frontend:**
    *   Display calculated scores clearly on assessment views.
    *   Consider visualizing contributing factors or score breakdown for transparency (e.g., showing high impact from Proximity + High-Intensity Conflict).
    *   Admin interface for managing scoring configurations (optional).

*   **Elasticsearch:**
    *   Index calculated scores (overall and potentially component scores).
    *   Index key framework factors associated with the assessment (e.g., Conflict ID, Primary Actor Type, Industry, Connection Type) to enable powerful filtering and aggregation (e.g., "Show all assessments with High Direct Connection to Conflict Z").

*   **Testing:**
    *   Extensive unit tests validating scoring logic against various framework scenarios and configurations.
    *   Integration tests verifying score calculation endpoints and data persistence.
    *   Validation of Elasticsearch indexing for framework factors and scores.

## 6. Report Generation Integration

*   **Requirements:**
    *   Generate summary reports for completed assessments, structured according to the Enhanced Framework v2.0 methodology.
    *   Include assessment details, framework phase data (Conflict, Cyber Power, Org Exposure), findings, recommendations, and calculated scores based on the framework.
    *   Allow basic customization/filtering for reports.
*   **Database:**
    *   Leverage existing risk schema data and newly added framework-related fields.
*   **API Endpoints:**
    *   `GET /api/v1/assessments/{id}/report`: Generate/download report for an assessment.
*   **Services:**
    *   Utilize/extend the existing `Report Generation` service (`app/services/reports/`).
    *   Create report templates reflecting the framework structure (e.g., sections for each framework phase, connection analysis, amplification).
*   **Frontend:**
    *   Button/link on assessment view to generate/download report.
*   **Testing:** Integration tests for report generation endpoint, validation of report content against framework structure.

## 7. Dependencies

*   **Client Management (Phase 2):** Requires comprehensive and accurate client details, asset information (criticality, location, type), and potentially relationship data (suppliers, partners) to feed into the framework's Organizational Exposure and Connection Analysis sections.
*   **Existing Elasticsearch Intelligence Data:** The platform already has indexed data for ACLED events/actors, MITRE techniques, and general threat content, accessible via backend services (as evidenced by `docs/backend-elastic-cli.md`). Phase 3 will leverage this existing data for the Conflict Analysis and Cyber Power Assessment components of the framework.
*   **Intelligence Feed (Phase 4):** While basic intelligence data exists, Phase 4 will likely focus on enhancing the feed (e.g., adding new sources, improving correlation, real-time processing, advanced analytics) which will further improve scoring accuracy and depth. Full scoring potential still depends on robust integration, but Phase 3 is not blocked on initial data availability.

## 8. Architecture Diagram (Simplified Workflow)

```mermaid
graph TD
    subgraph Client Management
        ClientData[Client/Asset Data]
    end

    subgraph Risk Assessment Engine (Phase 3)
        A[Create Assessment] --> B(Add Findings);
        B --> C{Assign Severity/Category};
        C --> D[Add Recommendations];
        D --> E{Assign Priority/Status};
        C --> F[Calculate Risk Score];
        F --> G[Store Score];
        A & B & D & G --> H(Generate Report);
    end

    subgraph Intelligence Feed (Phase 4)
        IntelData[Threat/Event Data]
    end

    ClientData --> A;
    ClientData --> C;
    ClientData --> F;
    IntelData -.-> C;  // Optional/Future Link
    IntelData -.-> F;  // Optional/Future Link
    H --> Output[Assessment Report PDF/HTML];

    style ClientData fill:#f9f,stroke:#333,stroke-width:2px;
    style IntelData fill:#ccf,stroke:#333,stroke-width:2px;
```

## 9. Timeline & Sprints (Example based on 8 weeks)

*   **Weeks 9-10:** Assessment Workflow foundation (DB, API, Basic UI).
*   **Weeks 11-12:** Finding Management (DB, API, UI Integration, ES Indexing).
*   **Weeks 13-14:** Recommendation System (DB, API, UI Integration).
*   **Weeks 15-16:** Scoring Models & Report Integration (Services, Calculation Logic, Report Templates).

## 10. Success Metrics

*   Ability to create, manage, and complete an assessment workflow.
*   Accurate tracking of findings and recommendations with status updates.
*   Successful calculation and storage of risk scores based on defined models.
*   Generation of coherent assessment summary reports.
*   Code coverage for new services and API endpoints.

## 11. Implementation Progress

### Completed Items

*   **Database Models**:
    *   ✅ Created framework configuration models (`IndustryProfile`, `ConnectionType`, `AmplificationFactor`, `ScoringConfiguration`)
    *   ✅ Updated existing models (`Assessment`, `Finding`, `Recommendation`) with framework-specific fields
    *   ✅ Created and applied migration script to update the database schema

*   **Scoring Logic**:
    *   ✅ Implemented `ScoringService` that calculates risk scores based on the framework's methodology
    *   ✅ Incorporated the three core components: Conflict Analysis, Cyber Power Assessment, and Organizational Exposure
    *   ✅ Added support for amplification factors and connection types

*   **API Endpoints**:
    *   ✅ Added endpoints for calculating risk scores
    *   ✅ Added endpoints for managing findings with framework-specific categorization
    *   ✅ Added endpoints for managing recommendations linked to findings

*   **Elasticsearch Integration**:
    *   ✅ Updated `RiskSearchService` to include framework-specific fields in indexed documents
    *   ✅ Added support for searching and filtering by framework categories

*   **Sample Data**:
    *   ✅ Created script to initialize framework configuration data
    *   ✅ Added industry profiles, connection types, amplification factors, and scoring configurations

### Pending Items

*   **Frontend Components**:
    *   ⏳ Assessment dashboard/list view with framework-specific filters
    *   ⏳ Assessment detail view with framework scores visualization
    *   ⏳ Finding management interface with framework categorization
    *   ⏳ Recommendation management interface

*   **Report Generation**:
    *   ⏳ Report templates reflecting the framework structure
    *   ⏳ PDF/HTML report generation functionality

*   **Testing**:
    *   ⏳ Unit tests for scoring algorithms
    *   ⏳ Integration tests for API endpoints
    *   ⏳ End-to-end tests for assessment workflows