from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, URL, Length

# Placeholder choices - these should ideally come from a config or database
INDUSTRY_CHOICES = [
    ("", "-- Select Industry --"),
    ("Critical: Military/Defense", "Critical: Military/Defense"),
    ("Critical: Government", "Critical: Government"),
    ("Critical: Infrastructure", "Critical: Infrastructure"),
    ("Critical: Financial Services", "Critical: Financial Services"),
    ("High-Impact: News Media", "High-Impact: News Media"),
    ("High-Impact: Technology", "High-Impact: Technology"),
    ("High-Impact: Manufacturing", "High-Impact: Manufacturing"),
    ("High-Impact: Transportation", "High-Impact: Transportation"),
    ("Support: Professional Services", "Support: Professional Services"),
    ("Support: Telecommunications", "Support: Telecommunications"),
    ("Support: Energy", "Support: Energy"),
    ("Support: Healthcare", "Support: Healthcare"),
    ("Other", "Other"),
]

# Placeholder - a real app would use a more comprehensive list
COUNTRY_CHOICES = [
    ("", "-- Select Country --"),
    ("US", "United States"),
    ("CA", "Canada"),
    ("GB", "United Kingdom"),
    ("DE", "Germany"),
    ("FR", "France"),
    ("JP", "Japan"),
    # Add more countries as needed
]


class ClientOnboardingForm(FlaskForm):
    """Form for onboarding a new client."""

    # Organization Details
    name = StringField(
        "Organization Name", validators=[DataRequired(), Length(max=128)]
    )
    industry = SelectField(
        "Industry", choices=INDUSTRY_CHOICES, validators=[DataRequired()]
    )
    website = StringField("Website", validators=[Optional(), URL(), Length(max=128)])
    description = TextAreaField("Description", validators=[Optional()])
    public_profile_summary = TextAreaField(
        "Public Profile Summary", validators=[Optional()]
    )

    # Primary Contact Details
    contact_first_name = StringField(
        "Contact First Name", validators=[DataRequired(), Length(max=64)]
    )
    contact_last_name = StringField(
        "Contact Last Name", validators=[DataRequired(), Length(max=64)]
    )
    contact_email = StringField(
        "Contact Email", validators=[DataRequired(), Email(), Length(max=120)]
    )
    contact_phone = StringField("Contact Phone", validators=[Optional(), Length(max=20)])
    contact_position = StringField(
        "Contact Position", validators=[Optional(), Length(max=64)]
    )

    # Primary Location Details (Assuming HQ)
    location_name = StringField(
        "Location Name", default="Headquarters", validators=[DataRequired(), Length(max=128)]
    )
    location_address = StringField("Address", validators=[Optional(), Length(max=256)])
    location_city = StringField("City", validators=[Optional(), Length(max=64)])
    location_state = StringField("State/Province", validators=[Optional(), Length(max=64)])
    location_country = SelectField(
        "Country", choices=COUNTRY_CHOICES, validators=[DataRequired()]
    )
    location_postal_code = StringField(
        "Postal Code", validators=[Optional(), Length(max=20)]
    )

    submit = SubmitField("Onboard Client")