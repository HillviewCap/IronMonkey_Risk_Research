"""
Elasticsearch service for risk assessment data
"""
from flask import current_app
from app.services.elasticsearch.base import ElasticsearchService

class RiskSearchService(ElasticsearchService):
    """Service for risk assessment data in Elasticsearch"""
    
    INDEX_NAME = 'risk_assessments'
    
    @classmethod
    def index_assessment(cls, assessment):
        """
        Index a risk assessment in Elasticsearch
        
        Args:
            assessment: Assessment model instance
            
        Returns:
            Elasticsearch response or None if service not available
        """
        if not assessment:
            return None
        
        # Create assessment document for indexing
        document = {
            'id': assessment.id,
            'client_id': assessment.client_id,
            'name': assessment.name,
            'description': assessment.description,
            'methodology': assessment.methodology,
            'assessment_type': assessment.assessment_type,
            'status': assessment.status,
            'assigned_user_id': assessment.assigned_user_id,
            'risk_score': assessment.risk_score,
            'framework_scores': assessment.framework_scores,
            'scoring_config_id': assessment.scoring_config_id,
            'assessment_date': assessment.assessment_date.isoformat() if assessment.assessment_date else None,
            'created_at': assessment.created_at.isoformat() if assessment.created_at else None,
            'updated_at': assessment.updated_at.isoformat() if assessment.updated_at else None,
            'findings': [],
            'recommendations': []
        }
        
        # Add findings
        for finding in assessment.findings:
            document['findings'].append({
                'id': finding.id,
                'title': finding.title,
                'description': finding.description,
                'risk_level': finding.risk_level,
                'likelihood': finding.likelihood,
                'asset_id': finding.asset_id,
                'framework_category': finding.framework_category,
                'attack_type': finding.attack_type,
                'connection_type_id': finding.connection_type_id,
                'conflict_id': finding.conflict_id,
                'actor_id': finding.actor_id,
                'status': finding.status,
                'score_contribution': finding.score_contribution
            })
        
        # Add recommendations
        for recommendation in assessment.recommendations:
            document['recommendations'].append({
                'id': recommendation.id,
                'title': recommendation.title,
                'description': recommendation.description,
                'priority': recommendation.priority,
                'status': recommendation.status,
                'finding_id': recommendation.finding_id,
                'implementation_cost': recommendation.implementation_cost,
                'implementation_time': recommendation.implementation_time,
                'assigned_user_id': recommendation.assigned_user_id
            })
        
        return cls.index_document(cls.INDEX_NAME, assessment.id, document)
    
    @classmethod
    def search_assessments(cls, query_string, client_id=None, page=1, per_page=10):
        """
        Search risk assessments
        
        Args:
            query_string: Search query string
            client_id: Optional client ID to filter results
            page: Page number (1-based)
            per_page: Results per page
            
        Returns:
            Dict with results and pagination info or None if service not available
        """
        # Calculate pagination offsets
        from_val = (page - 1) * per_page
        
        # Build search query
        should_clauses = [
            {"match": {"name": {"query": query_string, "boost": 3}}},
            {"match": {"description": {"query": query_string, "boost": 2}}},
            {"match": {"findings.title": {"query": query_string, "boost": 2}}},
            {"match": {"findings.description": {"query": query_string}}},
            {"match": {"findings.framework_category": {"query": query_string, "boost": 1.5}}},
            {"match": {"findings.attack_type": {"query": query_string, "boost": 1.5}}},
            {"match": {"recommendations.title": {"query": query_string, "boost": 2}}},
            {"match": {"recommendations.description": {"query": query_string}}}
        ]
        
        must_clauses = []
        if client_id:
            must_clauses.append({"term": {"client_id": client_id}})
        
        query = {
            "size": per_page,
            "from": from_val,
            "query": {
                "bool": {
                    "should": should_clauses,
                    "must": must_clauses
                }
            },
            "sort": [
                {"_score": {"order": "desc"}},
                {"assessment_date": {"order": "desc"}}
            ]
        }
        
        result = cls.search(cls.INDEX_NAME, query)
        if not result:
            return None
        
        # Format results
        assessments = []
        for hit in result.get('hits', {}).get('hits', []):
            assessment = hit.get('_source', {})
            assessment['score'] = hit.get('_score')
            assessments.append(assessment)
        
        total = result.get('hits', {}).get('total', {}).get('value', 0)
        
        return {
            'assessments': assessments,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
