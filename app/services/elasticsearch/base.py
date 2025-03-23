"""
Base Elasticsearch service for common operations
"""
from flask import current_app

class ElasticsearchService:
    """Base service for Elasticsearch operations"""
    
    @staticmethod
    def get_client():
        """Get the Elasticsearch client from the application"""
        return current_app.elasticsearch
    
    @classmethod
    def index_document(cls, index, document_id, body):
        """
        Index a document in Elasticsearch
        
        Args:
            index: Elasticsearch index name
            document_id: Document ID
            body: Document content
            
        Returns:
            Elasticsearch response or None if service not available
        """
        es = cls.get_client()
        if es is None:
            current_app.logger.warning("Elasticsearch is not configured")
            return None
        
        try:
            return es.index(index=index, id=document_id, document=body)
        except Exception as e:
            current_app.logger.error(f"Error indexing document: {str(e)}")
            return None
    
    @classmethod
    def search(cls, index, query):
        """
        Search documents in Elasticsearch
        
        Args:
            index: Elasticsearch index name
            query: Elasticsearch query
            
        Returns:
            Search results or None if service not available
        """
        es = cls.get_client()
        if es is None:
            current_app.logger.warning("Elasticsearch is not configured")
            return None
        
        try:
            return es.search(index=index, body=query)
        except Exception as e:
            current_app.logger.error(f"Error searching documents: {str(e)}")
            return None
    
    @classmethod
    def get_document(cls, index, document_id):
        """
        Get a document from Elasticsearch
        
        Args:
            index: Elasticsearch index name
            document_id: Document ID
            
        Returns:
            Document or None if not found or service not available
        """
        es = cls.get_client()
        if es is None:
            current_app.logger.warning("Elasticsearch is not configured")
            return None
        
        try:
            return es.get(index=index, id=document_id)
        except Exception as e:
            current_app.logger.error(f"Error getting document: {str(e)}")
            return None
    
    @classmethod
    def delete_document(cls, index, document_id):
        """
        Delete a document from Elasticsearch
        
        Args:
            index: Elasticsearch index name
            document_id: Document ID
            
        Returns:
            Elasticsearch response or None if service not available
        """
        es = cls.get_client()
        if es is None:
            current_app.logger.warning("Elasticsearch is not configured")
            return None
        
        try:
            return es.delete(index=index, id=document_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting document: {str(e)}")
            return None
    
    @classmethod
    def update_document(cls, index, document_id, body):
        """
        Update a document in Elasticsearch
        
        Args:
            index: Elasticsearch index name
            document_id: Document ID
            body: Document content
            
        Returns:
            Elasticsearch response or None if service not available
        """
        es = cls.get_client()
        if es is None:
            current_app.logger.warning("Elasticsearch is not configured")
            return None
        
        try:
            return es.update(index=index, id=document_id, body={"doc": body})
        except Exception as e:
            current_app.logger.error(f"Error updating document: {str(e)}")
            return None
