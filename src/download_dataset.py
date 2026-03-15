import os
from dotenv import load_dotenv
import requests
load_dotenv() 

key = os.getenv('EBIRD_API_KEY')


url = "https://api.ebird.org/v2/product/top100/US/2025/01/01"

payload={}
headers = {
        'x-ebirdapitoken':key
        }

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

