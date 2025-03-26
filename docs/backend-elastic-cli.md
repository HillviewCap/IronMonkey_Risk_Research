# Elasticsearch CLI Commands

This document outlines the available CLI commands for interacting with the Elasticsearch search and analytics functionality.

## Search Commands

### Search Events

Search for ACLED events with various filters.

```bash
python -m cli.elastic_search events [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -s, --start-date TEXT   Start date (YYYY-MM-DD)
  -e, --end-date TEXT     End date (YYYY-MM-DD)
  -l, --location TEXT     Location search (lat,lon,distance) e.g. "33.5,36.3,10km"
  --size INTEGER          Number of results to return (default: 10)
  -f, --format [table|json]  Output format (default: table)
```

### Search Actors

Search for ACLED actors by name and type.

```bash
python -m cli.elastic_search actors [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -t, --actor-type TEXT   Actor type filter
  --size INTEGER          Number of results to return (default: 10)
  -f, --format [table|json]  Output format (default: table)
```

### Search Techniques

Search for MITRE ATT&CK techniques.

```bash
python -m cli.elastic_search techniques [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -t, --tactic TEXT       MITRE tactic filter
  -p, --platform TEXT     Target platform filter
  --size INTEGER          Number of results to return (default: 10)
  -f, --format [table|json]  Output format (default: table)
```

### Search Threat Content

Search through threat intelligence content.

```bash
python -m cli.elastic_search threat-content [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -c, --creator TEXT      Filter by content creator
  -f, --feed TEXT        Filter by feed title
  -s, --start-date TEXT   Start date (YYYY-MM-DD)
  -e, --end-date TEXT     End date (YYYY-MM-DD)
  --size INTEGER          Number of results to return (default: 10)
  --format [table|json]   Output format (default: table)

Examples:
# Search for specific threat content
python -m cli.elastic_search threat-content -q "ransomware"

# Filter by creator and date range
python -m cli.elastic_search threat-content -c "ThreatPost" -s 2023-01-01 -e 2023-12-31

# Search specific feed with JSON output
python -m cli.elastic_search threat-content -f "SecurityWeek" --format json
```

## Statistics Commands

### Event Statistics

Get aggregated statistics for events.

```bash
python -m cli.elastic_search event-stats [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -s, --start-date TEXT   Start date (YYYY-MM-DD)
  -e, --end-date TEXT     End date (YYYY-MM-DD)
  -t, --type [time|event_type|location|actors]  Type of aggregation (default: event_type)
  --interval TEXT         Time interval for time-based aggregation (e.g. 1d, 1w, 1M)
  -f, --format [table|json]  Output format (default: table)

Examples:
# Get event type distribution
python -m cli.elastic_search event-stats -t event_type

# Get time-based trends by week
python -m cli.elastic_search event-stats -t time --interval 1w

# Get geographic distribution
python -m cli.elastic_search event-stats -t location

# Get actor type involvement
python -m cli.elastic_search event-stats -t actors
```

### Actor Statistics

Get aggregated statistics for actors.

```bash
python -m cli.elastic_search actor-stats [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -t, --type [type]       Type of aggregation (default: type)
  -f, --format [table|json]  Output format (default: table)

Examples:
# Get actor type distribution
python -m cli.elastic_search actor-stats

# Get JSON output
python -m cli.elastic_search actor-stats --format json
```

### Technique Statistics

Get aggregated statistics for MITRE techniques.

```bash
python -m cli.elastic_search technique-stats [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -t, --type [tactic|platform]  Type of aggregation (default: tactic)
  -f, --format [table|json]  Output format (default: table)

Examples:
# Get tactic distribution
python -m cli.elastic_search technique-stats -t tactic

# Get platform distribution
python -m cli.elastic_search technique-stats -t platform
```

### Threat Content Statistics

Get aggregated statistics for threat content.

```bash
python -m cli.elastic_search threat-stats [OPTIONS]

Options:
  -q, --query TEXT        Search query string
  -t, --type [creator|feed|time]  Type of aggregation (default: feed)
  --interval TEXT         Time interval for time-based aggregation (e.g. 1d, 1w, 1M)
  --format [table|json]   Output format (default: table)

Examples:
# Get distribution by creator
python -m cli.elastic_search threat-stats -t creator

# Get time-based trends by day
python -m cli.elastic_search threat-stats -t time --interval 1d

# Get feed distribution in JSON format
python -m cli.elastic_search threat-stats -t feed --format json
```

## Output Formats

All commands support two output formats:

- `table`: Human-readable formatted table (default)
- `json`: JSON format for programmatic use

## Common Options

Most commands support:

- Query filtering with `-q/--query`
- Output format selection with `-f/--format`
- Result size limitation with `--size`

## Examples of Complex Queries

```bash
# Search for events in a specific location and date range
python -m cli.elastic_search events -q "protest" -s 2023-01-01 -e 2023-12-31 -l "33.5,36.3,10km"

# Get event statistics for a specific time period
python -m cli.elastic_search event-stats -t time --interval 1w -s 2023-01-01 -e 2023-12-31

# Search for actors with type filter
python -m cli.elastic_search actors -q "military" -t "State Forces"

# Get technique statistics filtered by query
python -m cli.elastic_search technique-stats -q "phishing" -t platform

# Search threat content with multiple filters
python -m cli.elastic_search threat-content -q "zero-day" -c "SecurityWeek" -s 2025-01-01 -e 2025-03-23 --size 20

# Get threat content statistics with query filter
python -m cli.elastic_search threat-stats -q "vulnerability" -t time --interval 1w
```
