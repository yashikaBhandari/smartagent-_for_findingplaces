from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")



import streamlit as st
import streamlit_geolocation
import os
import requests
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.memory import ConversationBufferMemory



llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0)


# ----------------------------
# 2. NEARBY PLACES TOOL (UPGRADED)
# ----------------------------

# **NEW FUNCTION: Geocoding to get coordinates for a city**
def geocode_city(city_name: str):
    """Gets latitude and longitude for a given city name using a free API."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "results" in data:
            location = data["results"][0]
            return location["latitude"], location["longitude"]
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Geocoding failed: {e}")
        return None, None

def fetch_places(text_query: str, lat: float, lng: float, radius: int = 5000):
    """Calls the Google Places API's searchText endpoint."""
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress"
    }
    data = {
        "textQuery": text_query,
        "maxResultCount": 5,
        "locationBias": {  # NOTE: Changed from locationRestriction to locationBias
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius)
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error fetching places: {e}"


def summarize_places(places_json):
    """Uses an LLM to create a clean summary of the places."""
    # (This function is unchanged)
    places_text = json.dumps(places_json, indent=2)
    prompt = ChatPromptTemplate.from_template(
        "Summarize the nearby places from this JSON into a clear, bulleted list. Include the name and address. If no places are found, say so.\nJSON:\n{places_text}")
    chain = prompt | llm
    return chain.invoke({"places_text": places_text}).content


# **MODIFIED TOOL LOGIC**
def nearby_places_tool_func(query: str):
    """
    Main tool function. It gets the correct location and passes the
    full user query to the searchText endpoint.
    """
    lat, lng = None, None

    # Step 1: Check if a specific location is mentioned (this logic is unchanged)
    location_prompt = ChatPromptTemplate.from_template(
        "From the user query '{query}', extract the city or location name. If no location is mentioned, respond with only the word 'None'.")
    extractor_chain = location_prompt | llm
    location_name = extractor_chain.invoke({"query": query}).content.strip()

    if location_name != "None":
        st.write(f"Geocoding location: {location_name}...")
        lat, lng = geocode_city(location_name)
        if not lat:
            return f"Sorry, I couldn't find the coordinates for {location_name}."
    else:
        # Step 2: Fallback to the user's live location (this logic is unchanged)
        if 'latitude' in st.session_state and 'longitude' in st.session_state:
            lat = st.session_state.latitude
            lng = st.session_state.longitude
        else:
            return "I don't have your location yet. Please grant location access or specify a city in your query."

    # **CHANGE**: No need to extract 'place_type' anymore.
    # We pass the user's original query directly to fetch_places.
    st.write(f"🔍 Searching for '{query}' near ({lat:.4f}, {lng:.4f})...")
    raw_places = fetch_places(text_query=query, lat=lat, lng=lng, radius=5000)
    return summarize_places(raw_places)


# ----------------------------
# 3. AGENT WITH MEMORY
# ----------------------------

tools = [
    Tool(
        name="Places Search",
        func=nearby_places_tool_func,
        # **UPDATED DESCRIPTION: Crucial for the agent to understand its new capability**
        description="Use this tool to find information about places like restaurants or cafes. It can search near the user's current location or in a specific city if mentioned (e.g., 'restaurants in Delhi')."
    )
]
prompt = hub.pull("hwchase17/react-chat")


@st.cache_resource
def initialize_agent_executor():
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True, handle_parsing_errors=True)
    return agent_executor


agent_executor = initialize_agent_executor()

# ----------------------------
# 4. STREAMLIT UI
# ----------------------------
# (The UI section remains unchanged)
st.title("Smart Places Finder 🌍")

location_data = streamlit_geolocation.streamlit_geolocation()

if location_data and 'latitude' in location_data:
    st.session_state.latitude = location_data['latitude']
    st.session_state.longitude = location_data['longitude']
    st.success(f"📍 Your location acquired. You can now ask about places 'near me' or in a specific city.")
else:
    st.info(
        "Waiting for location access... You can still ask about places in a specific city (e.g., 'cafes in Jalandhar').")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask about places near you or in a city..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent_executor.invoke({"input": user_input})
            st.markdown(response["output"])

    st.session_state.messages.append({"role": "assistant", "content": response["output"]})