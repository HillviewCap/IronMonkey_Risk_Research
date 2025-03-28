from flask import request, jsonify, render_template, redirect, url_for, flash

from flask import request, jsonify, render_template
from flask_login import login_required
from app.services.client_service import search_clients, create_client_with_details # Added create_client_with_details
from .forms import ClientOnboardingForm # Added form import

from app.services.client_service import search_clients
from . import client_bp  # Import the blueprint from __init__.py


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
            # Redirect to a client detail page (assuming it exists or will be created)
            # For now, let's redirect to a placeholder or the search page
            # Replace 'client.search_page' with 'client.client_detail' and add client_id=new_client.id when ready
            return redirect(url_for('client.search_page'))
        else:
            flash('Error onboarding client. Please check the logs or try again.', 'danger')

    # For GET request or if form validation fails
    return render_template('client/onboard_client.html', title='Onboard New Client', form=form)
