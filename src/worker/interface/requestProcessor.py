import abc
from typing import Dict, Any

class RequestProcessor(abc.ABC):
    """Abstract base class for processing requests."""
    
    @abc.abstractmethod
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process the incoming request and return a response."""
        pass