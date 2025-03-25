from sqlalchemy import or_
from app.models.client import Organization, Location
from app.utils.db import db


def search_clients(query=None, industry=None, country=None):
    q = db.session.query(Organization, Location).join(
        Location, Organization.id == Location.organization_id
    )
    if query:
        search_str = f"%{query}%"
        q = q.filter(
            or_(
                Organization.name.ilike(search_str),
                Organization.industry.ilike(search_str),
                Location.city.ilike(search_str),
            )
        )
    if industry:
        q = q.filter(Organization.industry == industry)
    if country:
        q = q.filter(Location.country == country)
    results = q.all()
    clients = {}
    for org, loc in results:
        if org.id not in clients:
            clients[org.id] = {
                "id": org.id,
                "name": org.name,
                "industry": org.industry,
                "locations": [],
            }
        clients[org.id]["locations"].append({"city": loc.city, "country": loc.country})
    return list(clients.values())
