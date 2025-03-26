"""
Risk assessment models
"""
from datetime import datetime
import json
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Assessment(db.Model):
    """Risk assessment model"""
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients_organizations.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    assessment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    methodology = db.Column(db.String(64), default='Enhanced Framework v2.0')
    assessment_type = db.Column(db.String(64))  # Full Framework, Targeted Conflict, Ad-hoc
    status = db.Column(db.String(32), default='draft')  # draft, in_progress, review, complete
    assigned_user_id = db.Column(db.Integer)  # Reference to users.users_accounts.id
    risk_score = db.Column(db.Float)
    framework_scores = db.Column(JSONB)  # Component scores (conflict, cyber, org exposure)
    scoring_config_id = db.Column(db.Integer, db.ForeignKey('risk_scoring_configurations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    findings = db.relationship('Finding', backref='assessment', lazy='dynamic')
    recommendations = db.relationship('Recommendation', backref='assessment', lazy='dynamic')
    scoring_config = db.relationship('ScoringConfiguration')
    
    def __repr__(self):
        return f'<Assessment {self.name}>'
    
    def to_dict(self):
        """Convert assessment to dictionary for API responses"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'assessment_date': self.assessment_date.isoformat() if self.assessment_date else None,
            'description': self.description,
            'methodology': self.methodology,
            'assessment_type': self.assessment_type,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'risk_score': self.risk_score,
            'framework_scores': self.framework_scores,
            'scoring_config_id': self.scoring_config_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'findings_count': self.findings.count(),
            'recommendations_count': self.recommendations.count()
        }


class Finding(db.Model):
    """Risk finding model"""
    __tablename__ = 'risk_findings'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('risk_assessments.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    risk_level = db.Column(db.String(16))  # Critical, High, Medium, Low
    impact = db.Column(db.Text)
    likelihood = db.Column(db.String(16))  # High, Medium, Low
    asset_id = db.Column(db.Integer, db.ForeignKey('clients_assets.id'))
    evidence = db.Column(db.Text)
    
    # Framework-specific fields
    framework_category = db.Column(db.String(32))  # Geopolitical Conflict, Cyber Actor, Org Exposure
    attack_type = db.Column(db.String(32))  # Destruction, Disruption, Intelligence, Influence
    connection_type_id = db.Column(db.Integer, db.ForeignKey('risk_connection_types.id'))
    conflict_id = db.Column(db.Integer)  # Reference to intelligence.conflicts (Phase 4)
    actor_id = db.Column(db.Integer)  # Reference to intelligence.cyber_actors (Phase 4)
    status = db.Column(db.String(16), default='open')  # Open, Mitigating, Resolved, Accepted
    score_contribution = db.Column(db.Float)  # Contribution to overall risk score
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = db.relationship('ClientAsset')
    connection_type = db.relationship('ConnectionType')
    
    def __repr__(self):
        return f'<Finding {self.title}>'
        
    def to_dict(self):
        """Convert finding to dictionary for API responses"""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'title': self.title,
            'description': self.description,
            'risk_level': self.risk_level,
            'impact': self.impact,
            'likelihood': self.likelihood,
            'asset_id': self.asset_id,
            'evidence': self.evidence,
            'framework_category': self.framework_category,
            'attack_type': self.attack_type,
            'connection_type_id': self.connection_type_id,
            'conflict_id': self.conflict_id,
            'actor_id': self.actor_id,
            'status': self.status,
            'score_contribution': self.score_contribution,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Recommendation(db.Model):
    """Risk recommendation model"""
    __tablename__ = 'risk_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('risk_assessments.id'), nullable=False)
    finding_id = db.Column(db.Integer, db.ForeignKey('risk_findings.id'))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(16))  # Critical, High, Medium, Low
    implementation_cost = db.Column(db.String(16))  # High, Medium, Low
    implementation_time = db.Column(db.String(16))  # Short, Medium, Long
    status = db.Column(db.String(16), default='open')  # open, in_progress, implemented, rejected
    assigned_user_id = db.Column(db.Integer)  # Reference to users.users_accounts.id
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    finding = db.relationship('Finding', backref='recommendations')
    
    def __repr__(self):
        return f'<Recommendation {self.title}>'
        
    def to_dict(self):
        """Convert recommendation to dictionary for API responses"""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'finding_id': self.finding_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'implementation_cost': self.implementation_cost,
            'implementation_time': self.implementation_time,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class GeoRisk(db.Model):
    """Geopolitical risk model"""
    __tablename__ = 'geo_risks'
    
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64), nullable=False)
    region = db.Column(db.String(64))
    risk_type = db.Column(db.String(32))  # political, economic, cyber, etc.
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    risk_level = db.Column(db.String(16))  # Critical, High, Medium, Low
    source = db.Column(db.String(128))
    published_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GeoRisk {self.title}>'
    
    def to_dict(self):
        """Convert geo risk to dictionary for API responses"""
        return {
            'id': self.id,
            'country': self.country,
            'region': self.region,
            'risk_type': self.risk_type,
            'title': self.title,
            'description': self.description,
            'risk_level': self.risk_level,
            'source': self.source,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CyberThreat(db.Model):
    """Cyber threat model"""
    __tablename__ = 'cyber_threats'
    
    id = db.Column(db.Integer, primary_key=True)
    threat_type = db.Column(db.String(32))  # APT, Malware, Ransomware, etc.
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    actor = db.Column(db.String(64))
    tactics = db.Column(db.String(256))  # MITRE ATT&CK tactics
    techniques = db.Column(db.String(256))  # MITRE ATT&CK techniques
    affected_systems = db.Column(db.String(256))
    indicators = db.Column(db.Text)  # JSON stored IOCs
    risk_level = db.Column(db.String(16))  # Critical, High, Medium, Low
    source = db.Column(db.String(128))
    published_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CyberThreat {self.title}>'
    
    def get_indicators(self):
        """Get indicators as dictionary"""
        if self.indicators:
            return json.loads(self.indicators)
        return {}
    
    def set_indicators(self, indicators):
        """Set indicators from dictionary"""
        self.indicators = json.dumps(indicators)
