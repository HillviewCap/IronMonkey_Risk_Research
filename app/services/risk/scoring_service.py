"""
Scoring service for risk assessments based on the Enhanced Framework v2.0
"""
from flask import current_app
from app.models.risk import Assessment, Finding
from app.models.client import Client, ClientAsset, ClientLocation
from app.models.framework import IndustryProfile, ConnectionType, AmplificationFactor, ScoringConfiguration
from app.services.elasticsearch.risk_service import RiskSearchService
from app import db
import logging

logger = logging.getLogger(__name__)

class ScoringService:
    """Service for calculating risk scores based on the Enhanced Framework v2.0"""
    
    @staticmethod
    def calculate_assessment_score(assessment_id):
        """
        Calculate the risk score for an assessment based on the Enhanced Framework v2.0
        
        Args:
            assessment_id: ID of the assessment to score
            
        Returns:
            Dictionary with overall score and component scores, or None if assessment not found
        """
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            logger.warning(f"Assessment {assessment_id} not found")
            return None
            
        # Get client data
        client = Client.query.get(assessment.client_id)
        if not client:
            logger.warning(f"Client {assessment.client_id} not found")
            return None
            
        # Get scoring configuration
        scoring_config = None
        if assessment.scoring_config_id:
            scoring_config = ScoringConfiguration.query.get(assessment.scoring_config_id)
        
        if not scoring_config:
            # Use default configuration if none specified
            scoring_config = ScoringConfiguration.query.filter_by(is_active=True).first()
            
        if not scoring_config:
            logger.warning("No scoring configuration found")
            return None
            
        # Calculate component scores
        conflict_score = ScoringService._calculate_conflict_score(assessment)
        cyber_score = ScoringService._calculate_cyber_score(assessment)
        org_exposure_score = ScoringService._calculate_org_exposure_score(assessment, client)
        
        # Get industry profile for baseline risk
        industry_profile = IndustryProfile.query.filter_by(industry=client.industry).first()
        baseline_risk = 50  # Default baseline if no industry profile found
        if industry_profile:
            baseline_risk = industry_profile.baseline_risk_score
        
        # Calculate overall score using the framework's methodology
        # This is a simplified implementation - the actual algorithm would be more complex
        # and based on the specific weights and rules defined in the scoring configuration
        config = scoring_config.configuration
        
        # Apply weights from configuration
        conflict_weight = config.get('conflict_weight', 0.3)
        cyber_weight = config.get('cyber_weight', 0.3)
        exposure_weight = config.get('exposure_weight', 0.4)
        
        # Calculate weighted score
        weighted_score = (
            conflict_score * conflict_weight +
            cyber_score * cyber_weight +
            org_exposure_score * exposure_weight
        )
        
        # Apply amplification factors
        amplification_factor = ScoringService._calculate_amplification_factor(assessment, client)
        
        # Final score calculation
        overall_score = baseline_risk + (weighted_score * amplification_factor)
        
        # Ensure score is within bounds (0-100)
        overall_score = max(0, min(100, overall_score))
        
        # Store scores in assessment
        framework_scores = {
            'conflict_score': conflict_score,
            'cyber_score': cyber_score,
            'org_exposure_score': org_exposure_score,
            'baseline_risk': baseline_risk,
            'amplification_factor': amplification_factor,
            'weighted_score': weighted_score
        }
        
        assessment.risk_score = overall_score
        assessment.framework_scores = framework_scores
        db.session.commit()
        
        # Index updated assessment in Elasticsearch
        RiskSearchService.index_assessment(assessment)
        
        return {
            'overall_score': overall_score,
            'framework_scores': framework_scores
        }
    
    @staticmethod
    def _calculate_conflict_score(assessment):
        """
        Calculate the conflict component score
        
        This would typically use data from the intelligence.conflicts index
        For now, we'll use a simplified approach based on findings
        """
        # Get conflict-related findings
        conflict_findings = Finding.query.filter_by(
            assessment_id=assessment.id,
            framework_category='Geopolitical Conflict'
        ).all()
        
        if not conflict_findings:
            return 0
            
        # Calculate score based on finding severity
        severity_map = {
            'Critical': 100,
            'High': 75,
            'Medium': 50,
            'Low': 25
        }
        
        total_severity = sum(severity_map.get(finding.risk_level, 0) for finding in conflict_findings)
        return total_severity / len(conflict_findings)
    
    @staticmethod
    def _calculate_cyber_score(assessment):
        """
        Calculate the cyber power component score
        
        This would typically use data from the intelligence.cyber_actors index
        For now, we'll use a simplified approach based on findings
        """
        # Get cyber-related findings
        cyber_findings = Finding.query.filter_by(
            assessment_id=assessment.id,
            framework_category='Cyber Actor'
        ).all()
        
        if not cyber_findings:
            return 0
            
        # Calculate score based on finding severity
        severity_map = {
            'Critical': 100,
            'High': 75,
            'Medium': 50,
            'Low': 25
        }
        
        total_severity = sum(severity_map.get(finding.risk_level, 0) for finding in cyber_findings)
        return total_severity / len(cyber_findings)
    
    @staticmethod
    def _calculate_org_exposure_score(assessment, client):
        """
        Calculate the organizational exposure component score
        
        This uses client data (locations, assets) and findings
        """
        # Get org exposure-related findings
        exposure_findings = Finding.query.filter_by(
            assessment_id=assessment.id,
            framework_category='Org Exposure'
        ).all()
        
        # Base score on client assets in high-risk areas
        critical_assets = ClientAsset.query.filter_by(
            client_id=client.id
        ).filter(ClientAsset.criticality_score >= 8).count()
        
        # Consider locations in conflict zones (simplified)
        # Use latitude/longitude instead of PostGIS geometry
        high_risk_locations = ClientLocation.query.filter_by(
            client_id=client.id
        ).filter(ClientLocation.country.in_(['Ukraine', 'Syria', 'Yemen', 'Afghanistan'])).count()
        
        # Calculate exposure score
        exposure_score = 0
        
        # Add score from findings
        if exposure_findings:
            severity_map = {
                'Critical': 100,
                'High': 75,
                'Medium': 50,
                'Low': 25
            }
            finding_score = sum(severity_map.get(finding.risk_level, 0) for finding in exposure_findings)
            if exposure_findings:
                finding_score /= len(exposure_findings)
            exposure_score += finding_score * 0.5  # 50% weight to findings
        
        # Add score from assets and locations
        asset_location_score = 0
        if critical_assets > 0:
            asset_location_score += min(100, critical_assets * 10)
        if high_risk_locations > 0:
            asset_location_score += min(100, high_risk_locations * 25)
        
        if critical_assets > 0 or high_risk_locations > 0:
            asset_location_score /= 2  # Average the two components
            exposure_score += asset_location_score * 0.5  # 50% weight to assets/locations
        
        return exposure_score
    
    @staticmethod
    def _calculate_amplification_factor(assessment, client):
        """
        Calculate the amplification factor based on the Risk Amplification Matrix
        
        This considers primary factors (conflict intensity, geographic proximity, 
        industry sector, public stance) and secondary factors (infrastructure dependency,
        supply chain exposure, data sensitivity, regulatory requirements)
        """
        # Get amplification factors from database
        primary_factors = AmplificationFactor.query.filter_by(category='Primary').all()
        secondary_factors = AmplificationFactor.query.filter_by(category='Secondary').all()
        
        # For now, use a simplified approach with a default amplification factor
        # In a real implementation, this would consider various client and assessment attributes
        return 1.2  # 20% amplification as a default
    
    @staticmethod
    def calculate_finding_scores(assessment_id):
        """
        Calculate score contributions for each finding in an assessment
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            Dictionary mapping finding IDs to their score contributions
        """
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            logger.warning(f"Assessment {assessment_id} not found")
            return None
            
        findings = Finding.query.filter_by(assessment_id=assessment_id).all()
        if not findings:
            logger.warning(f"No findings found for assessment {assessment_id}")
            return {}
            
        # Calculate score contribution for each finding
        # This is a simplified implementation
        severity_map = {
            'Critical': 1.0,
            'High': 0.75,
            'Medium': 0.5,
            'Low': 0.25
        }
        
        likelihood_map = {
            'High': 1.0,
            'Medium': 0.6,
            'Low': 0.3
        }
        
        finding_scores = {}
        for finding in findings:
            # Base score on severity and likelihood
            severity_factor = severity_map.get(finding.risk_level, 0.5)
            likelihood_factor = likelihood_map.get(finding.likelihood, 0.5)
            
            # Consider connection type if available
            connection_factor = 1.0
            if finding.connection_type_id:
                connection_type = ConnectionType.query.get(finding.connection_type_id)
                if connection_type:
                    connection_factor = connection_type.impact_multiplier
            
            # Calculate score contribution
            score_contribution = severity_factor * likelihood_factor * connection_factor * 10
            
            # Update finding with score contribution
            finding.score_contribution = score_contribution
            finding_scores[finding.id] = score_contribution
        
        db.session.commit()
        return finding_scores