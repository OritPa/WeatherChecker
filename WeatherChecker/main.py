import requests
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json
import re

def is_valid_city_input(location):
    if not isinstance(location, str):
        return False
    location = location.strip()
    return bool(re.match(r"^[a-zA-Z\s,.\-']+$", location))  # Allow letters, spaces, commas, hyphens, periods

def GetWeatherData(location):
    api_key = "7ca1b7fdc9a1b1da782c8929f3e2d595"

    # Step 1: Basic validation
    if not is_valid_city_input(location):
        print("Invalid city input. Please use a format like 'City', 'City, Country', or 'City, State, Country'.")
        return None

    # Step 2: Use Geocoding API to get coordinates
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={api_key}"

    try:
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            print("City not found via geolocation API.")
            return None

        location_info = geo_data[0]
        lat = location_info['lat']
        lon = location_info['lon']
        resolved_city = location_info.get('name')
        resolved_state = location_info.get('state', '')
        resolved_country = location_info.get('country')

    except requests.exceptions.RequestException as geo_error:
        print(f"Error validating city: {geo_error}")
        return None

    # Step 3: Get weather data using lat/lon
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        data = weather_response.json()

        if data.get('cod') != 200:
            print(f"API Error: {data.get('message')}")
            return None

        # Build dictionary
        weather_info = {
            "city": resolved_city,
            "state": resolved_state,
            "country": resolved_country,
            "temperature": round(data['main']['temp'], 1),
            "feels_like": round(data['main']['feels_like'], 1),
            "temp_min": round(data['main']['temp_min'], 1),
            "temp_max": round(data['main']['temp_max'], 1),
            "humidity": data['main']['humidity'],
            "description": data['weather'][0]['description'],
            "icon": data['weather'][0]['icon'],
            "longitude": lon,
            "latitude": lat,
            "timezone_offset": data.get('timezone')
        }

        return weather_info

    except requests.exceptions.RequestException as error:
        print(f"Weather API request failed: {error}")
        return None

    except (KeyError, json.JSONDecodeError) as parse_error:
        print(f"Error parsing weather data: {parse_error}")
        return None