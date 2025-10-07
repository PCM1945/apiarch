import aio_pika
from aio_pika import ExchangeType
from domain.interfaces import Message, MessageBroker


class RabbitMQWorker(MessageBroker):
    """Adapter RabbitMQ compatível com task_exchange e dlx_exchange."""

    def __init__(
        self,
        amqp_url: str,
        task_queue: str = "task_queue",
        response_queue: str = "response_queue",
        task_exchange: str = "task_exchange",
        event_exchange: str = "event_exchange",
        dlx_exchange: str = "dlx_exchange",
    ):
        self.amqp_url = amqp_url
        self.task_queue = task_queue
        self.response_queue = response_queue
        self.task_exchange_name = task_exchange
        self.event_exchange_name = event_exchange
        self.dlx_exchange_name = dlx_exchange

        self.connection = None
        self.channel = None
        self.task_exchange = None
        self.event_exchange = None
        self.queue = None

    async def connect(self):
        """Estabelece conexão e garante bindings definidos no JSON."""
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

        # Exchanges existentes (não recria, apenas garante a referência)
        self.task_exchange = await self.channel.get_exchange(self.task_exchange_name)
        self.event_exchange = await self.channel.get_exchange(self.event_exchange_name)
        self.dlx_exchange = await self.channel.get_exchange(self.dlx_exchange_name)

        # Garante a fila (sem redefinir argumentos)
        self.queue = await self.channel.get_queue(self.task_queue)

    async def consume(self, callback):
        """Consome mensagens da task_queue e entrega ao handler."""
        async with self.queue.iterator() as queue_iter:
            async for msg in queue_iter:
                async with msg.process():
                    message = Message(
                        body=msg.body.decode(),
                        correlation_id=msg.correlation_id or "",
                        reply_to=msg.reply_to or self.response_queue,
                    )
                    await callback(message)

    async def publish(self, message: Message, routing_key: str = "task_response"):
        """Publica respostas na response_queue via task_exchange."""
        response = aio_pika.Message(
            body=message.body.encode(),
            correlation_id=message.correlation_id,
        )

        await self.task_exchange.publish(response, routing_key=routing_key)

    async def publish_event(self, message: Message, routing_key: str = "event.broadcast"):
        """Permite envio de eventos para o event_exchange."""
        event = aio_pika.Message(
            body=message.body.encode(),
            correlation_id=message.correlation_id,
        )

        await self.event_exchange.publish(event, routing_key=routing_key)
