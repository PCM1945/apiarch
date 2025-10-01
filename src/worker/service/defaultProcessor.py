from typing import Dict, Any
import aiohttp
import json
import logging
from interface.requestProcessor import RequestProcessor

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DefaultRequestProcessor(RequestProcessor):
    """Default implementation of RequestProcessor that makes HTTP API calls."""
    
    def __init__(self, base_api_url: str = "http://localhost:8009"):
        self.base_api_url = base_api_url

    async def process_request(self, payload: Dict[str, Any], kind: str) -> Dict[str, Any]:
        """
        Process request by making HTTP call to API.
        
        Args:
            payload: Request payload containing correlation_id and api_url
            
        Returns:
            Response data from API or error information
        """
        correlation_id = payload.get("correlation_id")
        api_url = payload.get("api_url")
        
        api_payload = {
            "message": f"correlation_id: {correlation_id}",
            "sender": correlation_id
        }
        
        logger.info(f"Processing request with correlation ID: {correlation_id}, calling API {api_url}")
        
        try:
            logger.info(f"Making request to {self.base_api_url + api_url}")
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                if kind == "GET":
                    async with session.get(
                        self.base_api_url + api_url,
                        params=api_payload
                    ) as resp:
                        data = await resp.json()
                        logger.info(f"Received data from API: {data}")
                        return data
                if kind == "POST":
                    async with session.post(
                        self.base_api_url + api_url,
                        data=json.dumps(api_payload),
                        headers=headers
                    ) as resp:
                        data = await resp.json()
                        logger.info(f"Received data from API: {data}")
                        return data
                else:
                    raise ValueError(f"Unsupported HTTP method: {kind}")
                
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return {"error": str(e)}
