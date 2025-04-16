from app import db


class Country(db.Model):
    """Model for the global_countries_eda table."""

    __tablename__ = "global_countries_eda"

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False, index=True)
    abbreviation = db.Column(db.String(10), index=True)
    capital_city = db.Column(db.String(100))
    currency_code = db.Column(db.String(10))
    official_language = db.Column(db.String(100))
    population = db.Column(db.Float, index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp()
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp()
    )

    # Additional fields are available but not mapped here for simplicity

    def __repr__(self):
        return f"<Country {self.country} ({self.abbreviation})>"
