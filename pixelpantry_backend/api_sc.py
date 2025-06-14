import requests
import sys
import pandas as pd
import os

# Read command-line arguments
latitude = sys.argv[1]
longitude = sys.argv[2]
start_date = sys.argv[3]
end_date = sys.argv[4]

# Open-Meteo API URL
url = "https://archive-api.open-meteo.com/v1/archive"

# API parameters
params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": start_date,
    "end_date": end_date,
    "timezone": "auto",
    "daily": ["temperature_2m_min", "temperature_2m_max", "temperature_2m_mean", "precipitation_sum", "rain_sum"],
    "temperature_unit": "celsius",
    "wind_speed_unit": "kmh",
    "precipitation_unit": "mm",
    "timeformat": "iso8601"
}

# Fetch data from Open-Meteo API
response = requests.get(url, params=params)
data = response.json()

# Extract dates
dates = data["daily"]["time"]

# Extract weather data
weather_data = {
    "time": dates,
    "temperature_2m_min (°C)": data["daily"]["temperature_2m_min"],
    "temperature_2m_max (°C)": data["daily"]["temperature_2m_max"],
    "temperature_2m_mean (°C)": data["daily"]["temperature_2m_mean"],
    "precipitation_sum (mm)": data["daily"]["precipitation_sum"],
    "rain_sum (mm)": data["daily"]["rain_sum"]
}

# Convert to DataFrame
df = pd.DataFrame(weather_data)

# Set download folder
download_dir = os.getcwd()
file_name = f"weather_data_{latitude}_{longitude}_{start_date}_{end_date}.csv"
file_path = os.path.join(download_dir, file_name)

# Save as CSV
df.to_csv(file_path, index=False)

print(f" Weather data saved as {file_name}")
