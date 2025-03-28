"""
Client model for storing client information
"""

from datetime import datetime
import json
from app import db
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB


class Client(db.Model):
    """Client organization model"""

    __tablename__ = "clients_organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    industry = db.Column(db.String(64))
    description = db.Column(db.Text)
    website = db.Column(db.String(128))
    public_profile_summary = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    locations = db.relationship("ClientLocation", backref="client", lazy="dynamic")
    contacts = db.relationship("ClientContact", backref="client", lazy="dynamic")
    assets = db.relationship("ClientAsset", backref="client", lazy="dynamic")
    assessments = db.relationship("Assessment", backref="client", lazy="dynamic")

    def __repr__(self):
        return f"<Client {self.name}>"

    def to_dict(self):
        """Convert client to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry,
            "description": self.description,
            "website": self.website,
            "public_profile_summary": self.public_profile_summary,

            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "locations_count": self.locations.count(),
            "contacts_count": self.contacts.count(),
            "assets_count": self.assets.count(),
            "assessments_count": self.assessments.count(),
        }


class ClientLocation(db.Model):
    """Client location model"""

    __tablename__ = "clients_locations"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("clients_organizations.id"), nullable=False
    )
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    country = db.Column(db.String(64))
    postal_code = db.Column(db.String(20))
    location_type = db.Column(db.String(32))  # HQ, Branch, Data center, etc.
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<ClientLocation {self.name}>"


class ClientContact(db.Model):
    """Client contact person model"""

    __tablename__ = "clients_contacts"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("clients_organizations.id"), nullable=False
    )
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    position = db.Column(db.String(64))
    notes = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<ClientContact {self.first_name} {self.last_name}>"


class ClientAsset(db.Model):
    """Client asset model"""

    __tablename__ = "clients_assets"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("clients_organizations.id"), nullable=False
    )
    name = db.Column(db.String(128), nullable=False)
    asset_type = db.Column(
        db.String, CheckConstraint("asset_type IN ('physical', 'digital', 'personnel')")
    )
    description = db.Column(db.Text)
    criticality_score = db.Column(
        db.Integer, CheckConstraint("criticality_score BETWEEN 1 AND 10")
    )
    location_id = db.Column(db.Integer, db.ForeignKey("clients_locations.id"))
    technical_details = db.Column(JSONB)
    # Instead of using PostGIS geometry type, we'll use regular lat/lon columns
    # geo_location = db.Column(Geometry("POINT", srid=4326))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    location = db.relationship("ClientLocation")

    def __repr__(self):
        return f"<ClientAsset {self.name}>"

    def get_technical_details(self):
        """Get technical details as dictionary"""
        return self.technical_details if self.technical_details is not None else {}

    def set_technical_details(self, details):
        """Set technical details from dictionary or JSON string"""
        if isinstance(details, dict):
            self.technical_details = details
        else:
            try:
                self.technical_details = json.loads(details)
            except Exception:
                self.technical_details = {}
