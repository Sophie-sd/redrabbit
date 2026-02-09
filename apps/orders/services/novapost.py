"""
Wrapper для Nova Poshta API v2.0 (api.novaposhta.ua)
"""
import requests
import logging
from typing import List, Dict, Optional
from django.conf import settings


logger = logging.getLogger(__name__)


class NovaPostService:
    """Wrapper для Nova Poshta API v2.0"""
    
    API_URL = "https://api.novaposhta.ua/v2.0/json"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def _request(self, model_name: str, called_method: str, properties: dict = None) -> dict:
        """
        Виконує запит до Nova Poshta API v2.0
        
        Args:
            model_name: Назва моделі (наприклад, "Address", "AddressGeneral")
            called_method: Назва методу (наприклад, "getCities", "getWarehouses")
            properties: Параметри запиту
        """
        payload = {
            "apiKey": self.api_key,
            "modelName": model_name,
            "calledMethod": called_method,
            "methodProperties": properties or {}
        }
        
        try:
            response = requests.post(
                self.API_URL,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                logger.warning(f"API error: {result.get('errors', [])}")
                return {'success': False, 'data': []}
            
            return result
        except Exception as e:
            logger.error(f"Nova Poshta API request failed: {called_method}, error: {e}")
            return {'success': False, 'data': []}
    
    def search_cities(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Пошук міст для autocomplete
        
        API: Address.getCities
        Returns: список міст з Ref та Description
        """
        try:
            result = self._request(
                "Address",
                "getCities",
                {"FindByString": query, "Limit": limit}
            )
            return result.get('data', [])
        except Exception as e:
            logger.error(f"City search failed for query='{query}': {e}")
            return []
    
    def get_warehouses(self, city_ref: str, limit: int = 100) -> List[Dict]:
        """
        Отримує відділення/поштомати для обраного міста
        
        API: AddressGeneral.getWarehouses
        Args:
            city_ref: Ref міста з методу getCities
            limit: Максимальна кількість результатів
        Returns: список відділень з Ref, Description, Address тощо
        """
        try:
            result = self._request(
                "AddressGeneral",
                "getWarehouses",
                {"CityRef": city_ref, "Limit": limit}
            )
            return result.get('data', [])
        except Exception as e:
            logger.error(f"Warehouses fetch failed for city_ref='{city_ref}': {e}")
            return []
    
    def create_shipment(self, order_data: dict) -> Dict:
        """
        Створення ТТН (майбутня функція для адмінки)
        
        API: InternetDocument.save
        """
        try:
            result = self._request(
                "InternetDocument",
                "save",
                order_data
            )
            return result
        except Exception as e:
            logger.error(f"Shipment creation failed: {e}")
            raise
