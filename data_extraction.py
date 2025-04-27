import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NASA_API_KEY")
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")

def fetch_neo_data():
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={START_DATE}&end_date={END_DATE}&api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    all_asteroids = []
    for date, asteroids in data['near_earth_objects'].items():
        for asteroid in asteroids:
            all_asteroids.append({
                'name': asteroid['name'],
                'close_approach_date': asteroid['close_approach_data'][0]['close_approach_date'],
                'miss_distance_km': float(asteroid['close_approach_data'][0]['miss_distance']['kilometers']),
                'velocity_km_s': float(asteroid['close_approach_data'][0]['relative_velocity']['kilometers_per_second']),
                'diameter_m': float(asteroid['estimated_diameter']['meters']['estimated_diameter_max']),
                'is_potentially_hazardous_asteroid': asteroid['is_potentially_hazardous_asteroid']
            })

    return pd.DataFrame(all_asteroids)

df_asteroids = fetch_neo_data()