import requests
import os

api_key=os.getenv("API_KEY")

def check_openai_credits(api_key):
    try:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get("https://api.openai.com/v1/usage", headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_available = data.get("data", [])[0].get("total_available")
            print(f"Total credits available: {total_available} credits")
        else:
            print(f"Failed to retrieve credits. Status code: {response.status_code}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



# Uso de la función
api_key = api_key # Reemplaza con tu clave de API de OpenAI
check_openai_credits(api_key)
