import base64
from PIL import Image
import os
import base64
from io import BytesIO

def add_logo():
    with open("assets/HackademixLogo.png", "rb") as f:
        image_data = f.read()
    # Resize the image
    image = Image.open(BytesIO(image_data))
    width, height = image.size
    image = image.resize((285, 60), Image.LANCZOS) 
    # Convert the image to a base64-encoded string
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode()
    return encoded_image
