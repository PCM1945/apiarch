import aio_pika
from domain.interfaces import Message, MessageBroker


class RabbitMQWorker(MessageBroker):
    """Adapter concreto para RabbitMQ."""

    def __init__(self, amqp_url: str, parity_key: str,
                 requests_exchange: str = "requests_exchange",
                 responses_exchange: str = "responses_exchange"):
        self.amqp_url = amqp_url
        self.parity_key = parity_key
        self.requests_exchange_name = requests_exchange
        self.responses_exchange_name = responses_exchange

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

        self.requests_exchange = await self.channel.declare_exchange(
            self.requests_exchange_name, aio_pika.ExchangeType.TOPIC
        )
        self.responses_exchange = await self.channel.declare_exchange(
            self.responses_exchange_name, aio_pika.ExchangeType.TOPIC
        )

        self.queue = await self.channel.declare_queue(f"worker.{self.parity_key}", durable=True)
        await self.queue.bind(self.requests_exchange, routing_key=f"process.{self.parity_key}")

    async def publish(self, message: Message, routing_key: str):
        response = aio_pika.Message(
            body=message.body.encode(),
            correlation_id=message.correlation_id,
        )
        await self.responses_exchange.publish(response, routing_key=routing_key)

    async def consume(self, callback):
        async with self.queue.iterator() as queue_iter:
            async for msg in queue_iter:
                async with msg.process():
                    message = Message(
                        body=msg.body.decode(),
                        correlation_id=msg.correlation_id,
                        reply_to=msg.reply_to
                    )
                    await callback(message)
