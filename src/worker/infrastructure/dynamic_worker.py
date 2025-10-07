import aio_pika
from aio_pika import ExchangeType
from domain.interfaces import Message, MessageBroker

class DynamicWorker(MessageBroker):
    """Adapter RabbitMQ que escuta múltiplas routing keys."""

    def __init__(self, amqp_url: str, routing_keys: list[str]):
        
        self.amqp_url = amqp_url
        self.routing_keys = routing_keys
        self.connection = None
        self.channel = None

        self.task_exchange = "task_exchange"
        self.task_exchange = "task_exchange"
        self.task_queue_name = "task_queue"

    async def connect(self):
        """Estabelece conexão com RabbitMQ e configura filas e exchanges dinamicamente."""
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

        self.request_exchange = await self.channel.declare_exchange(
            self.task_exchange, ExchangeType.TOPIC
        )

        self.task_exchange = await self.channel.declare_exchange(self.task_exchange, ExchangeType.TOPIC)

        self.queue = await self.channel.declare_queue(self.task_queue_name, durable=True)

        for key in self.routing_keys:
            await self.queue.bind(self.task_exchange, routing_key=f"task.{key}")

    async def publish(self, message: Message, routing_key: str):
        response = aio_pika.Message(
            body=message.body.encode(),
            correlation_id=message.correlation_id,
        )
        await self.exchange.publish(response, routing_key=routing_key)

    async def consume(self, callback):
        async with self.queue.iterator() as queue_iter:
            async for msg in queue_iter:
                async with msg.process():
                    message = Message(
                        body=msg.body.decode(),
                        correlation_id=msg.correlation_id or "",
                        reply_to=msg.reply_to or "",
                    )
                    await callback(message)
