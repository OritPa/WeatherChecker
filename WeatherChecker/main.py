import requests
import streamlit as st
from datetime import datetime, timedelta , timezone
import pandas as pd
import json


def is_valid_city_input(city):
    # checks if the input is correct there are digits or special chars
    special_char= "!@#$%^&*()_+-=[]{}/\\|;:'\",<>?`"
    is_digit= any(char.isdigit() for char in city)
    has_special= any(char in special_char for char in city)
    return not is_digit and not has_special

def does_city_exists(city: str, api_key: str):
     #Validate city name via OpenWeatherMap Geocoding API.

    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"

    try:
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            return None

        location_info = geo_data[0]
        return {
            "lat": location_info['lat'],
            "lon": location_info['lon'],
            "city_name": location_info.get('name'),
            "state_name": location_info.get('state', ''),
            "country_name": location_info.get('country')
        }

    except requests.exceptions.RequestException as geo_error:
        print(f"Error in geo data: {geo_error}")
        return None

def current_weather_data(city):
    api_key = "7ca1b7fdc9a1b1da782c8929f3e2d595"

    if not is_valid_city_input(city):
        print("Invalid city input. Please enter input without digits or special characters")
        return None

    location = does_city_exists(city, api_key)
    if not location:
        print("City not found!")
        return None

    lat, lon = location["lat"], location["lon"]
    city_name = location["city_name"]
    state_name = location["state_name"]
    country_name = location["country_name"]


    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        data = weather_response.json()

        if data.get('cod') != 200:
            print(f"API Error: {data.get('message')}")
            return None

        timestamp = data.get('dt')
        timezone_offset = data.get('timezone', 0)
        target_tz = timezone(timedelta(seconds=timezone_offset))
        local_dt = datetime.fromtimestamp(timestamp, tz=target_tz)

        weather_info = {
            "city": city_name,
            "state": state_name,
            "country": country_name,
            "temperature": round(data['main']['temp'], 1),
            "feels_like": round(data['main']['feels_like'], 1),
            "temp_min": round(data['main']['temp_min'], 1),
            "temp_max": round(data['main']['temp_max'], 1),
            "humidity": data['main']['humidity'],
            "description": data['weather'][0]['description'],
            "icon": data['weather'][0]['icon'],
            "longitude": lon,
            "latitude": lat,
            "timestamp": local_dt
        }

        return weather_info

    except requests.exceptions.RequestException as error:
        print(f"Weather API request failed: {error}")
        return None

    except (KeyError, json.JSONDecodeError) as parse_error:
        print(f"Error parsing weather data: {parse_error}")
        return None

def five_day_forcast(city):
    api_key = "7ca1b7fdc9a1b1da782c8929f3e2d595"

    location = does_city_exists(city, api_key)
    if not location:
        print("City not found!")
        return None

    lat, lon = location["lat"], location["lon"]

    five_day_forecast_url= f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        forecast_response = requests.get(five_day_forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        if forecast_data.get('cod') != "200":
            print(f"API Error: {forecast_data.get('message')}")
            return None

        city_population= forecast_data["city"]["population"]
        city_timezone = forecast_data["city"]["timezone"]
        tz = timezone(timedelta(seconds=city_timezone))

        daily_data = {}

        for day in forecast_data["list"]:
            dt_local = datetime.fromtimestamp(day["dt"], tz=tz)
            date_str = dt_local.strftime('%Y-%m-%d')

            if date_str not in daily_data and dt_local.hour in [12, 15]:
                daily_data[date_str] = {
                    "date": date_str,
                    "time": dt_local.strftime('%H:%M'),
                    "temp": round(day["main"]["temp"], 1),
                    "temp_min": round(day['main']['temp_min'], 1),
                    "temp_max": round(day['main']['temp_max'], 1),
                    "description": day["weather"][0]["description"],
                    "icon": day["weather"][0]["icon"],
                    "humidity": day["main"]["humidity"],
                    "wind_speed": day["wind"]["speed"]
                }

        # Ensure you only return 5 days max
        return {
            "population": city_population,
            "forecast": list(daily_data.values())[:5]
        }

    except requests.exceptions.RequestException as error:
        print(f"Forecast API request failed: {error}")
        return None

    except (KeyError, json.JSONDecodeError) as parse_error:
        print(f"Error parsing forecast data: {parse_error}")
        return None


#Streamlit app
st.title('Streamlit Weather Checker App')
st.markdown('Creator: Orit Padawer')
st.markdown('Data retrieved from https://openweathermap.org/api')

city= st.text_input("Enter a city").capitalize()
if city:
    print(city)


