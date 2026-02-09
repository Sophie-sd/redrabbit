"""
Wrapper для Nova Post API v1.0 (api.novapost.com)
НЕ використовує novaposhta-python-client через застарілий API v2.0
"""
import requests
import logging
from cachetools import TTLCache
from typing import List, Dict, Optional
from django.conf import settings


logger = logging.getLogger(__name__)


class NovaPostService:
    """Wrapper для Nova Post API v1.0"""
    
    API_URL = "https://api.novapost.com/v1.0"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._jwt_cache = TTLCache(maxsize=1, ttl=3000)  # 50 хвилин (токен живе 60)
    
    def _get_jwt(self) -> str:
        """Генерує JWT токен (кешується на 50 хв)"""
        if 'jwt' in self._jwt_cache:
            return self._jwt_cache['jwt']
        
        try:
            response = requests.get(
                f"{self.API_URL}/clients/authorization",
                params={'apiKey': self.api_key},
                timeout=10
            )
            response.raise_for_status()
            jwt = response.json()['jwt']
            self._jwt_cache['jwt'] = jwt
            logger.info("Nova Post JWT token generated successfully")
            return jwt
        except Exception as e:
            logger.error(f"Failed to get Nova Post JWT: {e}")
            raise
    
    def _request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Виконує запит з JWT-аутентифікацією"""
        jwt = self._get_jwt()
        headers = {'Authorization': f'Bearer {jwt}'}
        
        try:
            if method == 'GET':
                response = requests.get(f"{self.API_URL}{endpoint}", headers=headers, timeout=10)
            else:
                response = requests.post(f"{self.API_URL}{endpoint}", headers=headers, json=data, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Nova Post API request failed: {endpoint}, error: {e}")
            raise
    
    def search_cities(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Пошук міст для autocomplete
        
        ВАЖЛИВО: Endpoint потрібно уточнити в офіційній документації Nova Post v1.0!
        Можливі варіанти:
        - /dictionaries/cities
        - /address/search-cities
        - /settlements/search
        """
        try:
            # Тимчасовий endpoint (потребує уточнення!)
            return self._request(f'/dictionaries/cities?query={query}&limit={limit}')
        except Exception as e:
            logger.error(f"City search failed for query='{query}': {e}")
            return []
    
    def get_warehouses(self, city_ref: str, limit: int = 100) -> List[Dict]:
        """
        Відділення/поштомати для обраного міста
        
        ВАЖЛИВО: Endpoint потрібно уточнити в документації!
        """
        try:
            return self._request(f'/dictionaries/warehouses?cityRef={city_ref}&limit={limit}')
        except Exception as e:
            logger.error(f"Warehouses fetch failed for city_ref='{city_ref}': {e}")
            return []
    
    def create_shipment(self, order_data: dict) -> Dict:
        """
        Створення ТТН (майбутня функція для адмінки)
        """
        try:
            return self._request('/shipments', method='POST', data=order_data)
        except Exception as e:
            logger.error(f"Shipment creation failed: {e}")
            raise
