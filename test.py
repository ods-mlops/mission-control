import requests
from PIL import Image
from PIL import features
import io


def get_solar_image(date):  
    response = requests.get(
        f"https://api.helioviewer.org/v2/getClosestImage/?date={date}T00:00:00.000Z&sourceId=10"
    )
    data = response.json()
    imageId = data["id"]
    response = requests.get(
        f"https://api.helioviewer.org/v2/getJP2Image/?id={imageId}"
    )
    content = response.content
    img = Image.open(io.BytesIO(content))
    img = img.convert("RGB")
    output = io.BytesIO()
    img.save(output, format="JPEG")
    jpg_bytes = output.getvalue()
    
    return jpg_bytes


