from sqlalchemy import or_
from app.models.client import Client, ClientLocation  # Renamed imports
from app import db  # Corrected import


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
