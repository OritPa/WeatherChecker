import requests

API_KEY = "7ca1b7fdc9a1b1da782c8929f3e2d595"  # Replace with your real API key
CITY = "London"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

response = requests.get(URL)

if response.status_code == 200:
    data = response.json()
    temperature = data['main']['temp']
    weather = data['weather'][0]['description']
    print(f"Current temperature in {CITY}: {temperature}°C")
    print(f"Weather: {weather}")
else:
    print(f"Failed to retrieve data: {response.status_code} - {response.text}")



import requests

API_KEY = "your_api_key"
CITY = "London"
GEO_URL = f"http://api.openweathermap.org/geo/1.0/direct?q={CITY}&limit=1&appid={API_KEY}"

response = requests.get(GEO_URL)
location = response.json()[0]
lat = location["lat"]
lon = location["lon"]



WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
weather = requests.get(WEATHER_URL).json()



FORECAST_URL = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
forecast = requests.get(FORECAST_URL).json()



AIR_URL = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
air = requests.get(AIR_URL).json()



ONECALL_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
onecall = requests.get(ONECALL_URL).json()