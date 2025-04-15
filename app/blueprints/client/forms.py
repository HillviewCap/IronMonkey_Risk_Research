from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SubmitField,
    FloatField,
    IntegerField,
    BooleanField,
    HiddenField,
)
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, URL, Length, NumberRange
from wtforms.validators import DataRequired, Email, Optional, URL, Length

# Industry and Country choices will be populated dynamically in the route


class ClientOnboardingForm(FlaskForm):
    """Form for onboarding a new client."""

    # Organization Details
    name = StringField(
        "Organization Name", validators=[DataRequired(), Length(max=128)]
    )
    # Choices set in route
    industry = SelectField("Industry", validators=[DataRequired()])
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
    contact_phone = StringField(
        "Contact Phone", validators=[Optional(), Length(max=20)]
    )
    contact_position = StringField(
        "Contact Position", validators=[Optional(), Length(max=64)]
    )

    # Primary Location Details (Assuming HQ)
    location_name = StringField(
        "Location Name",
        default="Headquarters",
        validators=[DataRequired(), Length(max=128)],
    )
    location_address = StringField("Address", validators=[Optional(), Length(max=256)])
    location_city = StringField("City", validators=[Optional(), Length(max=64)])
    location_state = StringField(
        "State/Province", validators=[Optional(), Length(max=64)]
    )
    # Choices set in route
    location_country = SelectField("Country", validators=[DataRequired()])
    location_postal_code = StringField(
        "Postal Code", validators=[Optional(), Length(max=20)]
    )

    submit = SubmitField("Onboard Client")


class ClientEditForm(FlaskForm):
    """Form for editing core client details."""

    name = StringField(
        "Organization Name", validators=[DataRequired(), Length(max=128)]
    )
    # Choices set in route
    industry = SelectField("Industry", validators=[DataRequired()])
    website = StringField("Website", validators=[Optional(), URL(), Length(max=128)])
    description = TextAreaField("Description", validators=[Optional()])
    public_profile_summary = TextAreaField(
        "Public Profile Summary", validators=[Optional()]
    )
    # Using TextArea for competitors, expecting JSON or comma-separated. Could enhance with JS later.
    competitors = TextAreaField(
        "Competitors (JSON or comma-separated)", validators=[Optional()]
    )
    submit = SubmitField("Save Changes")


class LocationForm(FlaskForm):
    """Form for adding/editing a client location."""

    name = StringField("Location Name", validators=[DataRequired(), Length(max=128)])
    location_type = StringField(
        "Location Type (e.g., HQ, Branch, Data Center)",
        validators=[Optional(), Length(max=32)],
    )
    address = StringField("Address", validators=[Optional(), Length(max=256)])
    city = StringField("City", validators=[Optional(), Length(max=64)])
    state = StringField("State/Province", validators=[Optional(), Length(max=64)])
    # Choices set in route
    country = SelectField("Country", validators=[DataRequired()])
    postal_code = StringField("Postal Code", validators=[Optional(), Length(max=20)])
    latitude = FloatField(
        "Latitude", validators=[Optional(), NumberRange(min=-90, max=90)]
    )
    longitude = FloatField(
        "Longitude", validators=[Optional(), NumberRange(min=-180, max=180)]
    )
    submit = SubmitField("Save Location")


class ContactForm(FlaskForm):
    """Form for adding/editing a client contact."""

    first_name = StringField("First Name", validators=[DataRequired(), Length(max=64)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=64)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    position = StringField("Position", validators=[Optional(), Length(max=64)])
    notes = TextAreaField("Notes", validators=[Optional()])
    is_primary = BooleanField("Is Primary Contact?", default=False)
    submit = SubmitField("Save Contact")


class AssetForm(FlaskForm):
    """Form for adding/editing a client asset."""

    name = StringField("Asset Name", validators=[DataRequired(), Length(max=128)])
    asset_type = SelectField(
        "Asset Type",
        choices=[
            ("physical", "Physical"),
            ("digital", "Digital"),
            ("personnel", "Personnel"),
        ],
        validators=[DataRequired()],
    )
    description = TextAreaField("Description", validators=[Optional()])
    criticality_score = IntegerField(
        "Criticality Score (1-10)", validators=[Optional(), NumberRange(min=1, max=10)]
    )
    # Choices set in route
    location_id = SelectField(
        "Location (Optional)", validators=[Optional()]
    )  # Removed coerce=int
    # Hidden field to store technical details (categories) as a JSON string list
    technical_details = HiddenField(
        "Technical Details (Categories)", validators=[Optional()]
    )
    submit = SubmitField("Save Asset")
