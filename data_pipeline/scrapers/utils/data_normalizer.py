import re
from datetime import datetime

class DataNormalizer:
    @staticmethod
    def normalize_price(price_str):
        """Convert price strings to float"""
        if not price_str:
            return 0.0
        return float(re.sub(r'[^\d.]', '', price_str))

    @staticmethod
    def normalize_currency(currency_str):
        """Standardize currency format"""
        currency_map = {
            'DT': 'TND',
            'TND': 'TND',
            'د.ت': 'TND',
            'Dinar': 'TND',
            'Tunisian Dinar': 'TND'
        }
        return currency_map.get(currency_str.strip().upper(), 'TND')

    @staticmethod
    def normalize_date(date_str, format='%Y-%m-%d %H:%M:%S'):
        """Normalize date strings"""
        try:
            return datetime.strptime(date_str, format).isoformat()
        except:
            return datetime.now().isoformat()