# image_gen.py
import requests

CRAIYON_API_URL = "https://api.craiyon.com/generate"  # Craiyon's unofficial API URL

def generate_image(prompt):
    try:
        # Prepare the payload
        response = requests.post(CRAIYON_API_URL, json={"prompt": prompt})
        
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            if "images" in data:
                return data["images"][0]  # Return the first image from the response
            else:
                print("Error: No images found in the response.")
                return None
        else:
            print(f"[Craiyon] Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Craiyon] Error: {e}")
        return None
