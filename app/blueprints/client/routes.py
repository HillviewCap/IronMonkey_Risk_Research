from flask import (
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
)
from flask_login import login_required
import json  # For handling JSON fields

from app import db  # Import db instance
from app.services.client_service import (
    search_clients,
    create_client_with_details,
    get_client_by_id,
)
from .forms import (
    ClientOnboardingForm,
    ClientEditForm,
    LocationForm,
    ContactForm,
    AssetForm,
)  # Import new forms
from . import client_bp
from app.models.client import (
    Client,
    ClientLocation,
    ClientContact,
    ClientAsset,
)  # Import models
from app.models.framework import IndustryProfile  # Import IndustryProfile


@client_bp.route("/api/v1/clients/search", methods=["GET"])
@login_required
def client_search():
    query = request.args.get("query")
    industry = request.args.get("industry")
    country = request.args.get("country")
    results = search_clients(query, industry, country)
    return jsonify(
        {
            "status": "success",
            "data": results,
            "meta": {"total": len(results), "page": 1, "per_page": 10},
        }
    )


@client_bp.route("/clients", methods=["GET"])
@login_required
def client_landing():
    """Display a landing page with a list of clients, optionally filtered by search."""
    query = request.args.get("query", "")
    industry_filter = request.args.get("industry", "")
    country_filter = request.args.get("country", "")

    # Fetch clients using the search service
    clients = search_clients(query, industry_filter, country_filter)

    # Fetch choices for dropdowns
    try:
        industries_query = IndustryProfile.query.order_by(
            IndustryProfile.category, IndustryProfile.industry
        ).all()
        industry_choices = [("", "-- All Industries --")] + [
            (ind.industry, f"{ind.category}: {ind.industry}")
            for ind in industries_query
        ]
    except Exception as e:
        current_app.logger.error(
            f"Failed to load industries for client landing search: {e}", exc_info=True
        )
        industry_choices = [("", "Error loading industries")]

    country_choices = current_app.config.get(
        "COUNTRIES", [("", "Error loading countries")]
    )
    # Ensure the format is (value, label) and add an "All" option
    if country_choices and isinstance(country_choices[0], tuple):
        country_choices = [("", "-- All Countries --")] + country_choices
    else:  # Handle potential simple list format
        country_choices = [("", "-- All Countries --")] + [
            (c, c) for c in country_choices
        ]

    return render_template(
        "client/landing.html",
        title="Clients",
        clients=clients,
        industry_choices=industry_choices,
        country_choices=country_choices,
        search_query=query,
        search_industry=industry_filter,
        search_country=country_filter,
    )


@client_bp.route("/clients/onboard", methods=["GET", "POST"])
@login_required
def onboard_client():
    """Handle client onboarding form display and submission."""
    form = ClientOnboardingForm()

    # Populate dynamic choices
    try:
        # Query industries and format for SelectField: (value, label)
        industries = IndustryProfile.query.order_by(
            IndustryProfile.category, IndustryProfile.industry
        ).all()
        form.industry.choices = [("", "-- Select Industry --")] + [
            (ind.industry, f"{ind.category}: {ind.industry}") for ind in industries
        ]
    except Exception as e:
        # Log the error and provide a fallback choice
        current_app.logger.error(
            f"Failed to load industries for onboarding form: {e}", exc_info=True
        )
        form.industry.choices = [("", "Error loading industries")]

    # Load countries from config
    form.location_country.choices = current_app.config.get(
        "COUNTRIES", [("", "Error loading countries")]
    )

    if form.validate_on_submit():
        # Extract data from the form
        form_data = form.data
        # Call the service function to create the client
        new_client = create_client_with_details(form_data)
        if new_client:
            flash(f'Client "{new_client.name}" onboarded successfully!', "success")
            # Redirect to the new client's detail page
            return redirect(url_for("client.client_detail", client_id=new_client.id))
        else:
            flash(
                "Error onboarding client. Please check the logs or try again.", "danger"
            )

    # For GET request or if form validation fails
    return render_template(
        "client/onboard_client.html", title="Onboard New Client", form=form
    )


