from sqlalchemy import or_
from app.models.client import Client, ClientLocation, ClientContact # Added ClientContact

from app.models.client import Client, ClientLocation  # Renamed imports
from app import db  # Corrected import
import logging

logger = logging.getLogger(__name__)



def search_clients(query=None, industry=None, country=None):
    # Use correct class names Client and ClientLocation
    q = db.session.query(Client, ClientLocation).join(
        ClientLocation, Client.id == ClientLocation.client_id  # Use correct foreign key
    )
    if query:
        search_str = f"%{query}%"
        q = q.filter(
            or_(
                Client.name.ilike(search_str),
                Client.industry.ilike(search_str),
                ClientLocation.city.ilike(search_str),
            )
        )
    if industry:
        q = q.filter(Client.industry == industry)
    if country:
        q = q.filter(ClientLocation.country == country)
    results = q.all()
    clients = {}
    # Use correct variable names client and loc
    for client, loc in results:
        if client.id not in clients:
            clients[client.id] = {
                "id": client.id,
                "name": client.name,
                "industry": client.industry,
                "locations": [],
            }
        clients[client.id]["locations"].append({"city": loc.city, "country": loc.country})
    return list(clients.values())


def create_client_with_details(form_data: dict) -> Client | None:
    """Creates a new client, primary contact, and HQ location.

    Args:
        form_data: A dictionary containing validated form data.

    Returns:
        The newly created Client object, or None if an error occurred.
    """
    try:
        # Create Client organization
        new_client = Client(
            name=form_data.get('name'),
            industry=form_data.get('industry'),
            website=form_data.get('website'),
            description=form_data.get('description'),
            public_profile_summary=form_data.get('public_profile_summary')
        )
        db.session.add(new_client)
        # Flush to get the new_client.id before creating related objects
        db.session.flush()

        # Create Primary Contact
        new_contact = ClientContact(
            client_id=new_client.id,
            first_name=form_data.get('contact_first_name'),
            last_name=form_data.get('contact_last_name'),
            email=form_data.get('contact_email'),
            phone=form_data.get('contact_phone'),
            position=form_data.get('contact_position'),
            is_primary=True
        )
        db.session.add(new_contact)

        # Create Primary Location (HQ)
        new_location = ClientLocation(
            client_id=new_client.id,
            name=form_data.get('location_name', 'Headquarters'), # Default name
            address=form_data.get('location_address'),
            city=form_data.get('location_city'),
            state=form_data.get('location_state'),
            country=form_data.get('location_country'),
            postal_code=form_data.get('location_postal_code'),
            location_type="HQ"
        )
        db.session.add(new_location)

        db.session.commit()
        logger.info(f"Successfully created new client: {new_client.name} (ID: {new_client.id})")
        return new_client

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating new client: {e}", exc_info=True)
        return None
