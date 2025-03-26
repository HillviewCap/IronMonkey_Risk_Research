"""
Initialize framework configuration data for the Risk Assessment Engine
"""
import sys
import os
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.framework import IndustryProfile, ConnectionType, AmplificationFactor, ScoringConfiguration

def init_industry_profiles():
    """Initialize industry profiles with baseline risk scores"""
    profiles = [
        {
            'industry': 'Military/Defense',
            'category': 'Critical',
            'description': 'Organizations directly involved in military operations or defense contracting',
            'baseline_risk_score': 80.0,
            'vulnerability_factors': {
                'targeted_frequency': 'High',
                'data_sensitivity': 'Extreme',
                'infrastructure_criticality': 'High'
            }
        },
        {
            'industry': 'Government',
            'category': 'Critical',
            'description': 'Government agencies and public sector organizations',
            'baseline_risk_score': 75.0,
            'vulnerability_factors': {
                'targeted_frequency': 'High',
                'data_sensitivity': 'High',
                'infrastructure_criticality': 'High'
            }
        },
        {
            'industry': 'Critical Infrastructure',
            'category': 'Critical',
            'description': 'Energy, water, transportation, and other critical infrastructure',
            'baseline_risk_score': 70.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Medium',
                'data_sensitivity': 'Medium',
                'infrastructure_criticality': 'Extreme'
            }
        },
        {
            'industry': 'Financial Services',
            'category': 'Critical',
            'description': 'Banks, insurance, and financial institutions',
            'baseline_risk_score': 65.0,
            'vulnerability_factors': {
                'targeted_frequency': 'High',
                'data_sensitivity': 'High',
                'infrastructure_criticality': 'Medium'
            }
        },
        {
            'industry': 'News Media',
            'category': 'High-Impact',
            'description': 'News organizations and media outlets',
            'baseline_risk_score': 60.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Medium',
                'data_sensitivity': 'Medium',
                'infrastructure_criticality': 'Low'
            }
        },
        {
            'industry': 'Technology',
            'category': 'High-Impact',
            'description': 'Technology companies and software developers',
            'baseline_risk_score': 55.0,
            'vulnerability_factors': {
                'targeted_frequency': 'High',
                'data_sensitivity': 'Medium',
                'infrastructure_criticality': 'Medium'
            }
        },
        {
            'industry': 'Manufacturing',
            'category': 'High-Impact',
            'description': 'Manufacturing companies and industrial organizations',
            'baseline_risk_score': 50.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Medium',
                'data_sensitivity': 'Low',
                'infrastructure_criticality': 'Medium'
            }
        },
        {
            'industry': 'Transportation',
            'category': 'High-Impact',
            'description': 'Transportation and logistics companies',
            'baseline_risk_score': 45.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Low',
                'data_sensitivity': 'Low',
                'infrastructure_criticality': 'High'
            }
        },
        {
            'industry': 'Professional Services',
            'category': 'Support',
            'description': 'Consulting, legal, and other professional services',
            'baseline_risk_score': 40.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Low',
                'data_sensitivity': 'Medium',
                'infrastructure_criticality': 'Low'
            }
        },
        {
            'industry': 'Telecommunications',
            'category': 'Support',
            'description': 'Telecommunications providers and services',
            'baseline_risk_score': 35.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Medium',
                'data_sensitivity': 'Medium',
                'infrastructure_criticality': 'High'
            }
        },
        {
            'industry': 'Energy',
            'category': 'Support',
            'description': 'Energy companies and utilities',
            'baseline_risk_score': 30.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Medium',
                'data_sensitivity': 'Low',
                'infrastructure_criticality': 'High'
            }
        },
        {
            'industry': 'Healthcare',
            'category': 'Support',
            'description': 'Healthcare providers and services',
            'baseline_risk_score': 25.0,
            'vulnerability_factors': {
                'targeted_frequency': 'Medium',
                'data_sensitivity': 'High',
                'infrastructure_criticality': 'Medium'
            }
        }
    ]
    
    for profile_data in profiles:
        profile = IndustryProfile(
            industry=profile_data['industry'],
            category=profile_data['category'],
            description=profile_data['description'],
            baseline_risk_score=profile_data['baseline_risk_score'],
            vulnerability_factors=profile_data['vulnerability_factors']
        )
        db.session.add(profile)
    
    db.session.commit()
    print(f"Added {len(profiles)} industry profiles")

def init_connection_types():
    """Initialize connection types with impact multipliers"""
    connection_types = [
        {
            'name': 'Direct',
            'description': 'Direct exposure through physical presence, client relationships, or infrastructure dependency',
            'impact_multiplier': 1.5
        },
        {
            'name': 'Indirect',
            'description': 'Indirect exposure through supply chain, partner networks, or market dependencies',
            'impact_multiplier': 1.2
        },
        {
            'name': 'Reputational',
            'description': 'Exposure through public statements, media coverage, or industry position',
            'impact_multiplier': 1.1
        }
    ]
    
    for connection_data in connection_types:
        connection = ConnectionType(
            name=connection_data['name'],
            description=connection_data['description'],
            impact_multiplier=connection_data['impact_multiplier']
        )
        db.session.add(connection)
    
    db.session.commit()
    print(f"Added {len(connection_types)} connection types")

