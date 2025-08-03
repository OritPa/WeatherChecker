import requests
import streamlit as st
from datetime import datetime, timedelta , timezone
import pandas as pd
import json
import folium
from streamlit_folium import st_folium ,folium_static


def find_matching_cities(city: str, limit: int = 5):
    api_key = "7ca1b7fdc9a1b1da782c8929f3e2d595"
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={limit}&appid={api_key}"

    try:
        response = requests.get(geo_url)
        response.raise_for_status()
        results = response.json()

        if not results:
            return []

        cities = []
        for item in results:
            cities.append({
                "lat": item["lat"],
                "lon": item["lon"],
                "city_name": item["name"],
                "state_name": item.get("state", ""),
                "country_name": item["country"]
            })

        return cities

    except requests.exceptions.RequestException as error:
        print(f"Geo API error: {error}")
        return []

def is_valid_city_input(city):
    # checks if the input is correct there are digits or special chars
    special_char= "!@#$%^&*()_+-=[]{}/\\|;:'\",<>?`"
    is_digit= any(char.isdigit() for char in city)
    has_special= any(char in special_char for char in city)
    return not is_digit and not has_special

def does_city_exists(lat: float, lon: float, api_key: str):
     #Validate city name via OpenWeatherMap Geocoding API.
    geo_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"

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

def current_weather_data(lat: float, lon: float):

    api_key = "7ca1b7fdc9a1b1da782c8929f3e2d595"

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    location= does_city_exists(lat, lon, api_key)
    city_name = location["city_name"]
    country_name = location["country_name"]



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
            "city": city_name ,
            "country": country_name,
            "temperature": round(data['main']['temp'], 1),
            "feels_like": round(data['main']['feels_like'], 1),
            "temp_min": round(data['main']['temp_min'], 1),
            "temp_max": round(data['main']['temp_max'], 1),
            "humidity": data['main']['humidity'],
            "description": data['weather'][0]['description'],
            "icon": data['weather'][0]['icon'],
            "local_timestamp": local_dt,
            "lat": lat,
            "lon":lon
        }

        return weather_info

    except requests.exceptions.RequestException as error:
        print(f"Weather API request failed: {error}")
        return None

    except (KeyError, json.JSONDecodeError) as parse_error:
        print(f"Error parsing weather data: {parse_error}")
        return None

