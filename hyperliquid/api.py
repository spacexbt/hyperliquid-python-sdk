import json
import requests
from typing import Any, Dict, Optional

from .utils.error_handling import APIError, retry_on_failure

class API:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "https://api.hyperliquid.xyz"
        self.session = requests.Session()

    @retry_on_failure(max_retries=3)
    def post(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        """Make a POST request to the API with retry mechanism.
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            
        Returns:
            API response
            
        Raises:
            APIError: If the request fails
        """
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(
                f"API request failed: {str(e)}",
                status_code=getattr(e.response, 'status_code', None),
                response=getattr(e.response, 'text', None)
            )
        except json.JSONDecodeError as e:
            raise APIError(f"Failed to decode API response: {str(e)}")