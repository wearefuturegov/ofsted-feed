
import requests


ip_check_response = requests.get('https://api64.ipify.org/?format=json')
print(ip_check_response.json())