def five_day_forcast(lat: float, lon: float):
    api_key = "7ca1b7fdc9a1b1da782c8929f3e2d595"

    five_day_forecast_url= f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    location = does_city_exists(lat, lon, api_key)
    city_name = location["city_name"]
    country_name = location["country_name"]


    try:
        forecast_response = requests.get(five_day_forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        if forecast_data.get('cod') != "200":
            print(f"API Error: {forecast_data.get('message')}")
            return None


        city_population= forecast_data["city"]["population"]
        city_tz = timezone(timedelta(seconds=forecast_data["city"]["timezone"]))


        # Group entries by date
        entries_by_date = {}
        for entry in forecast_data["list"]:
            local_dt = datetime.fromtimestamp(entry["dt"], tz=city_tz)
            date_str = local_dt.strftime("%Y-%m-%d")

            if date_str not in entries_by_date:
                entries_by_date[date_str] = []
            entries_by_date[date_str].append((local_dt, entry))

        # Build one forecast per day, prefer 12:00 or 15:00
        daily_data = []
        for date_str, entries in entries_by_date.items():
            print(f"{date_str}: {[e[0].hour for e in entries]}")
            preferred = [e for e in entries if e[0].hour in [11, 12, 13, 14, 15, 16]]
            chosen = preferred[0] if preferred else entries[0]
            local_dt, forecast = chosen

            daily_data.append({
                "date": date_str,
                "time": local_dt.strftime("%H:%M"),
                "temp": round(forecast["main"]["temp"], 1),
                "temp_min": round(forecast["main"]["temp_min"], 1),
                "temp_max": round(forecast["main"]["temp_max"], 1),
                "description": forecast["weather"][0]["description"],
                "icon": forecast["weather"][0]["icon"],
                "humidity": forecast["main"]["humidity"],
                "wind_speed": forecast["wind"]["speed"]
            })

        # Ensure you only return 5 days max
        return {
            "population": city_population,
            "city": city_name,
            "country": country_name,
            "forecast": daily_data[:5]
        }

    except requests.exceptions.RequestException as error:
        print(f"Forecast API request failed: {error}")
        return None

    except (KeyError, json.JSONDecodeError) as parse_error:
        print(f"Error parsing forecast data: {parse_error}")
        return None


#Streamlit app
st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .stApp {
            background-color: #e3f2fd;
        }

        .main {
            max-width: 100%;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        table {
            width: 100%;
        }

        .dataframe th, .dataframe td {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.title('Streamlit Weather Checker App')
st.markdown('Creator: Orit Padawer')
st.markdown('Data retrieved from https://openweathermap.org/api')
col1, spacer, col2 = st.columns([1, 0.2, 1])
with col1:
    city1_input= st.text_input("Enter a city")

    selected_city1 = None
    weather1 = None
    forecast1 = None

    if city1_input:
            matches = find_matching_cities(city1_input)

    if matches:
        city_names = [
            f"{m['city_name']}, {m['state_name']}, {m['country_name']}".strip(', ')
            for m in matches
        ]
        selected_city_str = st.selectbox("Choose a city:", city_names, key="city1_select")
        selected_city1 = matches[city_names.index(selected_city_str)]

        lat1, lon1 = selected_city1['lat'], selected_city1['lon']
        #st.success(f"You selected: {selected_city_str}")
        weather1 = current_weather_data(lat1, lon1)
        forecast1 = five_day_forcast(lat1, lon1)

        # Now call GetWeatherData(lat, lon)
    else:
        st.warning("No matching cities found.")

    compare = st.checkbox("Compare with another city?")
    selected_city2 = None
    weather2 = None
    forecast2 = None

    if compare:
        with col2:
            city2_input = st.text_input("Enter second city")

            if city2_input:
                matches2 = find_matching_cities(city2_input)

                if matches2:
                 city_names2 = [
                      f"{m.get('city_name')}, {m.get('state_name', '')}, {m.get('country_name')}".strip(', ')
                       for m in matches2
                 ]
                selected_city_str2 = st.selectbox("Choose a second city:", city_names2, key="city2_select")
                selected_city2 = matches2[city_names2.index(selected_city_str2)]

                lat2, lon2 = selected_city2['lat'], selected_city2['lon']
                #st.success(f"You selected: {selected_city_str2}")
                weather2 = current_weather_data(lat2, lon2)
                forecast2 = five_day_forcast(lat2, lon2)
            else:
                st.warning("No matching cities found.")

#add map

if weather1:
        # Determine map center
        center_lat = weather1["lat"]
        center_lon = weather1["lon"]

        if weather2:
            center_lat = (weather1["lat"] + weather2["lat"]) / 2
            center_lon = (weather1["lon"] + weather2["lon"]) / 2

        # Create folium map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4)

        # Add first city marker
        folium.Marker(
            [weather1["lat"], weather1["lon"]],
            popup=f"{weather1['city']}, {weather1['country']} - {weather1['temperature']}°C",
            tooltip=weather1["city"],
            icon=folium.Icon(color="blue", icon="cloud")
        ).add_to(m)

        # Add second city marker (if exists)
        if weather2:
            folium.Marker(
                [weather2["lat"], weather2["lon"]],
                popup=f"{weather2['city']}, {weather2['country']} - {weather2['temperature']}°C",
                tooltip=weather2["city"],
                icon=folium.Icon(color="green", icon="cloud")
            ).add_to(m)

        # Display the map below both city inputs
        with st.container():
            folium_static(m, width=1000, height=250)


# add metrics
if weather1 and weather2:
  col1, spacer, col2 = st.columns([1, 0.2, 1])

  with col1:

      icon_col, info_col = st.columns([1, 4])

      with icon_col:
          st.image(f"http://openweathermap.org/img/wn/{weather1['icon']}@2x.png", width=60)

      with info_col:
          st.subheader(f"{weather1['city']}, {weather1['country']}")

      st.subheader("Local Time",weather1['local_timestamp'].strftime("%Y-%m-%d %H:%M:%S"))

      # Now below the nested row, show other metrics in two columns
      metric_col1, metric_col2 = st.columns(2)

      with metric_col1:
          st.metric("Current temperature", f"{weather1['temperature']}°C")
          st.metric("Min Temp", f"{weather1['temp_min']}°C")
          st.metric("Humidity", f"{weather1['humidity']}%")

      with metric_col2:
          st.metric("Feels Like", f"{weather1['feels_like']}°C")
          st.metric("Max Temp", f"{weather1['temp_max']}°C")

      st.write(f"**{weather1['description'].capitalize()}**")

  with col2:

      icon_col, info_col = st.columns([1, 4])

      with icon_col:
          st.image(f"http://openweathermap.org/img/wn/{weather2['icon']}@2x.png", width=60)

      with info_col:
          st.subheader(f"{weather2['city']}, {weather2['country']}")

      st.subheader("Local Time", weather2['local_timestamp'].strftime("%Y-%m-%d %H:%M:%S"))

      # Now below the nested row, show other metrics in two columns
      metric_col1, metric_col2 = st.columns(2)

      with metric_col1:
          st.metric("Current temperature", f"{weather2['temperature']}°C")
          st.metric("Min Temp", f"{weather2['temp_min']}°C")
          st.metric("Humidity", f"{weather2['humidity']}%")

      with metric_col2:
          st.metric("Feels Like", f"{weather2['feels_like']}°C")
          st.metric("Max Temp", f"{weather2['temp_max']}°C")

      st.write(f"**{weather2['description'].capitalize()}**")


elif weather1:
        icon_col, info_col = st.columns([1, 4])

        with icon_col:
            st.image(f"http://openweathermap.org/img/wn/{weather1['icon']}@2x.png", width=60)

        with info_col:
            st.subheader(f"{weather1['city']}, {weather1['country']}")

        st.subheader("Local Time", weather1['local_timestamp'].strftime("%Y-%m-%d %H:%M:%S"))

        # Now below the nested row, show other metrics in two columns
        metric_col1, metric_col2 = st.columns(2)

        with metric_col1:
            st.metric("Current temperature", f"{weather1['temperature']}°C")
            st.metric("Min Temp", f"{weather1['temp_min']}°C")
            st.metric("Humidity", f"{weather1['humidity']}%")

        with metric_col2:
            st.metric("Feels Like", f"{weather1['feels_like']}°C")
            st.metric("Max Temp", f"{weather1['temp_max']}°C")

        st.write(f"**{weather1['description'].capitalize()}**")



def build_forecast_dataframe(forecast_data):
    rows = []
    for day in forecast_data["forecast"]:
        #icon_url = f"http://openweathermap.org/img/wn/{day['icon']}@2x.png"
        rows.append({
            "Date": f"{day['date']} {day['time']}",
            #"Icon": f"![icon]({icon_url})",
            "Temp (°C)": day["temp"],
            "Humidity (%)": day["humidity"],
            "Wind Speed": day["wind_speed"],
            "Description": day["description"].capitalize()
        })
    return pd.DataFrame(rows)


if forecast1 and forecast2:
  col1, spacer, col2 = st.columns([1, 0.2, 1])

  with col1:
    df1 = build_forecast_dataframe(forecast1)
    st.subheader("Forcast for ",f"{weather1['city']}, {weather1['country']}")
    st.dataframe(df1)

  with col2:
    df2 = build_forecast_dataframe(forecast2)
    st.subheader("Forcast for ",f"{weather2['city']}, {weather2['country']}")
    st.dataframe(df2)


elif forecast1:
    df1 = build_forecast_dataframe(forecast1)
    st.subheader("Forcast for ",f"{weather1['city']}, {weather1['country']}")
    st.dataframe(df1)
