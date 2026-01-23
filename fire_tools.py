from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import json
import os

# --- Import your existing logic ---
# Ensure settlelite_image_fire_coordinate.py is in the same folder
try:
    from settlelite_image_fire_coordinate import fetch_firms_data
except ImportError:
    # Mock function for demonstration if file is missing
    async def fetch_firms_data(country, state, source, day_range):
        return (f"Mock data for {state}, {country}", "temp_file.csv")

# --- Tool 1: Internal Fire Data ---
@tool
async def get_current_fire_data(state: str, country: str = "India") -> str:
    """
    Fetches real-time wildfire data for a specific state and country.
    Useful when the user asks about active fires, confidence levels, or coordinates.
    """
    try:
        # Reusing your existing function logic
        raw_data, temp_file = await fetch_firms_data(
            country=country, 
            state=state, 
            source="VIIRS_SNPP_NRT", 
            day_range=3
        )
        
        # Cleanup temp file immediately to keep server clean
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

        # If data is a DataFrame, convert to JSON for the AI to read
        if hasattr(raw_data, 'to_json'):
            # Filter for high confidence to reduce token usage
            high_conf = raw_data[raw_data['confidence'] == 'h']
            if high_conf.empty:
                return f"No High Confidence fires detected in {state}."
            return high_conf.to_json(orient="records")
        
        return str(raw_data)
    except Exception as e:
        return f"Error fetching fire data: {str(e)}"

# --- Tool 2: Web Search (for News/Weather contexts) ---
@tool
def search_web(query: str) -> str:
    """
    Searches the web for news, evacuation orders, or general info not in the database.
    Use this if the user asks about news reports or things outside the dataset.
    """
    search = DuckDuckGoSearchRun()
    return search.invoke(query)

# Export list of tools
tools_list = [get_current_fire_data, search_web]