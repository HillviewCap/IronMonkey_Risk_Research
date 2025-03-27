"""
Routes for risk assessment blueprint
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, Response
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.risk import risk_bp
from app.models.risk import Assessment, Finding, Recommendation
from app.models.client import Client
from .forms import (
    AddFindingForm,
    AssessmentForm,
    EditAssessmentForm,
)  # Assuming AddFindingForm exists
from app.models.framework import ScoringConfiguration
from app.services.risk.scoring_service import ScoringService
from app.services.elasticsearch.risk_service import RiskSearchService
from app.services.reports.report_service import ReportService
from app import db
from datetime import datetime
import json


@risk_bp.route("/dashboard")
@login_required
def dashboard():
    """Display risk dashboard with framework-specific information"""
    # Get recent assessments
    recent_assessments = (
        Assessment.query.order_by(Assessment.updated_at.desc()).limit(5).all()
    )

    # Get high-risk assessments
    high_risk_assessments = (
        Assessment.query.filter(Assessment.risk_score >= 75)
        .order_by(Assessment.risk_score.desc())
        .limit(5)
        .all()
    )

    # Get assessment statistics
    total_assessments = Assessment.query.count()
    completed_assessments = Assessment.query.filter_by(status="complete").count()
    in_progress_assessments = Assessment.query.filter_by(status="in_progress").count()

    # Get framework statistics (e.g., distribution of findings by category)
    framework_categories = (
        db.session.query(Finding.framework_category, db.func.count(Finding.id))
        .group_by(Finding.framework_category)
        .all()
    )

    framework_stats = {
        category: count for category, count in framework_categories if category
    }

    return render_template(
        "risk/dashboard.html",
        recent_assessments=recent_assessments,
        high_risk_assessments=high_risk_assessments,
        total_assessments=total_assessments,
        completed_assessments=completed_assessments,
        in_progress_assessments=in_progress_assessments,
        framework_stats=framework_stats,
    )


@risk_bp.route("/assessments")
@login_required
def assessment_list():
    """Display list of risk assessments with framework-specific filtering"""
    # Get filter parameters
    client_id = request.args.get("client_id", type=int)
    status = request.args.get("status")
    assessment_type = request.args.get("assessment_type")
    framework_category = request.args.get("framework_category")
    min_risk_score = request.args.get("min_risk_score", type=float)
    max_risk_score = request.args.get("max_risk_score", type=float)

    # Build query
    query = Assessment.query

    if client_id:
        query = query.filter_by(client_id=client_id)

    if status:
        query = query.filter_by(status=status)

    if assessment_type:
        query = query.filter_by(assessment_type=assessment_type)

    if min_risk_score is not None:
        query = query.filter(Assessment.risk_score >= min_risk_score)

    if max_risk_score is not None:
        query = query.filter(Assessment.risk_score <= max_risk_score)

    # Framework-specific filtering requires joining with findings
    if framework_category:
        query = (
            query.join(Finding)
            .filter(Finding.framework_category == framework_category)
            .distinct()
        )

    # Get clients for filter dropdown
    clients = Client.query.all()

    # Get assessment types for filter dropdown
    assessment_types = db.session.query(Assessment.assessment_type).distinct().all()
    assessment_types = [at[0] for at in assessment_types if at[0]]

    # Get framework categories for filter dropdown
    framework_categories = db.session.query(Finding.framework_category).distinct().all()
    framework_categories = [fc[0] for fc in framework_categories if fc[0]]

    # Execute query with ordering
    assessments = query.order_by(Assessment.updated_at.desc()).all()

    assessments_data = [a.to_dict() for a in assessments]

    return render_template(
        "risk/list.html",
        assessments=assessments_data,
        clients=clients,
        assessment_types=assessment_types,
        framework_categories=framework_categories,
        filters={
            "client_id": client_id,
            "status": status,
            "assessment_type": assessment_type,
            "framework_category": framework_category,
            "min_risk_score": min_risk_score,
            "max_risk_score": max_risk_score,
        },
    )


@risk_bp.route("/assessments/<int:assessment_id>")
@login_required
def assessment_detail(assessment_id):
    """Display assessment details with framework-specific information"""
    assessment = Assessment.query.get_or_404(assessment_id)

    # Get client information
    client = Client.query.get(assessment.client_id)

    # Get findings with framework-specific categorization
    findings = Finding.query.filter_by(assessment_id=assessment_id).all()

    # Group findings by framework category
    findings_by_category = {}
    for finding in findings:
        category = finding.framework_category or "Uncategorized"
        if category not in findings_by_category:
            findings_by_category[category] = []
        findings_by_category[category].append(finding)

    # Get recommendations
    recommendations = Recommendation.query.filter_by(assessment_id=assessment_id).all()

    # Get framework scores
    framework_scores = assessment.framework_scores or {}

    # Get scoring configuration if available
    scoring_config = None
    if assessment.scoring_config_id:
        scoring_config = ScoringConfiguration.query.get(assessment.scoring_config_id)

    form = AddFindingForm()  # Instantiate the form
    return render_template(
        "risk/assessment_detail.html",
        assessment=assessment,
        client=client,
        findings=findings,
        form=form,
        findings_by_category=findings_by_category,
        recommendations=recommendations,
        framework_scores=framework_scores,
        scoring_config=scoring_config,
    )


@risk_bp.route("/assessments/new", methods=["GET", "POST"])
@login_required
def assessment_new():
    """Create new assessment with framework-specific fields"""
    # Get clients for dropdown
    clients = Client.query.all()

    # Get scoring configurations for dropdown
    scoring_configs = ScoringConfiguration.query.filter_by(is_active=True).all()

    if request.method == "POST":
        # Get form data
        client_id = request.form.get("client_id", type=int)
        name = request.form.get("name")
        description = request.form.get("description")
        assessment_date = request.form.get("assessment_date")
        assessment_type = request.form.get("assessment_type")
        scoring_config_id = request.form.get("scoring_config_id", type=int)

        # Validate required fields (Basic server-side check)
        # Ideally, WTForms validation should handle this more robustly
        if not client_id or not name or not assessment_date:
            flash("Client, name, and assessment date are required", "error")
            # Instantiate form with submitted data to show errors and preserve input
            form = AssessmentForm(request.form)
            form.client_id.choices = [
                (c.id, c.name) for c in clients
            ]  # Repopulate choices
            # Pass assessment_types if needed by template directly
            assessment_types = ["Full Framework", "Targeted Conflict", "Ad-hoc"]
            return render_template(
                "risk/edit.html",
                title="New Risk Assessment",  # Keep title consistent
                form=form,  # Pass the form with errors
                assessment=None,
                # clients=clients, # Not needed if choices set in form
                scoring_configs=scoring_configs,
                assessment_types=assessment_types,  # Pass if needed
            )

        try:
            # Parse assessment date
            assessment_date = datetime.strptime(assessment_date, "%Y-%m-%d").date()

            # Create new assessment
            assessment = Assessment(
                client_id=client_id,
                name=name,
                description=description,
                assessment_date=assessment_date,
                assessment_type=assessment_type,
                methodology="Enhanced Framework v2.0",
                status="draft",
                assigned_user_id=current_user.id,
                scoring_config_id=scoring_config_id,
            )

            db.session.add(assessment)
            db.session.commit()

            # Index in Elasticsearch
            RiskSearchService.index_assessment(assessment)

            flash("Assessment created successfully", "success")
            return redirect(
                url_for("risk.assessment_detail", assessment_id=assessment.id)
            )

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating assessment: {str(e)}", "error")
            # Re-render form with errors if POST fails before redirect
            form = AssessmentForm(
                request.form
            )  # Recreate form with submitted data on error
            form.client_id.choices = [
                (c.id, c.name) for c in clients
            ]  # Repopulate choices

    # GET request or failed POST: Render the form
    if request.method == "GET":
        form = AssessmentForm()  # Create blank form for GET
        # Pre-populate if needed, e.g., form.assessment_date.data = date.today()
    # If POST failed, 'form' is already populated with submitted data and errors

    form.client_id.choices = [(c.id, c.name) for c in clients]
    # Pass assessment_types to the template if the form doesn't handle choices directly
    assessment_types = [
        "Full Framework",
        "Targeted Conflict",
        "Ad-hoc",
    ]  # Or get from config/model

    return render_template(
        "risk/edit.html",
        title="New Risk Assessment",  # Pass title for the template
        form=form,  # Pass the form object
        assessment=None,  # Explicitly None for 'new'
        # clients=clients, # Not needed if choices are set in the form
        scoring_configs=scoring_configs,  # Pass if needed for a dropdown in the template
        assessment_types=assessment_types,  # Pass if needed for a dropdown in the template
    )


@risk_bp.route("/assessments/<int:assessment_id>/edit", methods=["GET", "POST"])
@login_required
def assessment_edit(assessment_id):
    """Edit existing assessment with framework-specific fields"""
    assessment = Assessment.query.get_or_404(assessment_id)

    # Get clients for dropdown
    clients = Client.query.all()

    # Get scoring configurations for dropdown
    scoring_configs = ScoringConfiguration.query.filter_by(is_active=True).all()

    if request.method == "POST":
        # Get form data
        client_id = request.form.get("client_id", type=int)
        name = request.form.get("name")
        description = request.form.get("description")
        assessment_date = request.form.get("assessment_date")
        assessment_type = request.form.get("assessment_type")
        status = request.form.get("status")
        scoring_config_id = request.form.get("scoring_config_id", type=int)

        # Validate required fields (Basic server-side check)
        if not client_id or not name or not assessment_date:
            flash("Client, name, and assessment date are required", "error")
            # Instantiate form with submitted data to show errors and preserve input
            form = EditAssessmentForm(request.form)
            form.client_id.choices = [
                (c.id, c.name) for c in clients
            ]  # Repopulate choices
            # Pass other necessary context
            assessment_types = ["Full Framework", "Targeted Conflict", "Ad-hoc"]
            statuses = ["draft", "in_progress", "review", "complete"]
            return render_template(
                "risk/edit.html",
                title=f"Edit Risk Assessment #{assessment.id}",  # Keep title consistent
                form=form,  # Pass the form with errors
                assessment=assessment,  # Pass original assessment for context if needed
                # clients=clients, # Not needed if choices set in form
                scoring_configs=scoring_configs,
                assessment_types=assessment_types,
                statuses=statuses,
            )

        try:
            # Parse assessment date
            assessment_date = datetime.strptime(assessment_date, "%Y-%m-%d").date()

            # Update assessment
            assessment.client_id = client_id
            assessment.name = name
            assessment.description = description
            assessment.assessment_date = assessment_date
            assessment.assessment_type = assessment_type
            assessment.status = status
            assessment.scoring_config_id = scoring_config_id

            db.session.commit()

            # Recalculate risk score if status is 'complete'
            if status == "complete":
                ScoringService.calculate_assessment_score(assessment.id)

            # Index in Elasticsearch
            RiskSearchService.index_assessment(assessment)

            flash("Assessment updated successfully", "success")
            return redirect(
                url_for("risk.assessment_detail", assessment_id=assessment.id)
            )

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating assessment: {str(e)}", "error")
            # If error during POST commit, re-render form with submitted data
            form = EditAssessmentForm(request.form)
            form.client_id.choices = [
                (c.id, c.name) for c in clients
            ]  # Repopulate choices
            # Fall through to render template below

    # GET request or failed POST commit: Render the form
    if request.method == "GET":
        # Populate form with existing assessment data for GET request
        form = EditAssessmentForm(obj=assessment)
    # If POST failed during commit, 'form' is already populated with submitted data

    form.client_id.choices = [(c.id, c.name) for c in clients]
    # Pass assessment_types and statuses if needed by template directly
    assessment_types = ["Full Framework", "Targeted Conflict", "Ad-hoc"]
    statuses = ["draft", "in_progress", "review", "complete"]

    return render_template(
        "risk/edit.html",
        title=f"Edit Risk Assessment #{assessment.id}",  # Pass title
        form=form,  # Pass the form object
        assessment=assessment,  # Pass assessment for context if needed
        # clients=clients, # Not needed if choices set in form
        scoring_configs=scoring_configs,  # Pass if needed for dropdown
        assessment_types=assessment_types,  # Pass if needed for dropdown
        statuses=statuses,  # Pass if needed for dropdown
    )


@risk_bp.route("/intelligence")
@login_required
def intelligence_feed():
    """Display intelligence feed"""
    return render_template("risk/intelligence.html")


@risk_bp.route("/scenarios")
@login_required
def scenario_list():
    """Display list of risk scenarios"""
    # Placeholder for scenario list retrieval
    scenarios = []
    return render_template("risk/scenarios.html", scenarios=scenarios)


# API Endpoints for Risk Assessment Engine


@risk_bp.route("/api/assessments/<int:assessment_id>/calculate-score", methods=["POST"])
@login_required
def calculate_assessment_score(assessment_id):
    """Calculate risk score for an assessment based on the Enhanced Framework v2.0"""
    assessment = Assessment.query.get_or_404(assessment_id)

    # Check if assessment is in a state where scoring is allowed
    if assessment.status not in ["review", "complete"]:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Assessment must be in review or complete status to calculate score",
                }
            ),
            400,
        )

    # Calculate score
    result = ScoringService.calculate_assessment_score(assessment_id)
    if not result:
        return (
            jsonify(
                {"status": "error", "message": "Error calculating assessment score"}
            ),
            500,
        )

    # Calculate finding scores
    finding_scores = ScoringService.calculate_finding_scores(assessment_id)

    return jsonify(
        {
            "status": "success",
            "message": "Assessment score calculated successfully",
            "data": {
                "assessment_id": assessment_id,
                "overall_score": result["overall_score"],
                "framework_scores": result["framework_scores"],
                "finding_scores": finding_scores,
            },
        }
    )


@risk_bp.route("/api/assessments/<int:assessment_id>/findings", methods=["POST"])
@login_required
def add_finding(assessment_id):
    """Add a finding to an assessment with framework-specific categorization"""
    assessment = Assessment.query.get_or_404(assessment_id)

    # Get request data
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Validate required fields
    required_fields = ["title", "risk_level"]
    for field in required_fields:
        if field not in data:
            return (
                jsonify(
                    {"status": "error", "message": f"Missing required field: {field}"}
                ),
                400,
            )

    try:
        # Create new finding
        finding = Finding(
            assessment_id=assessment_id,
            title=data["title"],
            description=data.get("description"),
            risk_level=data["risk_level"],
            likelihood=data.get("likelihood"),
            impact=data.get("impact"),
            asset_id=data.get("asset_id"),
            evidence=data.get("evidence"),
            framework_category=data.get("framework_category"),
            attack_type=data.get("attack_type"),
            connection_type_id=data.get("connection_type_id"),
            conflict_id=data.get("conflict_id"),
            actor_id=data.get("actor_id"),
            status="open",
        )

        db.session.add(finding)
        db.session.commit()

        # Index assessment in Elasticsearch
        RiskSearchService.index_assessment(assessment)

        return jsonify(
            {
                "status": "success",
                "message": "Finding added successfully",
                "data": {"finding_id": finding.id},
            }
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"status": "error", "message": f"Error adding finding: {str(e)}"}),
            500,
        )


@risk_bp.route("/api/findings/<int:finding_id>/recommendations", methods=["POST"])
@login_required
def add_recommendation(finding_id):
    """Add a recommendation to a finding"""
    finding = Finding.query.get_or_404(finding_id)

    # Get request data
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Validate required fields
    required_fields = ["title", "priority"]
    for field in required_fields:
        if field not in data:
            return (
                jsonify(
                    {"status": "error", "message": f"Missing required field: {field}"}
                ),
                400,
            )

    try:
        # Create new recommendation
        recommendation = Recommendation(
            assessment_id=finding.assessment_id,
            finding_id=finding_id,
            title=data["title"],
            description=data.get("description"),
            priority=data["priority"],
            implementation_cost=data.get("implementation_cost"),
            implementation_time=data.get("implementation_time"),
            status="open",
            assigned_user_id=data.get("assigned_user_id"),
        )

        db.session.add(recommendation)
        db.session.commit()

        # Index assessment in Elasticsearch
        assessment = Assessment.query.get(finding.assessment_id)
        RiskSearchService.index_assessment(assessment)

        return jsonify(
            {
                "status": "success",
                "message": "Recommendation added successfully",
                "data": {"recommendation_id": recommendation.id},
            }
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {"status": "error", "message": f"Error adding recommendation: {str(e)}"}
            ),
            500,
        )


@risk_bp.route("/api/assessments/<int:assessment_id>/report", methods=["GET"])
@login_required
def generate_assessment_report_api(assessment_id):
    """Generate and return an assessment report (HTML or PDF)"""
    assessment = Assessment.query.get_or_404(assessment_id)
    report_format = request.args.get("format", "html").lower()

    if report_format not in ["html", "pdf"]:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": 'Invalid report format requested. Use "html" or "pdf".',
                }
            ),
            400,
        )

    report_content = ReportService.generate_assessment_report(
        assessment, format=report_format
    )

    if report_content is None:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to generate {report_format.upper()} report for assessment {assessment_id}",
                }
            ),
            500,
        )

    if report_format == "pdf":
        # Set headers for PDF download
        headers = {
            "Content-Disposition": f"attachment;filename=assessment_{assessment_id}_report.pdf"
        }
        return Response(report_content, mimetype="application/pdf", headers=headers)
    else:  # HTML
        # Return HTML directly
        return Response(report_content, mimetype="text/html")
