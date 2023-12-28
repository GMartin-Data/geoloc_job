"""
Implementation of the Streamlit App
"""
import logging
from typing import Tuple

import httpx
import streamlit as st

from api import get_adzuna_ads_page
from logger_config import setup_logging
from utils import configure, create_client


# Instanciating logger
setup_logging()
logger = logging.getLogger(__name__)


# Specific Utility Function
def get_coordinates(address: str) -> Tuple[float, float] | Tuple[None, None]:
    """Gets geographic coordinates from an address"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    with httpx.Client() as client:
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            results = response.json()
            if results:
                return results[0]["lat"], results[0]["lon"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occured: {e}")
        except Exception as e:
            logger.error(f"An error occured: {e}")

    return None, None


# Configure and create client
conf = configure()
cli = create_client(conf["ua"])

# User inputs
with st.sidebar:
    location = st.text_input("Where?")
    radius = st.slider("Up to how many kilometers?", min_value=1, max_value=100)
    search_button = st.button("Search Job Ads")

# Button to trigger the API call
if search_button:
    if location:  # Ensure location is provided
        lat, lon = get_coordinates(location)
        if lat and lon:
            logger.info(f"Coordinates for {location}: Latitude {lat}, Longitude {lon}")
        else:
            logger.warning(f"Couldn't get coordinates for {location}")
        with st.spinner("Fetching job ads..."):
            results = get_adzuna_ads_page(conf, cli, 1, where=location, distance=radius)
            st.json(results)
    else:
        st.warning("Please enter a location.")
