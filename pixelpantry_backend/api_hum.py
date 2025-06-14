import requests
import sys
import pandas as pd
import os
import time

# Read command-line arguments
latitude = sys.argv[1]
longitude = sys.argv[2]
start_date = sys.argv[3]
end_date = sys.argv[4]

# Open-Meteo API URL for historical data
url = "https://archive-api.open-meteo.com/v1/archive"

# API parameters - requesting hourly relative humidity
params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": start_date,
    "end_date": end_date,
    "timezone": "auto",
    "hourly": ["relative_humidity_2m"],
    "temperature_unit": "celsius",
    "wind_speed_unit": "kmh",
    "precipitation_unit": "mm",
    "timeformat": "iso8601"
}

try:
    # Fetch data from Open-Meteo API
    print(f"Fetching humidity data for coordinates: {latitude}, {longitude}")
    print(f"Date range: {start_date} to {end_date}")
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise exception for HTTP errors
    data = response.json()
    
    # Extract times and humidity values
    times = data["hourly"]["time"]
    humidity_values = data["hourly"]["relative_humidity_2m"]
    
    # Create DataFrame with same column naming format as the website's CSV download
    weather_data = {
        "time": times,
        "relative_humidity_2m (%)": humidity_values
    }
    
    df = pd.DataFrame(weather_data)
    
    # Set download folder
    download_dir = os.getcwd()
    file_name = f"humidity_data_{latitude}_{longitude}_{start_date}_{end_date}.csv"
    file_path = os.path.join(download_dir, file_name)
    
    # Save as CSV
    df.to_csv(file_path, index=False)
    
    print(f"CSV file downloaded and renamed to: {file_name}")
    
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
    sys.exit(1)
except ValueError as e:
    print(f"Failed to parse JSON response: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)