def init_amplification_factors():
    """Initialize amplification factors with weights"""
    amplification_factors = [
        # Primary factors
        {
            'name': 'Conflict Intensity',
            'category': 'Primary',
            'description': 'Level of intensity of the conflict',
            'min_value': 1.0,
            'max_value': 2.0,
            'weight': 0.3
        },
        {
            'name': 'Geographic Proximity',
            'category': 'Primary',
            'description': 'Proximity to the conflict zone',
            'min_value': 1.0,
            'max_value': 1.8,
            'weight': 0.25
        },
        {
            'name': 'Industry Sector',
            'category': 'Primary',
            'description': 'Industry sector vulnerability',
            'min_value': 1.0,
            'max_value': 1.5,
            'weight': 0.2
        },
        {
            'name': 'Public Stance',
            'category': 'Primary',
            'description': 'Public position on the conflict',
            'min_value': 1.0,
            'max_value': 1.3,
            'weight': 0.15
        },
        # Secondary factors
        {
            'name': 'Infrastructure Dependency',
            'category': 'Secondary',
            'description': 'Dependency on infrastructure in conflict zones',
            'min_value': 1.0,
            'max_value': 1.4,
            'weight': 0.1
        },
        {
            'name': 'Supply Chain Exposure',
            'category': 'Secondary',
            'description': 'Exposure through supply chain connections',
            'min_value': 1.0,
            'max_value': 1.3,
            'weight': 0.1
        },
        {
            'name': 'Data Sensitivity',
            'category': 'Secondary',
            'description': 'Sensitivity of data that could be targeted',
            'min_value': 1.0,
            'max_value': 1.2,
            'weight': 0.05
        },
        {
            'name': 'Regulatory Requirements',
            'category': 'Secondary',
            'description': 'Regulatory compliance requirements',
            'min_value': 1.0,
            'max_value': 1.1,
            'weight': 0.05
        }
    ]
    
    for factor_data in amplification_factors:
        factor = AmplificationFactor(
            name=factor_data['name'],
            category=factor_data['category'],
            description=factor_data['description'],
            min_value=factor_data['min_value'],
            max_value=factor_data['max_value'],
            weight=factor_data['weight']
        )
        db.session.add(factor)
    
    db.session.commit()
    print(f"Added {len(amplification_factors)} amplification factors")

def init_scoring_configurations():
    """Initialize scoring configurations"""
    scoring_configs = [
        {
            'name': 'Standard Framework v2.0',
            'description': 'Standard scoring configuration for the Enhanced Framework v2.0',
            'is_active': True,
            'configuration': {
                'conflict_weight': 0.3,
                'cyber_weight': 0.3,
                'exposure_weight': 0.4,
                'severity_weights': {
                    'Critical': 1.0,
                    'High': 0.75,
                    'Medium': 0.5,
                    'Low': 0.25
                },
                'likelihood_weights': {
                    'High': 1.0,
                    'Medium': 0.6,
                    'Low': 0.3
                }
            }
        },
        {
            'name': 'Conflict-Focused',
            'description': 'Configuration with higher weight on conflict factors',
            'is_active': False,
            'configuration': {
                'conflict_weight': 0.5,
                'cyber_weight': 0.2,
                'exposure_weight': 0.3,
                'severity_weights': {
                    'Critical': 1.0,
                    'High': 0.75,
                    'Medium': 0.5,
                    'Low': 0.25
                },
                'likelihood_weights': {
                    'High': 1.0,
                    'Medium': 0.6,
                    'Low': 0.3
                }
            }
        },
        {
            'name': 'Cyber-Focused',
            'description': 'Configuration with higher weight on cyber factors',
            'is_active': False,
            'configuration': {
                'conflict_weight': 0.2,
                'cyber_weight': 0.5,
                'exposure_weight': 0.3,
                'severity_weights': {
                    'Critical': 1.0,
                    'High': 0.75,
                    'Medium': 0.5,
                    'Low': 0.25
                },
                'likelihood_weights': {
                    'High': 1.0,
                    'Medium': 0.6,
                    'Low': 0.3
                }
            }
        }
    ]
    
    for config_data in scoring_configs:
        config = ScoringConfiguration(
            name=config_data['name'],
            description=config_data['description'],
            is_active=config_data['is_active'],
            configuration=config_data['configuration']
        )
        db.session.add(config)
    
    db.session.commit()
    print(f"Added {len(scoring_configs)} scoring configurations")

def main():
    """Main function to initialize all framework data"""
    app = create_app()
    with app.app_context():
        # Check if data already exists
        if IndustryProfile.query.count() > 0:
            print("Industry profiles already exist. Skipping initialization.")
        else:
            init_industry_profiles()
        
        if ConnectionType.query.count() > 0:
            print("Connection types already exist. Skipping initialization.")
        else:
            init_connection_types()
        
        if AmplificationFactor.query.count() > 0:
            print("Amplification factors already exist. Skipping initialization.")
        else:
            init_amplification_factors()
        
        if ScoringConfiguration.query.count() > 0:
            print("Scoring configurations already exist. Skipping initialization.")
        else:
            init_scoring_configurations()
        
        print("Framework data initialization complete")

if __name__ == '__main__':
    main()