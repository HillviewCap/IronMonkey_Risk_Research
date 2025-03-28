"""
Elasticsearch service for querying Threat Intelligence Platform (TIP) data.
"""
import logging
from flask import current_app
from app.services.elasticsearch.base import ElasticsearchService

logger = logging.getLogger(__name__)

class TipSearchService(ElasticsearchService):
    """Service for querying TIP data in Elasticsearch"""

    VULNERABILITY_INDEX = 'tip_vulnerabilities'  # Assuming this index name

    @classmethod
    def find_vulnerabilities_for_asset(cls, asset_identifier, identifier_type='ip', min_severity='Medium', size=100):
        """
        Find vulnerabilities associated with a specific asset identifier.

        Args:
            asset_identifier (str): The identifier of the asset (e.g., IP address, hostname).
            identifier_type (str): The type of identifier ('ip', 'hostname', etc.). Default 'ip'.
            min_severity (str): Minimum severity level to include (e.g., 'Low', 'Medium', 'High', 'Critical'). Default 'Medium'.
            size (int): Maximum number of vulnerabilities to return. Default 100.

        Returns:
            list: A list of vulnerability documents found, or an empty list if none found or error.
        """
        if not cls.client or not asset_identifier:
            logger.warning("Elasticsearch client not available or asset identifier missing.")
            return []

        # Map severity levels to numerical order for range query
        severity_order = {
            'Low': 1,
            'Medium': 2,
            'High': 3,
            'Critical': 4
        }
        min_severity_level = severity_order.get(min_severity, 2) # Default to Medium if invalid

        # Determine the field to query based on identifier_type
        # Add more types as needed (e.g., hostname, cpe)
        if identifier_type == 'ip':
            field_to_query = 'asset_ip' # Assuming this field exists in the index
        # elif identifier_type == 'hostname':
        #     field_to_query = 'asset_hostname' # Assuming this field exists
        else:
            logger.warning(f"Unsupported identifier type: {identifier_type}")
            return []

        query = {
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {"term": {field_to_query: asset_identifier}}
                    ],
                    "filter": [
                        {"range": {"severity_level": {"gte": min_severity_level}}} # Assuming a numeric severity_level field exists
                        # Add date range filters if needed, e.g.,
                        # {"range": {"published_date": {"gte": "now-1y/d"}}}
                    ]
                }
            },
            "sort": [
                {"published_date": {"order": "desc"}} # Assuming published_date exists
            ]
        }

        try:
            result = cls.search(cls.VULNERABILITY_INDEX, query)
            if not result or 'hits' not in result or 'hits' not in result['hits']:
                logger.debug(f"No vulnerabilities found for {identifier_type} {asset_identifier} or error in search.")
                return []

            vulnerabilities = [hit['_source'] for hit in result['hits']['hits']]
            logger.info(f"Found {len(vulnerabilities)} vulnerabilities for {identifier_type} {asset_identifier} (min severity: {min_severity}).")
            return vulnerabilities

        except Exception as e:
            logger.error(f"Error searching vulnerabilities for {identifier_type} {asset_identifier}: {e}", exc_info=True)
            return []