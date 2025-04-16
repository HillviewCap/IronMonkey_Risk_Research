from app.models.country import Country
from flask import current_app
import logging

logger = logging.getLogger(__name__)


def get_countries_for_dropdown(
    include_empty_option=True, empty_label="-- Select Country --"
):
    """
    Fetch countries from the database for use in dropdown menus.

    Args:
        include_empty_option (bool): Whether to include an empty option at the beginning
        empty_label (str): Label for the empty option

    Returns:
        list: List of tuples (abbreviation, country) for use in SelectField choices
    """
    try:
        # Query countries from the database, ordered by country name
        countries_query = Country.query.order_by(Country.country).all()

        logger.debug(f"Found {len(countries_query)} countries in the database")

        # Format as (value, label) tuples for SelectField
        country_choices = []
        for c in countries_query:
            # Use abbreviation if available, otherwise use id as string
            value = c.abbreviation if c.abbreviation else str(c.id)
            country_choices.append((value, c.country))

        logger.debug(f"Formatted {len(country_choices)} countries for dropdown")

        # Add empty option if requested
        if include_empty_option:
            country_choices = [("", empty_label)] + country_choices

        # If no countries were found (even after trying to use IDs as fallback),
        # add a message to inform the user
        if not country_choices or (
            len(country_choices) == 1 and country_choices[0][0] == ""
        ):
            logger.warning("No countries found in the database for dropdown")
            if include_empty_option:
                return [("", "No countries available")]
            else:
                return [("", "No countries available")]

        return country_choices
    except Exception as e:
        logger.error(f"Error fetching countries from database: {e}", exc_info=True)
        # Return a minimal fallback in case of error
        return [("", "Error loading countries")]


def get_all_countries_for_dropdown(
    include_empty_option=True, empty_label="-- All Countries --"
):
    """
    Fetch countries from the database for use in filter dropdowns.
    Similar to get_countries_for_dropdown but with a different default empty label.

    Args:
        include_empty_option (bool): Whether to include an empty option at the beginning
        empty_label (str): Label for the empty option

    Returns:
        list: List of tuples (abbreviation, country) for use in SelectField choices
    """
    return get_countries_for_dropdown(include_empty_option, empty_label)
