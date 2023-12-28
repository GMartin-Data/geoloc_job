"""
Implementation of the Streamlit App
"""

import streamlit as st

from api import get_adzuna_ads_page
from utils import configure, create_client


# Configure and create client
conf = configure()
cli = create_client(conf['ua'])

# User inputs
location = st.text_input("Where?")
radius = st.slider("Up to how many kilometers?", min_value=1, max_value=100)

# Button to trigger the API call
if st.button("Search Jobs"):
    if location:  # Ensure location is provided
        with st.spinner("Fetching job ads..."):
            results = get_adzuna_ads_page(conf, cli, 1, where=location, distance=radius)
            st.json(results)
    else:
        st.warning("Please enter a location.")
