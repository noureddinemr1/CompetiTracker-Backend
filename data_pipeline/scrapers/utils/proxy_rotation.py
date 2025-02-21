import random
import requests

class ProxyRotation:
    def __init__(self):
        self.proxies = self._load_proxies()
        
    def _load_proxies(self):
        # Example: Load from external API or file
        try:
            response = requests.get('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http')
            return response.text.splitlines()
        except:
            return [
                'http://proxy1:port',
                'http://proxy2:port',
                # Add fallback proxies
            ]
    
    def get_random_proxy(self):
        return random.choice(self.proxies)