# Elasticsearch Data Reference Plan

## 1. Introduction

This document outlines the plan for creating a reference guide for developers using the data indexed in Elasticsearch. The guide will detail the structure and source of data within the following indices:

- `events`
- `actors`
- `techniques`
- `threat_content`

## 2. Index Details

### `events` Index

- **Source:** ACLED (Armed Conflict Location & Event Data Project) data.
- **Description:** Contains information about individual conflict events.
- **Fields (Based on `utils/acled/models.py::ACLEDEvent`):**
  - `event_id_cnty` (String): Unique event identifier.
  - `event_date` (Date): Date of the event.
  - `year` (Integer): Year of the event.
  - `event_type` (String): Type of event (e.g., 'Battles', 'Protests').
  - `sub_event_type` (String): Sub-type of the event.
  - `disorder_type` (String, Optional): Type of disorder.
  - `actor1` (String): Primary actor involved.
  - `actor2` (String, Optional): Secondary actor involved.
  - `region` (Integer/String): Region ID or name.
  - `country` (String): Country name.
  - `admin1` (String): First-level administrative division.
  - `admin2` (String, Optional): Second-level administrative division.
  - `location` (String): Specific location name.
  - `latitude` (Float): Latitude coordinate.
  - `longitude` (Float): Longitude coordinate.
  - `geo_precision` (Integer): Precision of geo-coordinates (1-3).
  - `source` (String): Source of event information.
  - `fatalities` (Integer): Number of reported fatalities.
  - `interaction_type` (Integer, Optional): Type of interaction between actors.
  - `timestamp` (Date): Original timestamp from ACLED data.
- **Transformations/Added Fields (by `utils/elastic_indexer.py::index_events`):**
  - `location` (Geo-point): Created from `latitude` and `longitude` (e.g., `{"lat": float, "lon": float}`).
  - `timestamp` (Date): Overwritten/added at indexing time (UTC).

### `actors` Index

- **Source:** ACLED data.
- **Description:** Contains information about actors involved in events.
- **Fields (Based on `utils/acled/models.py::ACLEDActor`):**
  - `actor_id` (Integer, Optional): Database ID for the actor.
  - `actor_name` (String): Name of the actor.
  - `actor_type` (String): Type of actor.
  - `actor_type_id` (Integer, Optional): ID of the actor type.
  - `first_event_date` (Date, Optional): Date of the first recorded event involving the actor.
  - `last_event_date` (Date, Optional): Date of the most recent event involving the actor.
  - `regions` (List[Integer]): List of region IDs where the actor is active.
  - `countries` (List[String]): List of country names where the actor is active.
  - `event_count` (Integer): Total number of events involving the actor.
- **Added Fields (by `utils/elastic_indexer.py::index_actors`):**
  - `last_updated` (Date): Timestamp added at indexing time (UTC).

### `techniques` Index

- **Source:** MITRE ATT&CK STIX data.
- **Description:** Contains information about adversary tactics and techniques.
- **Fields (Inferred from `utils/mitre_loader.py` and `utils/elastic_search.py`):**
  - `stix_id` (String): STIX unique identifier.
  - `technique_id` (String): MITRE ATT&CK technique ID (e.g., 'T1548').
  - `name` (String): Name of the technique.
  - `description` (String): Description of the technique.
  - `detection` (String): Guidance on detecting the technique (from `x_mitre_detection`).
  - `platforms` (List[String]): Applicable platforms (from `x_mitre_platforms`).
  - `permissions_required` (List[String]): Permissions needed to execute the technique (from `x_mitre_permissions_required`).
  - `tactic` / `tactics` (List[String]): Associated MITRE ATT&CK tactics (from `x_mitre_tactics`). _Field name might vary._
  - `spec_version` (String): STIX specification version.
  - `created_timestamp` (Date): Original creation timestamp from STIX data.
  - `modified_timestamp` (Date): Original modification timestamp from STIX data.
  - `domain` (String): MITRE ATT&CK domain (e.g., 'enterprise-attack', 'ics-attack').
  - _Note:_ The exact field names and structure are inferred as the direct indexing code path was not explicitly found in the reviewed files (`cli/mitre_init.py` only loads to PG/Mongo). The structure indexed is likely the dictionary passed to `index_techniques`.
- **Added Fields (by `utils/elastic_indexer.py::index_techniques`):**
  - `last_updated` (Date): Timestamp added at indexing time (UTC).

### `threat_content` Index

- **Source:** MongoDB collection `threats_db.parsed_content`.
- **Description:** Contains parsed content from various threat intelligence feeds.
- **Fields (Defined in `utils/elastic_indexer.py::index_threat_content`):**
  - `id` (String): Original MongoDB document `_id`.
  - `content` (String): Main content/body.
  - `title` (String): Title of the content.
  - `description` (String): Description or abstract.
  - `creator` (String): Author or creator information.
  - `feed_title` (String): Title of the source feed.
  - `pub_date` (Date): Publication date.
  - `created_at` (Date): Timestamp when the record was created in MongoDB.
  - `summary` (String): Summary of the content.
  - `url` (String): Primary URL associated with the content.
  - `processed` (Boolean): Flag indicating if the content has been processed.
  - `urls` (List[String]): List of URLs found within the content.
  - `emails` (List[String]): List of email addresses found within the content.
  - `last_analyzed` (Date): Timestamp of the last analysis performed.
  - `critical_infrastructure_sectors` (List[Object]): List of identified critical infrastructure sectors (e.g., `{'sector': 'string', 'confidence': float}`).
  - `identified_threat_actors` (List[Object]): List of identified threat actors (e.g., `{'name': 'string', 'uuid': 'string', 'confidence': float}`).
  - `identified_tools` (List[Object]): List of identified tools (e.g., `{'name': 'string', 'uuid': 'string', 'confidence': float}`).
  - `last_classified` (Date): Timestamp of the last classification performed.
  - `sentiment_score` (Float): Calculated sentiment score of the content.
- **Added Fields (by `utils/elastic_indexer.py::index_threat_content`):**
  - `timestamp` (Date): Timestamp added at indexing time (UTC).

## 3. Formatting

The final reference document will be created in Markdown format, using appropriate headings, lists, and code blocks for clarity.
