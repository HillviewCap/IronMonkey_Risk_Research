# IronMonkey Risk Assessment Levels

This document outlines the different levels of risk assessment offered by the IronMonkey Risk Research Platform.

## 1. Basic Assessment

**Scope:** Provides a high-level, automated risk score primarily focused on readily available organizational data and associated vulnerabilities.

**Purpose:** Offers a quick snapshot of potential risk exposure based on fundamental factors. Suitable for initial client screening or periodic high-level checks.

**Methodology:**

*   **Inputs:**
    *   **Client Industry:** Used to determine a baseline risk score from pre-defined `IndustryProfile` data.
    *   **Client Geographic Footprint:** Considers the countries where the client has locations (`ClientLocation`). Locations in pre-defined high-risk countries contribute to the score.
    *   **Client Primary Assets:** Identifies assets marked with high criticality (e.g., `criticality_score >= 8`) that have valid identifiers (`asset_identifier` and `identifier_type`).
    *   **TIP Vulnerability Data:** Queries the Elasticsearch `tip_vulnerabilities` index for known vulnerabilities (Medium severity or higher) associated with the identified primary assets.

*   **Scoring Logic (Simplified Additive Approach):**
    1.  **Start** with the `baseline_risk` based on the client's industry (default 50 if no profile).
    2.  **Add** a `geo_contribution` based on the number of client locations in high-risk countries (max contribution: 20 points).
    3.  **Add** a `vuln_contribution` based on the number and severity (Crit/High weighted more) of vulnerabilities found for primary assets (max contribution: 40 points).
    4.  **Cap** the final score between 0 and 100.

*   **Output:**
    *   An overall risk score (0-100).
    *   Details including the baseline risk, geographic contribution factor, vulnerability contribution factor, number of primary assets checked, and counts of vulnerabilities found.

**Limitations:**
*   Does not include in-depth analysis of specific geopolitical conflicts or cyber actor capabilities beyond what's directly linked to asset vulnerabilities in the TIP.
*   Relies on the accuracy and completeness of client data (locations, assets, identifiers) and TIP vulnerability data.
*   Uses a simplified geographic risk model (list of high-risk countries).

## 2. Enhanced Protection (Full Framework Assessment)

*(Placeholder - To be defined)*

**Scope:** Comprehensive assessment utilizing the full Enhanced Geopolitical Cyber Risk Assessment Framework (v2.0). Involves detailed analysis across Conflict Analysis, Cyber Power Assessment, and Organizational Exposure, potentially including manual analysis and expert input.

**Methodology:** Uses configurable weights and potentially amplification factors based on `ScoringConfiguration` and findings across all framework categories.

## 3. Premium Defense

*(Placeholder - To be defined)*

**Scope:** Likely builds upon the Enhanced Protection level with additional services, deeper intelligence integration, continuous monitoring, or tailored mitigation strategies.