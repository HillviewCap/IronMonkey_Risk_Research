"""
Risk assessment models
"""
from datetime import datetime
import json
from app import db

class Assessment(db.Model):
    """Risk assessment model"""
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients_organizations.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    assessment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    methodology = db.Column(db.String(64))
    status = db.Column(db.String(32), default='draft')  # draft, in_progress, complete
    risk_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    findings = db.relationship('Finding', backref='assessment', lazy='dynamic')
    recommendations = db.relationship('Recommendation', backref='assessment', lazy='dynamic')
    
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
            'status': self.status,
            'risk_score': self.risk_score,
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = db.relationship('ClientAsset')
    
    def __repr__(self):
        return f'<Finding {self.title}>'


class Recommendation(db.Model):
    """Risk recommendation model"""
    __tablename__ = 'risk_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('risk_assessments.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(16))  # Critical, High, Medium, Low
    implementation_cost = db.Column(db.String(16))  # High, Medium, Low
    implementation_time = db.Column(db.String(16))  # Short, Medium, Long
    status = db.Column(db.String(16), default='open')  # open, in_progress, implemented, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Recommendation {self.title}>'


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
