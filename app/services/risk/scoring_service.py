"""
Scoring service for risk assessments based on the Enhanced Framework v2.0
"""
from flask import current_app
from app.models.risk import Assessment, Finding
from app.models.client import Client, ClientAsset, ClientLocation
from app.models.framework import IndustryProfile, ConnectionType, AmplificationFactor, ScoringConfiguration
from app.services.elasticsearch.risk_service import RiskSearchService
from app.services.elasticsearch.tip_service import TipSearchService # Import TipSearchService
from app import db
import logging

logger = logging.getLogger(__name__)

# Define high-risk countries for Basic Assessment geographic scoring
HIGH_RISK_COUNTRIES = ['Ukraine', 'Syria', 'Yemen', 'Afghanistan', 'Russia', 'Iran', 'North Korea', 'Myanmar']

class ScoringService:
    """Service for calculating risk scores based on the Enhanced Framework v2.0 or Basic Assessment"""

    @staticmethod
    def calculate_assessment_score(assessment_id):
        """
        Calculate the risk score for an assessment based on its type
        (Enhanced Framework v2.0 or Basic Assessment).

        Args:
            assessment_id: ID of the assessment to score

        Returns:
            Dictionary with overall score and component scores, or None if assessment not found or error occurs.
        """
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            logger.warning(f"Assessment {assessment_id} not found for scoring.")
            return None

        client = Client.query.get(assessment.client_id)
        if not client:
            logger.warning(f"Client {assessment.client_id} not found for assessment {assessment_id}.")
            return None

        results = None
        if assessment.assessment_type == 'Basic':
            logger.info(f"Calculating Basic Assessment score for assessment {assessment_id}.")
            results = ScoringService._calculate_basic_assessment_score(assessment, client)
        else:
            # Assume Full Framework or other types use the original logic
            logger.info(f"Calculating Full Framework score for assessment {assessment_id} (Type: {assessment.assessment_type}).")
            results = ScoringService._calculate_full_framework_score(assessment, client)

        if not results:
            logger.error(f"Failed to calculate score for assessment {assessment_id} (Type: {assessment.assessment_type}).")
            return None

        # Store scores in assessment object
        assessment.risk_score = results['overall_score']
        assessment.framework_scores = results['details'] # Use 'details' key for component scores

        try:
            db.session.commit()
            logger.info(f"Successfully calculated and saved score for assessment {assessment_id} (Type: {assessment.assessment_type}, Score: {results['overall_score']})")

            # Index updated assessment in Elasticsearch
            # Consider making this asynchronous in a real application
            RiskSearchService.index_assessment(assessment)

            return {
                'overall_score': assessment.risk_score,
                'framework_scores': assessment.framework_scores
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving score or indexing assessment {assessment_id}: {e}", exc_info=True)
            return None

    @staticmethod
    def _calculate_basic_assessment_score(assessment, client):
        """
        Calculates the score for a 'Basic' assessment.
        Based on: Industry Baseline, Geographic Footprint, Vulnerabilities on Primary Assets.
        """
        try:
            # 1. Get Baseline Risk from Industry Profile
            industry_profile = IndustryProfile.query.filter_by(industry=client.industry).first()
            baseline_risk = 50  # Default baseline
            if industry_profile:
                baseline_risk = industry_profile.baseline_risk_score
            else:
                logger.warning(f"No industry profile found for client {client.id} industry '{client.industry}'. Using default baseline risk {baseline_risk}.")

            # 2. Calculate Geographic Risk Factor
            geo_risk_factor = 0
            client_locations = ClientLocation.query.filter_by(client_id=client.id).all()
            high_risk_location_count = sum(1 for loc in client_locations if loc.country in HIGH_RISK_COUNTRIES)
            if high_risk_location_count > 0:
                # Simple score: 15 points if any location is high-risk, max 30
                geo_risk_factor = min(30, 15 + (high_risk_location_count - 1) * 5)
                logger.debug(f"Client {client.id} has {high_risk_location_count} locations in high-risk countries. Geo risk factor: {geo_risk_factor}")

            # 3. Calculate Vulnerability Score from Primary Assets
            vulnerability_score_component = 0
            total_vulnerabilities_found = 0
            critical_high_vulnerabilities_found = 0
            primary_assets = ClientAsset.query.filter(
                ClientAsset.client_id == client.id,
                ClientAsset.criticality_score >= 8, # Primary asset definition
                ClientAsset.asset_identifier != None, # Need an identifier to search
                ClientAsset.identifier_type != None # Need type for search field
            ).all()

            logger.debug(f"Found {len(primary_assets)} primary assets for client {client.id} for vulnerability check.")

            severity_map = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}

            if primary_assets:
                vuln_points = 0
                for asset in primary_assets:
                    # Ensure asset_identifier and identifier_type are not None before proceeding
                    if asset.asset_identifier and asset.identifier_type:
                        logger.debug(f"Checking vulnerabilities for asset {asset.id} ({asset.identifier_type}: {asset.asset_identifier})")
                        vulnerabilities = TipSearchService.find_vulnerabilities_for_asset(
                            asset_identifier=asset.asset_identifier,
                            identifier_type=asset.identifier_type,
                            min_severity='Medium' # Only consider Medium+ for scoring
                        )
                        if vulnerabilities:
                            asset_vuln_count = len(vulnerabilities)
                            total_vulnerabilities_found += asset_vuln_count
                            # Assuming 'severity' field exists in ES vulnerability doc
                            asset_crit_high_count = sum(1 for v in vulnerabilities if severity_map.get(v.get('severity'), 0) >= 3)
                            critical_high_vulnerabilities_found += asset_crit_high_count
                            logger.debug(f" -> Found {asset_vuln_count} vulnerabilities ({asset_crit_high_count} Critical/High) for asset {asset.id}")
                            # Add points: 2 per C/H vuln, 0.5 per Medium vuln
                            vuln_points += asset_crit_high_count * 2 + (asset_vuln_count - asset_crit_high_count) * 0.5
                    else:
                        logger.warning(f"Skipping asset {asset.id} due to missing identifier or type.")


                # Scale vulnerability points to a max score component (e.g., max 50 points)
                vulnerability_score_component = min(50, vuln_points)
                logger.debug(f"Total vulnerability points: {vuln_points}. Scaled component score: {vulnerability_score_component}")

            # 4. Combine Scores (Additive Approach)
            # Start with baseline, add weighted contributions capped at max points.
            geo_contribution = min(20, geo_risk_factor * (20/30)) # Max 20 points from Geo (scaling from max 30)
            vuln_contribution = min(40, vulnerability_score_component * (40/50)) # Max 40 points from Vuln (scaling from max 50)
            overall_score = baseline_risk + geo_contribution + vuln_contribution

            overall_score = max(0, min(100, round(overall_score))) # Ensure 0-100 and round

            details = {
                'type': 'Basic',
                'baseline_risk': baseline_risk,
                'geo_risk_factor': geo_risk_factor,
                'geo_contribution': round(geo_contribution, 2),
                'vulnerability_score_component': vulnerability_score_component,
                'vuln_contribution': round(vuln_contribution, 2),
                'primary_assets_checked': len(primary_assets),
                'total_vulnerabilities_found': total_vulnerabilities_found,
                'critical_high_vulnerabilities_found': critical_high_vulnerabilities_found
            }
            logger.info(f"Basic Assessment calculation complete for {assessment.id}. Score: {overall_score}, Details: {details}")
            return {'overall_score': overall_score, 'details': details}

        except Exception as e:
            logger.error(f"Error calculating Basic Assessment score for assessment {assessment.id}: {e}", exc_info=True)
            return None


    @staticmethod
    def _calculate_full_framework_score(assessment, client):
        """ Calculates the score based on the Full Enhanced Framework v2.0 """
        # Get scoring configuration (Required for Full Framework)
        scoring_config = None
        if assessment.scoring_config_id:
            scoring_config = ScoringConfiguration.query.get(assessment.scoring_config_id)

        if not scoring_config:
            scoring_config = ScoringConfiguration.query.filter_by(is_active=True).first()

        if not scoring_config:
            logger.warning(f"No scoring configuration found for Full Framework assessment {assessment.id}. Cannot calculate score.")
            return None

        # Calculate component scores for Full Framework
        conflict_score = ScoringService._calculate_conflict_score(assessment)
        cyber_score = ScoringService._calculate_cyber_score(assessment)
        org_exposure_score = ScoringService._calculate_org_exposure_score(assessment, client)

        # Get industry profile for baseline risk
        industry_profile = IndustryProfile.query.filter_by(industry=client.industry).first()
        baseline_risk = 50  # Default baseline if no industry profile found
        if industry_profile:
            baseline_risk = industry_profile.baseline_risk_score

        # Calculate overall score using the framework's methodology
        config = scoring_config.configuration
        conflict_weight = config.get('conflict_weight', 0.3)
        cyber_weight = config.get('cyber_weight', 0.3)
        exposure_weight = config.get('exposure_weight', 0.4)

        weighted_score = (
            conflict_score * conflict_weight +
            cyber_score * cyber_weight +
            org_exposure_score * exposure_weight
        )

        amplification_factor = ScoringService._calculate_amplification_factor(assessment, client)
        overall_score = baseline_risk + (weighted_score * amplification_factor)
        overall_score = max(0, min(100, round(overall_score))) # Ensure 0-100 and round

        details = {
            'type': 'Full Framework',
            'conflict_score': conflict_score,
            'cyber_score': cyber_score,
            'org_exposure_score': org_exposure_score,
            'baseline_risk': baseline_risk,
            'amplification_factor': amplification_factor,
            'weighted_score': weighted_score
        }
        logger.info(f"Full Framework calculation complete for {assessment.id}. Score: {overall_score}")
        return {'overall_score': overall_score, 'details': details}


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