@client_bp.route("/clients/<int:client_id>")
@login_required
def client_detail(client_id):
    """Display the details for a specific client."""
    client = get_client_by_id(client_id)
    if not client:
        abort(404)  # Not found

    # Fetch related data
    locations = client.locations.order_by(ClientLocation.name).all()
    contacts = client.contacts.order_by(
        ClientContact.last_name, ClientContact.first_name
    ).all()
    assets = client.assets.order_by(ClientAsset.name).all()

    # Pass client and related data to the template
    return render_template(
        "client/client_detail.html",
        title=f"Client: {client.name}",
        client=client,
        locations=locations,
        contacts=contacts,
        assets=assets,
    )


@client_bp.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    """Handle editing of core client details."""
    client = Client.query.get_or_404(client_id)
    form = ClientEditForm(obj=client)  # Pre-populate form with client data on GET

    # Populate dynamic choices
    try:
        industries = IndustryProfile.query.order_by(
            IndustryProfile.category, IndustryProfile.industry
        ).all()
        form.industry.choices = [("", "-- Select Industry --")] + [
            (ind.industry, f"{ind.category}: {ind.industry}") for ind in industries
        ]
    except Exception as e:
        current_app.logger.error(
            f"Failed to load industries for edit form: {e}", exc_info=True
        )
        form.industry.choices = [("", "Error loading industries")]

    if form.validate_on_submit():
        try:
            client.name = form.name.data
            client.industry = form.industry.data
            client.website = form.website.data
            client.description = form.description.data
            client.public_profile_summary = form.public_profile_summary.data

            # Handle competitors - attempt JSON parsing, fallback to simple list if needed
            competitors_raw = form.competitors.data
            if competitors_raw:
                try:
                    # Try parsing as JSON list
                    parsed_competitors = json.loads(competitors_raw)
                    if isinstance(parsed_competitors, list):
                        client.competitors = parsed_competitors
                    else:
                        # If JSON but not a list, wrap it in a list
                        client.competitors = [parsed_competitors]
                except json.JSONDecodeError:
                    # If not valid JSON, treat as comma-separated string
                    client.competitors = [
                        c.strip() for c in competitors_raw.split(",") if c.strip()
                    ]
            else:
                client.competitors = None  # Clear if field is empty

            db.session.commit()
            flash("Client details updated successfully!", "success")
            return redirect(url_for("client.client_detail", client_id=client.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error updating client {client_id}: {e}", exc_info=True
            )
            flash("Error updating client details. Please check logs.", "danger")

    # For GET request or if validation fails, render the edit form
    # Need to create this template next
    return render_template(
        "client/edit_client.html",
        title=f"Edit Client: {client.name}",
        form=form,
        client=client,
    )


# --- Location Management Routes --- #


@client_bp.route("/clients/<int:client_id>/locations/add", methods=["GET", "POST"])
@login_required
def add_location(client_id):
    """Handle adding a new location for a client."""
    client = Client.query.get_or_404(client_id)
    form = LocationForm()

    # Load countries from config
    form.country.choices = current_app.config.get(
        "COUNTRIES", [("", "Error loading countries")]
    )

    if form.validate_on_submit():
        try:
            new_location = ClientLocation(
                client_id=client.id,
                name=form.name.data,
                location_type=form.location_type.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                country=form.country.data,
                postal_code=form.postal_code.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
            )
            db.session.add(new_location)
            db.session.commit()
            flash("Location added successfully!", "success")
            return redirect(url_for("client.client_detail", client_id=client.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error adding location for client {client_id}: {e}", exc_info=True
            )
            flash("Error adding location. Please check logs.", "danger")
            # Re-render form on exception during POST
            return render_template(
                "client/location_form.html",
                title="Add New Location",
                form=form,
                client=client,
            )

    # Handle GET request or failed validation
    return render_template(
        "client/location_form.html", title="Add New Location", form=form, client=client
    )


@client_bp.route(
    "/clients/<int:client_id>/locations/<int:location_id>/edit", methods=["GET", "POST"]
)
@login_required
def edit_location(client_id, location_id):
    """Handle editing an existing location for a client."""
    location = ClientLocation.query.filter_by(
        id=location_id, client_id=client_id
    ).first_or_404()
    client = location.client  # Get client from relationship
    form = LocationForm(obj=location)  # Pre-populate form

    # Load countries from config
    form.country.choices = current_app.config.get(
        "COUNTRIES", [("", "Error loading countries")]
    )

    if form.validate_on_submit():
        try:
            location.name = form.name.data
            location.location_type = form.location_type.data
            location.address = form.address.data
            location.city = form.city.data
            location.state = form.state.data
            location.country = form.country.data
            location.postal_code = form.postal_code.data
            location.latitude = form.latitude.data
            location.longitude = form.longitude.data
            db.session.commit()
            flash("Location updated successfully!", "success")
            return redirect(url_for("client.client_detail", client_id=client.id))
        except Exception as e:
            db.session.rollback()
            # Log the detailed error internally
            current_app.logger.error(
                f"Error updating location {location_id} for client {client_id}: {e}",
                exc_info=True,
            )
            # Flash a user-friendly message
            flash(
                "Error updating location. Please check the details and try again.",
                "danger",
            )
            # Re-render the form so the user can correct errors
            return render_template(
                "client/location_form.html",
                title="Edit Location",
                form=form,
                client=client,
                location=location,
            )

    # Handle GET request or failed validation by rendering the form
    return render_template(
        "client/location_form.html",
        title="Edit Location",
        form=form,
        client=client,
        location=location,
    )


@client_bp.route(
    "/clients/<int:client_id>/locations/<int:location_id>/delete", methods=["POST"]
)
@login_required
def delete_location(client_id, location_id):
    """Handle deleting a location for a client."""
    location = ClientLocation.query.filter_by(
        id=location_id, client_id=client_id
    ).first_or_404()
    try:
        # Check if any assets are linked to this location - prevent deletion if so?
        # For now, allow deletion. Consider adding a check later if needed.
        # assets_linked = ClientAsset.query.filter_by(location_id=location.id).count()
        # if assets_linked > 0:
        #     flash(f'Cannot delete location "{location.name}" as it has {assets_linked} asset(s) linked to it.', 'warning')
        #     return redirect(url_for('client.client_detail', client_id=client_id))

        db.session.delete(location)
        db.session.commit()
        flash(f'Location "{location.name}" deleted successfully!', "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error deleting location {location_id} for client {client_id}: {e}",
            exc_info=True,
        )
        flash("Error deleting location. Please check logs.", "danger")


# --- Contact Management Routes --- #


@client_bp.route("/clients/<int:client_id>/contacts/add", methods=["GET", "POST"])
@login_required
def add_contact(client_id):
    """Handle adding a new contact for a client."""
    client = Client.query.get_or_404(client_id)
    form = ContactForm()

    if form.validate_on_submit():
        try:
            new_contact = ClientContact(
                client_id=client.id,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                position=form.position.data,
                notes=form.notes.data,
                is_primary=form.is_primary.data,
            )
            db.session.add(new_contact)
            db.session.commit()
            flash("Contact added successfully!", "success")
            return redirect(url_for("client.client_detail", client_id=client.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error adding contact for client {client_id}: {e}", exc_info=True
            )
            flash("Error adding contact. Please check logs.", "danger")
            # Re-render form on exception during POST
            return render_template(
                "client/contact_form.html",
                title="Add New Contact",
                form=form,
                client=client,
            )

    # Handle GET request or failed validation
    return render_template(
        "client/contact_form.html", title="Add New Contact", form=form, client=client
    )


@client_bp.route(
    "/clients/<int:client_id>/contacts/<int:contact_id>/edit", methods=["GET", "POST"]
)
@login_required
def edit_contact(client_id, contact_id):
    """Handle editing an existing contact for a client."""
    contact = ClientContact.query.filter_by(
        id=contact_id, client_id=client_id
    ).first_or_404()
    client = contact.client
    form = ContactForm(obj=contact)  # Pre-populate

    if form.validate_on_submit():
        try:
            contact.first_name = form.first_name.data
            contact.last_name = form.last_name.data
            contact.email = form.email.data
            contact.phone = form.phone.data
            contact.position = form.position.data
            contact.notes = form.notes.data
            contact.is_primary = form.is_primary.data
            db.session.commit()
            flash("Contact updated successfully!", "success")
            return redirect(url_for("client.client_detail", client_id=client.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error updating contact {contact_id} for client {client_id}: {e}",
                exc_info=True,
            )
            flash("Error updating contact. Please check logs.", "danger")

    return render_template(
        "client/contact_form.html",
        title="Edit Contact",
        form=form,
        client=client,
        contact=contact,
    )


@client_bp.route(
    "/clients/<int:client_id>/contacts/<int:contact_id>/delete", methods=["POST"]
)
@login_required
def delete_contact(client_id, contact_id):
    """Handle deleting a contact for a client."""
    contact = ClientContact.query.filter_by(
        id=contact_id, client_id=client_id
    ).first_or_404()
    try:
        db.session.delete(contact)
        db.session.commit()
        flash(
            f'Contact "{contact.first_name} {contact.last_name}" deleted successfully!',
            "success",
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error deleting contact {contact_id} for client {client_id}: {e}",
            exc_info=True,
        )
        flash("Error deleting contact. Please check logs.", "danger")


# --- Asset Management Routes --- #


@client_bp.route("/clients/<int:client_id>/assets/add", methods=["GET", "POST"])
@login_required
def add_asset(client_id):
    """Handle adding a new asset for a client."""
    client = Client.query.get_or_404(client_id)
    form = AssetForm()

    # Populate location choices dynamically
    form.location_id.choices = [("", "-- Select Location (Optional) --")] + [
        (loc.id, loc.name)
        for loc in client.locations.order_by(ClientLocation.name).all()
    ]

    if form.validate_on_submit():
        try:
            new_asset = ClientAsset(
                client_id=client.id,
                name=form.name.data,
                asset_type=form.asset_type.data,
                description=form.description.data,
                criticality_score=form.criticality_score.data,
                location_id=form.location_id.data if form.location_id.data else None,
            )
            # Process technical details (categories) from hidden field JSON string
            # Read directly from request.form instead of form.field.data
            tech_details_str = request.form.get("technical_details")
            current_app.logger.debug(
                f"[add_asset] Raw tech_details_str from request.form: '{tech_details_str}' (type: {type(tech_details_str)})"
            )
            if tech_details_str:
                current_app.logger.debug(
                    "[add_asset] tech_details_str is not empty, attempting parse."
                )
                try:
                    # Parse the JSON string into a list
                    parsed_details = json.loads(tech_details_str)
                    current_app.logger.debug(
                        f"[add_asset] Successfully parsed JSON: {parsed_details} (type: {type(parsed_details)})"
                    )
                    # Ensure it's a list (basic validation)
                    if isinstance(parsed_details, list):
                        new_asset.technical_details = parsed_details
                        current_app.logger.debug(
                            f"[add_asset] Assigning parsed list to new_asset.technical_details: {new_asset.technical_details}"
                        )
                    else:
                        current_app.logger.warning(
                            f"[add_asset] Parsed technical_details is not a list: {parsed_details}. Setting to empty list."
                        )
                        new_asset.technical_details = []
                except json.JSONDecodeError:
                    current_app.logger.error(
                        f"[add_asset] Failed to decode technical_details JSON: {tech_details_str}",
                        exc_info=True,
                    )
                    flash("Error processing technical details categories.", "warning")
                    new_asset.technical_details = []  # Default to empty list on error
            else:
                current_app.logger.debug(
                    "[add_asset] tech_details_str is empty, setting technical_details to empty list."
                )
                new_asset.technical_details = []  # Use empty list if field is empty

            current_app.logger.debug(
                f"Asset technical_details *before commit* (add): {new_asset.technical_details}"
            )
            db.session.add(new_asset)
            db.session.commit()
            flash("Asset added successfully!", "success")
            return redirect(url_for("client.client_detail", client_id=client.id))
        except Exception as e:
            db.session.rollback()
            # Re-render form on general exception during POST
            return render_template(
                "client/asset_form.html",
                title="Add New Asset",
                form=form,
                client=client,
            )

    # Handle GET request or failed validation
    return render_template(
        "client/asset_form.html", title="Add New Asset", form=form, client=client
    )


@client_bp.route(
    "/clients/<int:client_id>/assets/<int:asset_id>/edit", methods=["GET", "POST"]
)
@login_required
def edit_asset(client_id, asset_id):
    """Handle editing an existing asset for a client."""
    asset = ClientAsset.query.filter_by(id=asset_id, client_id=client_id).first_or_404()
    client = asset.client

    form = AssetForm(obj=asset)  # Pre-populate using object
    # Manually set technical_details data as a JSON string for the hidden field
    if request.method == "GET":  # Only do this when initially loading the form
        if asset.technical_details and isinstance(asset.technical_details, list):
            form.technical_details.data = json.dumps(asset.technical_details)
        else:
            # Ensure it's an empty JSON array string if no data or not a list
            form.technical_details.data = "[]"

    # Populate location choices dynamically
    form.location_id.choices = [("", "-- Select Location (Optional) --")] + [
        (loc.id, loc.name)
        for loc in client.locations.order_by(ClientLocation.name).all()
    ]

    if form.validate_on_submit():
        try:
            asset.name = form.name.data
            asset.asset_type = form.asset_type.data
            asset.description = form.description.data
            asset.criticality_score = form.criticality_score.data
            asset.location_id = form.location_id.data if form.location_id.data else None

            # Process technical details (categories) from hidden field JSON string
            # Read directly from request.form instead of form.field.data
            tech_details_str = request.form.get("technical_details")
            current_app.logger.debug(
                f"[edit_asset] Raw tech_details_str from request.form: '{tech_details_str}' (type: {type(tech_details_str)})"
            )
            if tech_details_str:
                current_app.logger.debug(
                    "[edit_asset] tech_details_str is not empty, attempting parse."
                )
                try:
                    # Parse the JSON string into a list
                    parsed_details = json.loads(tech_details_str)
                    current_app.logger.debug(
                        f"[edit_asset] Successfully parsed JSON: {parsed_details} (type: {type(parsed_details)})"
                    )
                    # Ensure it's a list (basic validation)
                    if isinstance(parsed_details, list):
                        asset.technical_details = parsed_details
                        current_app.logger.debug(
                            f"[edit_asset] Assigning parsed list to asset.technical_details: {asset.technical_details}"
                        )
                    else:
                        current_app.logger.warning(
                            f"[edit_asset] Parsed technical_details is not a list: {parsed_details}. Setting to empty list."
                        )
                        asset.technical_details = []
                except json.JSONDecodeError:
                    current_app.logger.error(
                        f"[edit_asset] Failed to decode technical_details JSON: {tech_details_str}",
                        exc_info=True,
                    )
                    flash("Error processing technical details categories.", "warning")
                    # Re-render form on error
                    return render_template(
                        "client/asset_form.html",
                        title="Edit Asset",
                        form=form,
                        client=client,
                        asset=asset,
                    )
            else:
                current_app.logger.debug(
                    "[edit_asset] tech_details_str is empty, setting technical_details to empty list."
                )
                asset.technical_details = []  # Use empty list if field is empty

            current_app.logger.debug(
                f"Asset technical_details *before commit* (edit): {asset.technical_details}"
            )
            db.session.commit()
            flash("Asset updated successfully!", "success")
            return redirect(url_for("client.client_detail", client_id=client.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error updating asset {asset_id} for client {client_id}: {e}",
                exc_info=True,
            )
            flash("Error updating asset. Please check logs.", "danger")

    return render_template(
        "client/asset_form.html",
        title="Edit Asset",
        form=form,
        client=client,
        asset=asset,
    )


@client_bp.route(
    "/clients/<int:client_id>/assets/<int:asset_id>/delete", methods=["POST"]
)
@login_required
def delete_asset(client_id, asset_id):
    """Handle deleting an asset for a client."""
    asset = ClientAsset.query.filter_by(id=asset_id, client_id=client_id).first_or_404()
    try:
        db.session.delete(asset)
        db.session.commit()
        flash(f'Asset "{asset.name}" deleted successfully!', "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error deleting asset {asset_id} for client {client_id}: {e}",
            exc_info=True,
        )
        flash("Error deleting asset. Please check logs.", "danger")

    return redirect(url_for("client.client_detail", client_id=client_id))

    # Need to create this template
    return render_template(
        "client/asset_form.html", title="Add New Asset", form=form, client=client
    )

    return redirect(url_for("client.client_detail", client_id=client_id))

    # Need to create this template
    return render_template(
        "client/contact_form.html", title="Add New Contact", form=form, client=client
    )

    return redirect(url_for("client.client_detail", client_id=client_id))

    return render_template(
        "client/location_form.html",
        title="Edit Location",
        form=form,
        client=client,
        location=location,
    )

    # Need to create this template
    return render_template(
        "client/location_form.html", title="Add New Location", form=form, client=client
    )
