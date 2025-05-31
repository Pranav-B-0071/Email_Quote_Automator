import requests
import json

def create_quotes(my_api_key:str)-> str:
    api_url = 'https://api.api-ninjas.com/v1/quotes'
    response = requests.get(api_url, headers={'X-Api-Key': my_api_key})
    if response.status_code == requests.codes.ok:
        output = response.json()
        return output[0]["quote"]
    else:
        print("Error:", response.status_code, response.text)
        return None
