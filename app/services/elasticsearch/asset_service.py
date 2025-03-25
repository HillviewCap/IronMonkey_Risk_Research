from elasticsearch import Elasticsearch

# Initialize Elasticsearch client
# In a real-world scenario, configure the client with proper hosts and settings
es = Elasticsearch(hosts=["localhost:9200"])


def index_asset(asset):
    """
    Index an asset document in Elasticsearch.

    Args:
        asset: A ClientAsset object.

    Returns:
        The response from the Elasticsearch index operation.
    """
    doc = {
        "id": asset.id,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "description": asset.description,
        "criticality_score": asset.criticality_score,
        "technical_details": asset.get_technical_details(),
    }
    return es.index(index="assets", id=asset.id, document=doc)


def update_asset(asset):
    """
    Update an existing asset document in Elasticsearch.

    Args:
        asset: A ClientAsset object.

    Returns:
        The response from the Elasticsearch update operation.
    """
    doc = {
        "name": asset.name,
        "asset_type": asset.asset_type,
        "description": asset.description,
        "criticality_score": asset.criticality_score,
        "technical_details": asset.get_technical_details(),
    }
    return es.update(index="assets", id=asset.id, doc={"doc": doc})


def delete_asset(asset_id):
    """
    Delete an asset document from Elasticsearch.

    Args:
        asset_id: The ID of the asset to delete.

    Returns:
        The response from the Elasticsearch delete operation.
    """
    return es.delete(index="assets", id=asset_id)


def search_assets(query, filters=None):
    """
    Search for assets in Elasticsearch using text queries and optional filters.

    Args:
        query: The search query string.
        filters: A list of filter conditions (Elasticsearch DSL) to apply.

    Returns:
        The search results from Elasticsearch.
    """
    body = {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {"query": query, "fields": ["name", "description"]}
                },
                "filter": filters if filters else [],
            }
        }
    }
    return es.search(index="assets", body=body)
