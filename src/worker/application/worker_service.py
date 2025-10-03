from app.domain.interfaces import Message, MessageBroker
from app.domain.use_cases import ProcessRequestUseCase


class WorkerService:
    """Orchestrates message consumption and delegates processing."""

    def __init__(self, broker: MessageBroker, parity_key: str):
        self.broker = broker
        self.parity_key = parity_key
        self.use_case = ProcessRequestUseCase()

    async def start(self):
        """Starts the worker and registers callback."""
        await self.broker.consume(self._handle_message)

    async def _handle_message(self, message: Message):
        print(f"[Worker {self.parity_key}] Received: {message.body}")

        # Execute business logic
        result = await self.use_case.execute(message.body)

        # Publish response
        response = Message(result, message.correlation_id, message.reply_to)
        await self.broker.publish(response, routing_key=message.reply_to)

        print(f"[Worker {self.parity_key}] Sent response: {result}")
