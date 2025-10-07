from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class Message(BaseModel):
    """Simple entity that carries request data."""
    body: str
    correlation_id: str
    reply_to: str
    header: Optional[dict] = {}
    response: Optional[dict] = {}


class MessageBroker(ABC):
    """Messaging port - does not depend on RabbitMQ."""
    @abstractmethod
    async def publish(self, message: Message, routing_key: str):
        pass

    @abstractmethod
    async def consume(self, callback):
        pass