import requests
import os
from anthropic import Anthropic
from PIL import Image
import io
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


def analyze_flares(flares):
    
    client = Anthropic()
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens= 1000,
        system="""You are a planetary scientist working for NASA. Your role is to detect solar flares that may pose a threat to earth and current space programs in orbit. You need to identify any flares of types X and report back the intensity and origin. You also need to consider events that are linked to the flare. You need to produce a structured data output that includes: threat level, affected systems, and recommended actions. You support mission control operations, keep communication direct and professional - brevity is best. If no X class flares or linked events are detected, respond with: "No anomalies detected. All systems nominal.""",
        messages=[
            {"role": "user", "content": f"Analyze the following solar flare data:\n\n{flares}"}
        ]
    )
    
    return message.content[0].text


analysis = analyze_flares(flares)
print("=== MISSION CONTROL ANOMALY REPORT ===")
print(analysis)

def get_solar_image(date):  
    metadata_response = requests.get(
        f"https://api.helioviewer.org/v2/getClosestImage/?date={date}T00:00:00.000Z&sourceId=10"
    )
    data = metadata_response.json()
    imageId = data["id"]
    image_response = requests.get(
        f"https://api.helioviewer.org/v2/getJP2Image/?id={imageId}"
    )
    content = image_response.content
    img = Image.open(io.BytesIO(content))
    img = img.convert("RGB")
    output = io.BytesIO()
    img.save(output, format="JPEG")
    jpg_bytes = output.getvalue()
    
    return jpg_bytes

    