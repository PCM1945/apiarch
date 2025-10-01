from typing import Dict, Any
import aiohttp
import json
import asyncio
import logging
from interface.requestProcessor import RequestProcessor

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom processor example
class CustomRequestProcessor(RequestProcessor):
    """Example of a custom request processor."""
    
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Custom processing logic."""
        correlation_id = payload.get("correlation_id")
        
        # Custom processing logic here
        result = {
            "message": f"Custom processing for {correlation_id}",
            "processed_at": asyncio.get_event_loop().time(),
            "payload": payload
        }
        
        logger.info(f"Custom processing completed for {correlation_id}")
        return result