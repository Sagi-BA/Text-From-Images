import base64
import os
import re
from io import BytesIO
import logging
from urllib.parse import urlparse
import requests, os
from pathlib import Path
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from google.cloud import vision
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatWithImageClass: 
    def __init__(self, api_key=os.getenv('GOOGLE_CLOUD_VISION_API_KEY')):
        self.model_name = "Salesforce/blip-image-captioning-large"
        self.processor = BlipProcessor.from_pretrained(self.model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key         

    def clean_text(self, text):
        # Keep only Hebrew, English characters, and numbers
        text = re.sub(r'[^א-תA-Za-z0-9\s]', '', text)
        # Remove excessive whitespace
        text = re.sub(r'[\s]+', ' ', text).strip()
        return text
    
    def get_image_captions(self, image_url):
        print('sagi')
        print(type(image_url))
        try:
            image = self.get_image_from_url(image_url)
            return self.get_image_description(image)        
            
        except Exception as e:        
            logging.error(f"Failed to return message: " + str(e)) 
            return False

    def get_image_from_url(self, url):
        response = requests.get(url)

        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            print(f"Failed to download image. Status code: {response.status_code}") 
            return False   

    def get_image_description(self, image_url):
        try:
            input = self.processor(image_url, return_tensors="pt")
            out = self.model.generate(**input, max_new_tokens=20)
            description = self.processor.decode(out[0], skip_special_tokens=True)
        except Exception as e:        
            logging.error(f"Failed to return message: " + str(e)) 
            return False

        return description

    def detect_text_with_googleapi(self, image_path):
        
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            image_base64 = base64.b64encode(content).decode('utf-8')

            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "TEXT_DETECTION"}]
                    }
                ]
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if 'textAnnotations' not in result['responses'][0]:
                return ""

            text = result['responses'][0]['textAnnotations'][0]['description']

            # cleaned_text = self.clean_text(text)
        except Exception as e:
            logging.error(f"Failed to extract text from image: " + str(e))
            return False
        
        print('Start detect_text_with_googleapi')
        return text
    
if __name__ == '__main__':
    model = ChatWithImageClass()
    description = model.get_image_captions('https://t4.ftcdn.net/jpg/05/01/84/43/360_F_501844341_cA5xxjYPd4hL19XMImLMj5sCnP1Ib4hI.jpg')
    print(description)

    # Example usage of the new text extraction method
    text = model.extract_text_from_image('/path/to/your/image.jpg')
    print(text)