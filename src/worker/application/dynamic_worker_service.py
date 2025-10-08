import json
import logging
from domain.interfaces import Message, MessageBroker
from application.registry import UseCaseRegistry
from utils.logger import AppLogger

logger = AppLogger(__name__)

class WorkerService:
    """Processes messages dynamically based on the routing_key."""

    def __init__(self, broker: MessageBroker):
        self.broker = broker

    async def start(self):
        logger.info("Dynamic worker started. Waiting for messages...")
        await self.broker.consume(self._handle_message)

    async def _handle_message(self, message: Message):

        logger.info(f"[Worker] Message received: {message}")

        try:
            use_case = UseCaseRegistry.get_use_case(message.routing_key)

            result = await use_case.execute(message.body)
            
            response = Message(
                body=json.dumps(result),
                correlation_id=message.correlation_id,
                reply_to=message.reply_to
            )

            await self.broker.publish(response, routing_key=message.reply_to)

            logger.info(f"[Worker] Response sent to {message.reply_to}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")