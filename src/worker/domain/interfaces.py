from abc import ABC, abstractmethod


class Message:
    """Simple entity that carries request data."""
    def __init__(self, body: str, correlation_id: str, reply_to: str):
        self.body = body
        self.correlation_id = correlation_id
        self.reply_to = reply_to


class MessageBroker(ABC):
    """Messaging port - does not depend on RabbitMQ."""
    @abstractmethod
    async def publish(self, message: Message, routing_key: str):
        pass

    @abstractmethod
    async def consume(self, callback):
        pass