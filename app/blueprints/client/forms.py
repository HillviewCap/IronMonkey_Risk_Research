from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
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
    # Choices set in route
    location_country = SelectField("Country", validators=[DataRequired()])
    location_postal_code = StringField(
        "Postal Code", validators=[Optional(), Length(max=20)]
    )

    submit = SubmitField("Onboard Client")