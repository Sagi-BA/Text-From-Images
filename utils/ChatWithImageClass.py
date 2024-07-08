import base64
import os
import re
from io import BytesIO
import requests
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatWithImageClass: 
    def __init__(self, api_key=os.getenv('GOOGLE_CLOUD_VISION_API_KEY')):
        self.model_name = "Salesforce/blip-image-captioning-large"
        # self.processor = BlipProcessor.from_pretrained(self.model_name)
        # self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
        self.api_key = api_key         

    def clean_text(self, text):
        # Keep only Hebrew, English characters, and numbers
        text = re.sub(r'[^א-תA-Za-z0-9\s]', '', text)
        # Remove excessive whitespace
        text = re.sub(r'[\s]+', ' ', text).strip()
        return text
    
    def get_image_captions(self, image_url):
        try:
            image = self.get_image_from_url(image_url)
            if image:
                description = self.get_image_description(image)
                return description
            else:
                return False
        except Exception as e:        
            print(f"Failed to return message: {str(e)}") 
            return False

    def get_image_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Failed to download image: {str(e)}") 
            return False   

    def get_image_description(self, image):
        try:
            input_data = self.processor(image, return_tensors="pt")
            out = self.model.generate(**input_data, max_new_tokens=20)
            description = self.processor.decode(out[0], skip_special_tokens=True)
            return description
        except Exception as e:        
            print(f"Failed to get image description: {str(e)}") 
            return False

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
            return self.clean_text(text)
        except Exception as e:
            print(f"Failed to extract text from image: {str(e)}")
            return False
    
if __name__ == '__main__':
    model = ChatWithImageClass()
    description = model.get_image_captions('https://t4.ftcdn.net/jpg/05/01/84/43/360_F_501844341_cA5xxjYPd4hL19XMImLMj5sCnP1Ib4hI.jpg')
    print(description)
