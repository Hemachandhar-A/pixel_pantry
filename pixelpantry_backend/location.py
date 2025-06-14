import requests
import sys


GOOGLE_API_KEY = "AIzaSyDNm8Y1miiqufQl-SnsRj842IwUXLMvnME"  # Replace with your actual API key

# Step 1: Get coordinates from Google Geolocation API
geo_location_url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_API_KEY}"

geo_response = requests.post(geo_location_url, json={})
geo_data = geo_response.json()

lat = geo_data.get('location', {}).get('lat')
lng = geo_data.get('location', {}).get('lng')

if not lat or not lng:
    print("ERROR: Could not fetch lat/lng from Google Geolocation API")
    sys.exit(1)

# Step 2: Reverse geocode with Google Maps API to get the state
geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={GOOGLE_API_KEY}"
reverse_response = requests.get(geocode_url)
reverse_data = reverse_response.json()

if reverse_data['status'] == 'OK':
    components = reverse_data['results'][0]['address_components']
    state = next((comp['long_name'] for comp in components if "administrative_area_level_1" in comp['types']), None)
    print(f"{lat},{lng},{state}")

else:
    print(f"ERROR: {reverse_data.get('error_message', 'Unknown reverse geocoding error')}")
    sys.exit(1)

 