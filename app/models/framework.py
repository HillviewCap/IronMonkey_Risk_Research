"""
Framework models for the Enhanced Geopolitical Cyber Risk Assessment Framework (v2.0)
"""
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB


class IndustryProfile(db.Model):
    """Industry risk profile model for baseline risk assessment"""
    __tablename__ = 'risk_industry_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    industry = db.Column(db.String(64), nullable=False, unique=True)
    category = db.Column(db.String(32), nullable=False)  # Critical, High-Impact, Support
    description = db.Column(db.Text)
    baseline_risk_score = db.Column(db.Float, nullable=False)
    vulnerability_factors = db.Column(JSONB)  # JSON object with vulnerability factors
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<IndustryProfile {self.industry}>'
    
    def to_dict(self):
        """Convert industry profile to dictionary"""
        return {
            'id': self.id,
            'industry': self.industry,
            'category': self.category,
            'description': self.description,
            'baseline_risk_score': self.baseline_risk_score,
            'vulnerability_factors': self.vulnerability_factors,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ConnectionType(db.Model):
    """Connection type model for defining exposure types"""
    __tablename__ = 'risk_connection_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)  # Direct, Indirect, Reputational
    description = db.Column(db.Text)
    impact_multiplier = db.Column(db.Float, nullable=False)  # Multiplier for risk calculation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConnectionType {self.name}>'
    
    def to_dict(self):
        """Convert connection type to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'impact_multiplier': self.impact_multiplier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AmplificationFactor(db.Model):
    """Amplification factor model for risk calculation"""
    __tablename__ = 'risk_amplification_factors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    category = db.Column(db.String(32), nullable=False)  # Primary, Secondary
    description = db.Column(db.Text)
    min_value = db.Column(db.Float, nullable=False)
    max_value = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)  # Weight in the scoring formula
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AmplificationFactor {self.name}>'
    
    def to_dict(self):
        """Convert amplification factor to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ScoringConfiguration(db.Model):
    """Scoring configuration model for risk assessment"""
    __tablename__ = 'risk_scoring_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    configuration = db.Column(JSONB, nullable=False)  # JSON object with scoring configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScoringConfiguration {self.name}>'
    
    def to_dict(self):
        """Convert scoring configuration to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'configuration': self.configuration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }