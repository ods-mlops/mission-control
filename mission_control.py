import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Read your NASA key from .env
nasa_key = os.getenv("NASA_API_KEY")

def get_solar_flares():
    url = f"https://api.nasa.gov/DONKI/FLR?startDate=2024-01-01&endDate=2024-01-31&api_key={nasa_key}"
    
    response = requests.get(url)
    data = response.json()

    cleaned = []
    for event in data:
        cleaned.append({
            "flrID": event["flrID"],
            "classType": event["classType"],
            "beginTime": event["beginTime"],
            "peakTime": event["peakTime"],
            "sourceLocation": event["sourceLocation"],
            "linkedEvents": event["linkedEvents"]
        })
    
    return cleaned

# Call the function and store the result
flares = get_solar_flares()

# Print to verify it worked
print(f"Total flares: {len(flares)}")
print("\nFirst cleaned event:")
print(flares[0])
