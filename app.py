"""
Implementation of the Streamlit App
"""
import logging
from typing import Tuple

import folium
import httpx
import streamlit as st
from streamlit_folium import st_folium

from api import get_adzuna_ads_page
from logger_config import setup_logging
from utils import configure, create_client


# Instanciating logger
setup_logging()
logger = logging.getLogger(__name__)


# Specific Utility Functions (by order of appearance)
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
                return float(results[0]["lat"]), float(results[0]["lon"])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occured: {e}")
        except Exception as e:
            logger.error(f"An error occured: {e}")

    return None, None


def calculate_zoom_level(radius_km: float) -> int:
    """
    Heuristic function adapting the zoom_level of display to the chosen radius
    """
    if radius_km > 50:
        return 8  # More zoomed out
    if radius_km > 30:
        return 9
    if radius_km > 10:
        return 10
    return 11  # More zoomed in


def create_map(center_location: Tuple[float, float], search_radius_km: float) -> folium.Map:
    """
    Returns a folium map centered around center_location, with an adaptive zoom
    """
    zoom_level = calculate_zoom_level(search_radius_km)
    m = folium.Map(location=center_location, zoom_start=zoom_level)
    
    # Adding to the m map a circle corresponding to the search radius
    folium.Circle(
        center_location,
        radius=search_radius_km * 1000,
        color="blue",
        fill=True,
        opacity=0.1
    ).add_to(m)
    
    return m


# Configure and create client
conf = configure()
cli = create_client(conf["ua"])

# Initialize session state variables if they don't already exist
if 'location' not in st.session_state:
    st.session_state['location'] = None
if 'radius' not in st.session_state:
    st.session_state['radius'] = 1
if 'lat_lon' not in st.session_state:
    st.session_state['lat_lon'] = (None, None)

# Sidebar for User Inputs
with st.sidebar:
    st.session_state['location'] = st.text_input("Where?", st.session_state['location'])
    st.session_state['radius'] = st.slider("Up to how many kilometers?", min_value=1, max_value=100, value=st.session_state['radius'])
    search_button = st.button("Search Job Ads")

# Handle events on the left sidebar
if search_button and st.session_state['location']:
    lat, lon = get_coordinates(st.session_state['location'])
    if lat and lon:
        st.session_state['lat_lon'] = (lat, lon)
        logger.info(f"Coordinates for {st.session_state['location']}: Latitude {lat}, Longitude {lon}")
    else:
        logger.warning(f"Couldn't get coordinates for {st.session_state['location']}.")
        st.warning("Could not find the location.")

# Create and display the map if coordinates are available
lat, lon = st.session_state['lat_lon']
if lat and lon:
    map = create_map((lat, lon), st.session_state['radius'])
    st_folium(map)  
elif search_button:
    st.warning("Please enter a location...")
