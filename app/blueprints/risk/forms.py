from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


# Basic form for adding a finding - fields can be added later as needed
class AddFindingForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description", validators=[Optional()])
    # Add other relevant fields for a finding here
    submit = SubmitField("Add Finding")


# Re-define AssessmentForm and EditAssessmentForm here if they are specific to risk
# Or adjust the import in routes.py if they live elsewhere (e.g., a shared forms module)


class AssessmentForm(FlaskForm):
    client_id = SelectField("Client", coerce=int, validators=[DataRequired()])
    name = StringField("Assessment Name", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description", validators=[Optional()])
    assessment_date = DateField(
        "Assessment Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    assessment_type = SelectField(
        "Assessment Type",
        choices=[
            ("Internal", "Internal"),
            ("External", "External"),
            ("Compliance", "Compliance"),
            ("Vulnerability", "Vulnerability Scan"),
            ("Penetration", "Penetration Test"),
            ("Targeted Conflict", "Targeted Conflict Simulation"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Create Assessment")


class EditAssessmentForm(AssessmentForm):  # Inherits from AssessmentForm
    status = SelectField(
        "Status",
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("archived", "Archived"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Assessment")
