from flask import request, jsonify, render_template, redirect, url_for, flash, abort
from flask_login import login_required
from app.services.client_service import search_clients, create_client_with_details, get_client_by_id # Added get_client_by_id
from .forms import ClientOnboardingForm
from . import client_bp
from app.models.client import Client # Import Client model for type hinting if needed, or rely on service


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


@client_bp.route("/clients/search", methods=["GET"])
@login_required
def search_page():
    return render_template("client/search.html")



@client_bp.route('/clients/onboard', methods=['GET', 'POST'])
@login_required
def onboard_client():
    """Handle client onboarding form display and submission."""
    form = ClientOnboardingForm()
    if form.validate_on_submit():
        # Extract data from the form
        form_data = form.data
        # Call the service function to create the client
        new_client = create_client_with_details(form_data)
        if new_client:
            flash(f'Client "{new_client.name}" onboarded successfully!', 'success')
            # Redirect to the new client's detail page
            return redirect(url_for('client.client_detail', client_id=new_client.id))
        else:
            flash('Error onboarding client. Please check the logs or try again.', 'danger')

    # For GET request or if form validation fails
    return render_template('client/onboard_client.html', title='Onboard New Client', form=form)



@client_bp.route('/clients/<int:client_id>')
@login_required
def client_detail(client_id):
    """Display the details for a specific client."""
    client = get_client_by_id(client_id)
    if not client:
        abort(404) # Not found

    # Pass client data to the template
    # You might want to fetch related data like locations, contacts, assets here
    # depending on what the detail page needs to show.
    # For now, just pass the client object.
    return render_template('client/client_detail.html', title=f"Client: {client.name}", client=client)
