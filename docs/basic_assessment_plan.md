# Plan: Implement Basic Risk Assessment

**Goal:** Create the functionality for performing a "Basic Assessment" which calculates a high-level risk score based on client industry, geographic footprint, and known vulnerabilities associated with their primary assets using TIP data from Elasticsearch.

**Phase:** Part of Platform Plan Phase 3: Risk Assessment.

**Assumptions:**
*   TIP data, including vulnerabilities associated with assets (e.g., by IP, hostname, software name/version), exists in dedicated Elasticsearch indices.
*   Client data (industry, locations, assets with criticality) is available in the PostgreSQL database via SQLAlchemy models (`Client`, `ClientLocation`, `ClientAsset`).
*   `IndustryProfile` model contains baseline risk scores per industry.
*   A mechanism exists or can be easily added to identify a client's "primary assets" (e.g., using `ClientAsset.criticality_score >= threshold`).

**Steps:**

1.  **Define TIP Vulnerability Index Structure:** Identify ES index name/structure for vulnerabilities and asset linkage.
2.  **Create/Enhance Elasticsearch Service for TIP Queries:** Implement methods in a new/existing service (`app/services/elasticsearch/tip_service.py` or base) to query the vulnerability index based on asset identifiers.
3.  **Define "Primary Asset" Identification:** Determine criteria (e.g., `ClientAsset.criticality_score >= 8`).
4.  **Update Scoring Service (`scoring_service.py`):** Modify `calculate_assessment_score` to handle 'Basic' assessment type, retrieve client/industry data, query ES for vulnerabilities via the new TIP service methods, calculate geographic risk, combine factors into a score, and store results.
5.  **Update Database Models & Configuration:** Add 'Basic' to `Assessment.assessment_type` options and potentially update `ScoringConfiguration`.
6.  **Update UI/Routes (`risk/routes.py`, `risk/forms.py`, `risk/templates/`):** Add 'Basic' option to forms/templates and ensure details page can display Basic Assessment results.
7.  **Documentation:** Create content for `docs/risk-assessment-levels.md` defining the Basic Assessment.
8.  **Testing:** Write unit and integration tests for the new ES queries, scoring logic, and end-to-end flow.

**Diagram:**

```mermaid
graph TD
    subgraph Define & Prepare
        A[1. Define TIP Vuln Index Structure] --> B(2. Create/Enhance ES TIP Service);
        C[3. Define Primary Asset Criteria] --> D(4. Update Scoring Service);
    end

    subgraph Implementation
        B --> D;
        E[5. Update DB Models/Config] --> D;
        E --> F[6. Update UI/Routes];
        D --> F;
    end

    subgraph Finalize
        G[7. Document in risk-assessment-levels.md]
        H[8. Implement Tests]
        F --> G;
        F --> H;
    end

    style Define & Prepare fill:#f9f,stroke:#333,stroke-width:2px
    style Implementation fill:#ccf,stroke:#333,stroke-width:2px
    style Finalize fill:#cfc,stroke:#333,stroke-width:2px