import requests
import os
from anthropic import Anthropic
from PIL import Image
import io
from dotenv import load_dotenv
import base64

load_dotenv()



def get_solar_flares():
    nasa_key = os.getenv("NASA_API_KEY")
   
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


# def analyze_flares(flares):
    
#     client = Anthropic()
    
#     message = client.messages.create(
#         model="claude-haiku-4-5-20251001",
#         max_tokens= 1000,
#         system="""You are a planetary scientist working for NASA. Your role is to detect solar flares that may pose a threat to earth and current space programs in orbit. You need to identify any flares of types X and report back the intensity and origin. You also need to consider events that are linked to the flare. You need to produce a structured data output that includes: threat level, affected systems, and recommended actions. You support mission control operations, keep communication direct and professional - brevity is best. If no X class flares or linked events are detected, respond with: "No anomalies detected. All systems nominal.""",
#         messages=[
#             {"role": "user", "content": f"Analyze the following solar flare data:\n\n{flares}"}
#         ]
#     )
    
#     return message.content[0].text


def get_solar_image(date):  
    metadata_response = requests.get(
        f"https://api.helioviewer.org/v2/getClosestImage/?date={date}T00:00:00.000Z&sourceId=10"
    )
    data = metadata_response.json()
    image_id = data["id"]
    image_response = requests.get(
        f"https://api.helioviewer.org/v2/getJP2Image/?id={image_id}"
    )
    content = image_response.content
    img = Image.open(io.BytesIO(content))
    img = img.convert("RGB")
    output = io.BytesIO()
    img.save(output, format="JPEG")
    jpg_bytes = output.getvalue()
    
    return jpg_bytes

def analyze_with_image(flares, jpg_bytes):
    client = Anthropic()
    
    image_data = base64.standard_b64encode(jpg_bytes).decode("utf-8")
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        system="""You are a planetary scientist working for NASA. Your role is to detect solar flares that may pose a threat to earth and current space programs in orbit. You will be provided an event and a solar image. You need to identify any flares of types X and report back the intensity and origin. You also need to consider events that are linked to the flare. You need to produce a structured data output that includes: threat level, affected systems, and recommended actions. You support mission control operations, keep communication direct and professional - brevity is best. If no X class flares or linked events are detected, respond with: No anomalies detected. All systems nominal.""",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": f"Analyze this solar image alongside the flare data:\n\n{flares}"
                }
            ]
        }]
    )
    
    return message.content[0].text

def reasoning_loop(flares, jpg_bytes):
    client = Anthropic()
    
    reasoning_image = base64.standard_b64encode(jpg_bytes).decode("utf-8")

    obs_message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system="You are a NASA specialist. You need to observe the solar data provided and report back what you see in the image and in the data provided. Keep communication professional and direct. If there are not significant solar events present report back that there is nominal solar activity. Reply in a structured way that will be easily handed off to a solar anomaly team.",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": reasoning_image
                    }
                },
                {
                    "type": "text",
                    "text": f"Analyze this solar image alongside the flare data look for significant solar activity that could have impact on missions or critical infrastucture:\n\n{flares}"
                }
            ]
        }]
    )    
    
    observation = obs_message.content[0].text

    anom_message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        system="You are a NASA Solar Anomaly Specialist. Your role is to comb through the provided report and look for dangerous events, why the event is dangerous, and note potential impacts. Provide structured output that can be handed to a rapid response team. Keep communication direct and professional. If there is not a dangerous event please report that solar activity is nominal.",
        messages=[
            {"role": "user", "content": observation}
        ]
    )

    anomalies = anom_message.content[0].text

    ra_message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1800,
        system="You are a NASA Mission Control Specialist. Your role is to identify the second order impacts if action is not taken to address the solar events described. Identify mission critical systems, communications, assets in orbit, or defense capabilities that would be hindered or damaged if action is not taken. Provided a structured output that can be provided to mission opportators. Speak Professionally and directly.",
        messages=[
            {"role": "user", "content": anomalies}
        ]
    )

    risk_assessment = ra_message.content[0].text

    fr_message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        system="You are a NASA Mission Control Specialist. Your role is to provided a prioritized list of actions that should be taken to mitigate the impacts to operational assests descibed in the risk assessment. Only report on actions that must be taken. If siutation is normal do not produce urgent actions that are not needed. Provided Professional and direct bullets of actions to take in order of priority.",
        messages=[
            {"role": "user", "content": risk_assessment}
        ]
    )

    final_report = fr_message.content[0].text

    return final_report


def main():
    solar_flares = get_solar_flares()
    solar_image = get_solar_image("2024-01-29")
    flare_analysis = reasoning_loop(solar_flares, solar_image)
    print("=== MISSION CONTROL ANOMALY REPORT ===")
    print(flare_analysis)

if __name__ == "__main__":
    main()



