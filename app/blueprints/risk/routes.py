"""
Routes for risk assessment blueprint
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, Response
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
from datetime import datetime, timezone
import json
import logging


logger = logging.getLogger(__name__)


# Helper function for standardized API responses
def _make_api_response(
    status, data=None, error_code=None, error_message=None, error_details=None
):
    """Helper function to create standardized API responses."""
    response_payload = {
        "status": status,
        "data": data if status == "success" else None,
        "error": None,
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
    }
    status_code = 200  # Default to 200 OK
    if status == "error":
        response_payload["error"] = {
            "code": error_code or "UNKNOWN_ERROR",
            "message": error_message or "An unexpected error occurred.",
            "details": (
                str(error_details) if error_details else None
            ),  # Ensure details are stringified
        }
        # Basic status code mapping based on common error types
        if error_code == "BAD_REQUEST":
            status_code = 400
        elif error_code == "NOT_FOUND":
            status_code = 404
        elif error_code == "UNAUTHORIZED":
            status_code = 401
        elif error_code == "FORBIDDEN":
            status_code = 403
        else:  # Default server error
            status_code = 500

    return jsonify(response_payload), status_code


@risk_bp.route("/dashboard")
def _build_assessment_query(
    client_id=None,
    status=None,
    assessment_type=None,
    framework_category=None,
    min_risk_score=None,
    max_risk_score=None,
):
    """Builds a base query for assessments with common filters."""
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

    return query


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

    # Build query using helper function
    query = _build_assessment_query(
        client_id=client_id,
        status=status,
        assessment_type=assessment_type,
        framework_category=framework_category,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
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
        "list.html",
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
                "edit.html",
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

    context = {
        "title": "New Risk Assessment",
        "form": form,
        "assessment": None,
        "clients": clients,
        "scoring_configs": scoring_configs,
        "assessment_types": assessment_types,
        "statuses": ["draft", "in_progress", "review", "complete"],
    }
    logger.debug(
        f"Rendering edit.html for new assessment with context keys: {list(context.keys())}"
    )  # Log context keys
    # logger.debug(f"Rendering edit.html for new assessment with full context: {context}") # Optional: Log full context if needed, might be large

    return render_template("edit.html", **context)


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
                "edit.html",
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
        "edit.html",
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
    return render_template("intelligence.html")


@risk_bp.route("/scenarios")
@login_required
def scenario_list():
    """Display list of risk scenarios"""
    # Placeholder for scenario list retrieval
    scenarios = []
    return render_template("scenarios.html", scenarios=scenarios)


# API Endpoints for Risk Assessment Engine


@risk_bp.route("/api/v1/risk-assessments/", methods=["GET"])
@login_required
def list_assessments_api():
    """
    List risk assessments with filtering options.

    Query Parameters:
        client_id (int): Filter by client ID.
        status (str): Filter by assessment status.
        assessment_type (str): Filter by assessment type.
        framework_category (str): Filter assessments containing findings with this category.
        min_risk_score (float): Filter by minimum risk score.
        max_risk_score (float): Filter by maximum risk score.
        sort_by (str): Field to sort by (e.g., 'updated_at', 'risk_score'). Default 'updated_at'.
        sort_order (str): Sort order ('asc' or 'desc'). Default 'desc'.
        page (int): Page number for pagination. Default 1.
        per_page (int): Items per page. Default 20.

    Returns:
        JSON response with a list of assessments and pagination metadata.
    """
    try:
        # Get filter and pagination parameters
        client_id = request.args.get("client_id", type=int)
        status = request.args.get("status")
        assessment_type = request.args.get("assessment_type")
        framework_category = request.args.get("framework_category")
        min_risk_score = request.args.get("min_risk_score", type=float)
        max_risk_score = request.args.get("max_risk_score", type=float)
        sort_by = request.args.get("sort_by", "updated_at")
        sort_order = request.args.get("sort_order", "desc")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Build query using helper function
        query = _build_assessment_query(
            client_id=client_id,
            status=status,
            assessment_type=assessment_type,
            framework_category=framework_category,
            min_risk_score=min_risk_score,
            max_risk_score=max_risk_score,
        )

        # Sorting
        sort_column = getattr(Assessment, sort_by, Assessment.updated_at)
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        logger.debug(
            f"Assessment query built. Total items before pagination: {query.count()}"
        )

        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.debug(f"Paginating query: page={page}, per_page={per_page}")

        assessments = pagination.items
        assessments_data = [assessment.to_dict() for assessment in assessments]
        logger.debug(
            f"Pagination result: {len(assessments)} items on page {pagination.page} of {pagination.pages} (Total: {pagination.total})"
        )

        return _make_api_response(
            "success",
            data={
                "assessments": assessments_data,
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total_pages": pagination.pages,
                    "total_items": pagination.total,
                },
            },
        )

    except Exception as e:
        logger.error(f"Error listing assessments: {str(e)}", exc_info=True)
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while listing assessments.",
            error_details=e,
        )


@risk_bp.route("/api/v1/risk-assessments", methods=["POST"])
@login_required
def create_assessment_api():
    """
    Create a new risk assessment via API.

    Expects JSON payload with assessment details.
    """
    data = request.get_json()
    if not data:
        return _make_api_response(
            "error", error_code="BAD_REQUEST", error_message="No input data provided"
        )

    # Basic validation (consider using Marshmallow or WTForms for robust validation)
    required_fields = ["client_id", "name", "assessment_date", "assessment_type"]
    missing_fields = [
        field for field in required_fields if field not in data or not data[field]
    ]
    if missing_fields:
        return _make_api_response(
            "error",
            error_code="BAD_REQUEST",
            error_message=f"Missing required fields: {', '.join(missing_fields)}",
        )

    try:
        # Parse assessment date
        assessment_date = datetime.strptime(data["assessment_date"], "%Y-%m-%d").date()

        # Create new assessment
        assessment = Assessment(
            client_id=data["client_id"],
            name=data["name"],
            description=data.get("description"),
            assessment_date=assessment_date,
            assessment_type=data["assessment_type"],
            methodology=data.get(
                "methodology", "Enhanced Framework v2.0"
            ),  # Default if not provided
            status=data.get("status", "draft"),  # Default to draft
            assigned_user_id=current_user.id,  # Assign to current user
            scoring_config_id=data.get("scoring_config_id"),
        )

        db.session.add(assessment)
        db.session.commit()
        logger.info(f"Assessment {assessment.id} created successfully via API.")

        # Index in Elasticsearch
        try:
            RiskSearchService.index_assessment(assessment)
            logger.info(f"Assessment {assessment.id} indexed successfully.")
        except Exception as es_err:
            logger.error(
                f"Error indexing assessment {assessment.id}: {es_err}", exc_info=True
            )
            # Decide if failure to index should prevent success response - currently it doesn't

        # Return success response with the created assessment data (including ID)
        return _make_api_response("success", data=assessment.to_dict())

    except ValueError as ve:
        db.session.rollback()
        logger.error(f"Value error creating assessment: {ve}", exc_info=True)
        return _make_api_response(
            "error",
            error_code="BAD_REQUEST",
            error_message=f"Invalid data format: {ve}",
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating assessment via API: {e}", exc_info=True)
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="Failed to create assessment.",
            error_details=str(e),
        )


@risk_bp.route("/api/v1/risk-assessments/<int:assessment_id>", methods=["GET"])
@login_required
def get_assessment_detail_api(assessment_id):
    """
    Retrieve details for a single risk assessment.

    Includes associated findings and recommendations.

    Args:
        assessment_id: The ID of the assessment to retrieve.

    Returns:
        JSON response with assessment details.
    """
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return _make_api_response(
                "error",
                error_code="NOT_FOUND",
                error_message=f"Assessment with ID {assessment_id} not found.",
            )

        assessment_data = assessment.to_dict()
        # Eagerly load findings and recommendations
        assessment_data["findings"] = [
            finding.to_dict() for finding in assessment.findings
        ]
        assessment_data["recommendations"] = [
            rec.to_dict() for rec in assessment.recommendations
        ]

        return _make_api_response("success", data=assessment_data)

    except Exception as e:
        logger.error(
            f"Error retrieving assessment {assessment_id}: {str(e)}", exc_info=True
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while retrieving the assessment.",
            error_details=e,
        )


@risk_bp.route("/api/v1/risk-assessments/<int:assessment_id>", methods=["PUT"])
@login_required
def update_assessment_api(assessment_id):
    """
    Update details for a single risk assessment.

    Allows updating fields like name, description, status, etc.

    Args:
        assessment_id: The ID of the assessment to update.

    Request Body (JSON):
        Fields to update (e.g., name, description, status, assessment_type, scoring_config_id).

    Returns:
        JSON response with the updated assessment details.
    """
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return _make_api_response(
            "error",
            error_code="NOT_FOUND",
            error_message=f"Assessment with ID {assessment_id} not found.",
        )

    data = request.json
    if not data:
        return _make_api_response(
            "error", error_code="BAD_REQUEST", error_message="No data provided"
        )

    # Fields allowed for update via API
    allowed_fields = [
        "name",
        "description",
        "status",
        "assessment_type",
        "scoring_config_id",
        "assessment_date",
    ]
    updated = False

    try:
        original_status = (
            assessment.status
        )  # Store original status before potential update

        for field in allowed_fields:
            if field in data:
                # Special handling for date parsing
                if field == "assessment_date":
                    try:
                        date_value = datetime.strptime(data[field], "%Y-%m-%d").date()
                        setattr(assessment, field, date_value)
                        updated = True
                    except (
                        ValueError,
                        TypeError,
                    ):  # Catch TypeError if data[field] is not string
                        return _make_api_response(
                            "error",
                            error_code="BAD_REQUEST",
                            error_message=f"Invalid date format for assessment_date. Use YYYY-MM-DD.",
                        )
                else:
                    setattr(assessment, field, data[field])
                    updated = True

        if not updated:
            return _make_api_response(
                "error",
                error_code="BAD_REQUEST",
                error_message="No valid fields provided for update.",
            )

        # Recalculate score if status changed to 'complete'
        if (
            "status" in data
            and data["status"] == "complete"
            and original_status != "complete"
        ):
            ScoringService.calculate_assessment_score(
                assessment.id
            )  # Recalculate score

        db.session.commit()

        # Index updated assessment in Elasticsearch
        try:
            RiskSearchService.index_assessment(assessment)
        except Exception as es_error:
            logger.error(
                f"Failed to index assessment {assessment_id} after update: {es_error}",
                exc_info=True,
            )
            # Non-critical error

        return _make_api_response("success", data=assessment.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Error updating assessment {assessment_id}: {str(e)}", exc_info=True
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while updating the assessment.",
            error_details=e,
        )


@risk_bp.route(
    "/api/v1/risk-assessments/<int:assessment_id>/calculate-score", methods=["POST"]
)
@login_required
def calculate_assessment_score(assessment_id):
    """Calculate risk score for an assessment based on the Enhanced Framework v2.0"""
    assessment = Assessment.query.get_or_404(assessment_id)

    # Check if assessment is in a state where scoring is allowed
    if assessment.status not in ["review", "complete"]:
        return _make_api_response(
            "error",
            error_code="BAD_REQUEST",
            error_message="Assessment must be in review or complete status to calculate score",
        )

    # Calculate score
    try:
        result = ScoringService.calculate_assessment_score(assessment_id)
        if not result:
            # This case might indicate an issue within the service logic not raising an exception
            logger.warning(
                f"ScoringService.calculate_assessment_score returned None for assessment {assessment_id}"
            )
            return _make_api_response(
                "error",
                error_code="CALCULATION_FAILED",
                error_message="Assessment score calculation failed unexpectedly.",
            )

        # Calculate finding scores
        finding_scores = ScoringService.calculate_finding_scores(assessment_id)

        return _make_api_response(
            "success",
            data={
                "assessment_id": assessment_id,
                "overall_score": result["overall_score"],
                "framework_scores": result["framework_scores"],
                "finding_scores": finding_scores,
            },
        )
    except Exception as e:
        logger.error(
            f"Error calculating score for assessment {assessment_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred during score calculation.",
            error_details=e,
        )


@risk_bp.route("/api/v1/risk-assessments/<int:assessment_id>/findings", methods=["GET"])
@login_required
def list_findings_api(assessment_id):
    """
    List findings for a specific risk assessment.

    Args:
        assessment_id: The ID of the assessment.

    Returns:
        JSON response with a list of findings.
    """
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return _make_api_response(
            "error",
            error_code="NOT_FOUND",
            error_message=f"Assessment with ID {assessment_id} not found.",
        )

    try:
        # Add filtering/sorting/pagination later if needed
        findings = (
            Finding.query.filter_by(assessment_id=assessment_id)
            .order_by(Finding.created_at.desc())
            .all()
        )
        findings_data = [finding.to_dict() for finding in findings]

        return _make_api_response("success", data={"findings": findings_data})

    except Exception as e:
        logger.error(
            f"Error listing findings for assessment {assessment_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while listing findings.",
            error_details=e,
        )


@risk_bp.route("/api/v1/findings/<int:finding_id>", methods=["GET"])
@login_required
def get_finding_detail_api(finding_id):
    """
    Retrieve details for a single finding.

    Includes associated recommendations.

    Args:
        finding_id: The ID of the finding to retrieve.

    Returns:
        JSON response with finding details.
    """
    try:
        finding = Finding.query.get(finding_id)
        if not finding:
            return _make_api_response(
                "error",
                error_code="NOT_FOUND",
                error_message=f"Finding with ID {finding_id} not found.",
            )

        finding_data = finding.to_dict()
        # Eagerly load recommendations
        finding_data["recommendations"] = [
            rec.to_dict() for rec in finding.recommendations
        ]

        return _make_api_response("success", data=finding_data)

    except Exception as e:
        logger.error(f"Error retrieving finding {finding_id}: {str(e)}", exc_info=True)
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while retrieving the finding.",
            error_details=e,
        )


@risk_bp.route("/api/v1/findings/<int:finding_id>", methods=["PUT"])
@login_required
def update_finding_api(finding_id):
    """
    Update details for a single finding.

    Allows updating fields like title, description, status, risk_level, etc.

    Args:
        finding_id: The ID of the finding to update.

    Request Body (JSON):
        Fields to update.

    Returns:
        JSON response with the updated finding details.
    """
    finding = Finding.query.get(finding_id)
    if not finding:
        return _make_api_response(
            "error",
            error_code="NOT_FOUND",
            error_message=f"Finding with ID {finding_id} not found.",
        )

    data = request.json
    if not data:
        return _make_api_response(
            "error", error_code="BAD_REQUEST", error_message="No data provided"
        )

    # Fields allowed for update via API
    allowed_fields = [
        "title",
        "description",
        "risk_level",
        "likelihood",
        "impact",
        "asset_id",
        "evidence",
        "framework_category",
        "attack_type",
        "connection_type_id",
        "conflict_id",
        "actor_id",
        "status",
    ]
    updated = False

    try:
        for field in allowed_fields:
            if field in data:
                # Add validation if necessary (e.g., for status values)
                setattr(finding, field, data[field])
                updated = True

        if not updated:
            return _make_api_response(
                "error",
                error_code="BAD_REQUEST",
                error_message="No valid fields provided for update.",
            )

        db.session.commit()

        # Index the parent assessment in Elasticsearch as finding is nested
        try:
            assessment = Assessment.query.get(finding.assessment_id)
            if assessment:
                RiskSearchService.index_assessment(assessment)
            else:
                logger.warning(
                    f"Could not find assessment {finding.assessment_id} to re-index after updating finding {finding.id}"
                )
        except Exception as es_error:
            logger.error(
                f"Failed to index assessment {finding.assessment_id} after updating finding {finding.id}: {es_error}",
                exc_info=True,
            )
            # Non-critical error

        return _make_api_response("success", data=finding.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating finding {finding_id}: {str(e)}", exc_info=True)
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while updating the finding.",
            error_details=e,
        )


@risk_bp.route("/api/v1/findings/<int:finding_id>/recommendations", methods=["GET"])
@login_required
def list_recommendations_api(finding_id):
    """
    List recommendations for a specific finding.

    Args:
        finding_id: The ID of the finding.

    Returns:
        JSON response with a list of recommendations.
    """
    finding = Finding.query.get(finding_id)
    if not finding:
        return _make_api_response(
            "error",
            error_code="NOT_FOUND",
            error_message=f"Finding with ID {finding_id} not found.",
        )

    try:
        # Add filtering/sorting/pagination later if needed
        recommendations = (
            Recommendation.query.filter_by(finding_id=finding_id)
            .order_by(Recommendation.created_at.desc())
            .all()
        )
        recommendations_data = [rec.to_dict() for rec in recommendations]

        return _make_api_response(
            "success", data={"recommendations": recommendations_data}
        )

    except Exception as e:
        logger.error(
            f"Error listing recommendations for finding {finding_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while listing recommendations.",
            error_details=e,
        )


@risk_bp.route("/api/v1/recommendations/<int:recommendation_id>", methods=["GET"])
@login_required
def get_recommendation_detail_api(recommendation_id):
    """
    Retrieve details for a single recommendation.

    Args:
        recommendation_id: The ID of the recommendation to retrieve.

    Returns:
        JSON response with recommendation details.
    """
    try:
        recommendation = Recommendation.query.get(recommendation_id)
        if not recommendation:
            return _make_api_response(
                "error",
                error_code="NOT_FOUND",
                error_message=f"Recommendation with ID {recommendation_id} not found.",
            )

        return _make_api_response("success", data=recommendation.to_dict())

    except Exception as e:
        logger.error(
            f"Error retrieving recommendation {recommendation_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while retrieving the recommendation.",
            error_details=e,
        )


@risk_bp.route("/api/v1/recommendations/<int:recommendation_id>", methods=["PUT"])
@login_required
def update_recommendation_api(recommendation_id):
    """
    Update details for a single recommendation.

    Allows updating fields like title, description, status, priority, etc.

    Args:
        recommendation_id: The ID of the recommendation to update.

    Request Body (JSON):
        Fields to update.

    Returns:
        JSON response with the updated recommendation details.
    """
    recommendation = Recommendation.query.get(recommendation_id)
    if not recommendation:
        return _make_api_response(
            "error",
            error_code="NOT_FOUND",
            error_message=f"Recommendation with ID {recommendation_id} not found.",
        )

    data = request.json
    if not data:
        return _make_api_response(
            "error", error_code="BAD_REQUEST", error_message="No data provided"
        )

    # Fields allowed for update via API
    allowed_fields = [
        "title",
        "description",
        "priority",
        "implementation_cost",
        "implementation_time",
        "status",
        "assigned_user_id",
    ]
    updated = False

    try:
        for field in allowed_fields:
            if field in data:
                # Add validation if necessary (e.g., for status values)
                setattr(recommendation, field, data[field])
                updated = True

        if not updated:
            return _make_api_response(
                "error",
                error_code="BAD_REQUEST",
                error_message="No valid fields provided for update.",
            )

        db.session.commit()

        # Index the parent assessment in Elasticsearch as recommendation is nested
        try:
            assessment = Assessment.query.get(recommendation.assessment_id)
            if assessment:
                RiskSearchService.index_assessment(assessment)
            else:
                logger.warning(
                    f"Could not find assessment {recommendation.assessment_id} to re-index after updating recommendation {recommendation.id}"
                )
        except Exception as es_error:
            logger.error(
                f"Failed to index assessment {recommendation.assessment_id} after updating recommendation {recommendation.id}: {es_error}",
                exc_info=True,
            )
            # Non-critical error

        return _make_api_response("success", data=recommendation.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Error updating recommendation {recommendation_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while updating the recommendation.",
            error_details=e,
        )


@risk_bp.route(
    "/api/v1/risk-assessments/<int:assessment_id>/findings", methods=["POST"]
)
@login_required
def add_finding(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)

    # Get request data
    data = request.json
    if not data:
        return _make_api_response(
            "error", error_code="BAD_REQUEST", error_message="No data provided"
        )

    # Validate required fields
    required_fields = ["title", "risk_level"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return _make_api_response(
            "error",
            error_code="BAD_REQUEST",
            error_message=f"Missing required fields: {', '.join(missing_fields)}",
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

        # Index assessment in Elasticsearch (consider if this should be async)
        try:
            RiskSearchService.index_assessment(assessment)
        except Exception as es_error:
            logger.error(
                f"Failed to index assessment {assessment_id} after adding finding {finding.id}: {es_error}",
                exc_info=True,
            )
            # Non-critical error, proceed with success response but log it

        return _make_api_response("success", data={"finding_id": finding.id})

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Error adding finding to assessment {assessment_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while adding the finding.",
            error_details=e,
        )


@risk_bp.route("/api/v1/findings/<int:finding_id>/recommendations", methods=["POST"])
@login_required
def add_recommendation(finding_id):
    """Add a recommendation to a finding"""
    finding = Finding.query.get_or_404(finding_id)

    # Get request data
    data = request.json
    if not data:
        return _make_api_response(
            "error", error_code="BAD_REQUEST", error_message="No data provided"
        )

    # Validate required fields
    required_fields = ["title", "priority"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return _make_api_response(
            "error",
            error_code="BAD_REQUEST",
            error_message=f"Missing required fields: {', '.join(missing_fields)}",
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

        # Index assessment in Elasticsearch (consider if this should be async)
        try:
            assessment = Assessment.query.get(finding.assessment_id)
            if assessment:
                RiskSearchService.index_assessment(assessment)
            else:
                logger.warning(
                    f"Could not find assessment {finding.assessment_id} to re-index after adding recommendation {recommendation.id}"
                )
        except Exception as es_error:
            logger.error(
                f"Failed to index assessment {finding.assessment_id} after adding recommendation {recommendation.id}: {es_error}",
                exc_info=True,
            )
            # Non-critical error, proceed with success response but log it

        return _make_api_response(
            "success", data={"recommendation_id": recommendation.id}
        )

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Error adding recommendation to finding {finding_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred while adding the recommendation.",
            error_details=e,
        )


@risk_bp.route("/api/v1/risk-assessments/<int:assessment_id>/report", methods=["GET"])
@login_required
def generate_assessment_report_api(assessment_id):
    """Generate and return an assessment report (HTML or PDF)"""
    assessment = Assessment.query.get_or_404(assessment_id)
    report_format = request.args.get("format", "html").lower()

    if report_format not in ["html", "pdf"]:
        return _make_api_response(
            "error",
            error_code="BAD_REQUEST",
            error_message='Invalid report format requested. Use "html" or "pdf".',
        )

    try:
        report_content = ReportService.generate_assessment_report(
            assessment, format=report_format
        )

        if report_content is None:
            # This indicates an issue within the ReportService
            logger.error(
                f"ReportService.generate_assessment_report returned None for assessment {assessment_id}, format {report_format}"
            )
            return _make_api_response(
                "error",
                error_code="REPORT_GENERATION_FAILED",
                error_message=f"Failed to generate {report_format.upper()} report.",
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
    except Exception as e:
        logger.error(
            f"Error generating report for assessment {assessment_id}: {str(e)}",
            exc_info=True,
        )
        return _make_api_response(
            "error",
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An internal error occurred during report generation.",
            error_details=e,
        )
