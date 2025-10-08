import aio_pika
from aio_pika import ExchangeType
from domain.interfaces import Message, MessageBroker
from utils.logger import AppLogger

logger = AppLogger(__name__)


class DynamicWorker(MessageBroker):
    """RabbitMQ adapter that listens to multiple routing keys."""

    def __init__(self, amqp_url: str, routing_keys: list[str]):
        
        self.amqp_url = amqp_url
        self.routing_keys = routing_keys
        self.connection = None
        self.channel = None

        self.task_exchange = "task_exchange"
        self.task_exchange = "task_exchange"
        self.task_queue_name = "task_queue"

    async def connect(self):
        """Establishes connection with RabbitMQ and configures queues and exchanges dynamically."""
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

        self.task_exchange = await self.channel.declare_exchange(self.task_exchange, ExchangeType.TOPIC, durable=True)

        self.task_queue = await self.channel.declare_queue(
            self.task_queue_name, durable=True,
            arguments={
                "x-message-ttl": 30000,
                "x-dead-letter-exchange": "dlx_exchange",
                "x-dead-letter-routing-key": "dlx_key"
            }
        )

        # self.dlx_exchange = await self.channel.declare_exchange("dlx_exchange", ExchangeType.FANOUT, durable=True)
        # self.dlx_queue = await self.channel.declare_queue("dlx_queue", durable=True)
        # await self.dlx_queue.bind(self.dlx_exchange)

        for key in self.routing_keys:
            await self.task_queue.bind(self.task_exchange, routing_key=f"task.{key}")

    async def publish(self, message: Message, routing_key: str):
        response = aio_pika.Message(
            body=message.body.encode(),
            correlation_id=message.correlation_id,
        )
        await self.task_exchange.publish(response, routing_key=routing_key)

    async def consume(self, callback):
        async with self.task_queue.iterator() as queue_iter:
            async for msg in queue_iter:
                async with msg.process():
                    logger.info(f"Crude Message received: {msg}") 
                    message = Message(
                        body=msg.body.decode(),
                        routing_key=msg.routing_key,
                        correlation_id=msg.correlation_id,
                        reply_to=msg.reply_to,
                    )
                    await callback(message)
