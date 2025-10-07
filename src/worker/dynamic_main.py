import asyncio
import logging
from infrastructure.rabbitmq_worker import RabbitMQWorker
from application.worker_service import WorkerService

"""Worker dinâmico que processa mensagens conforme o routing_key."""
"""Aqui você escolhe quais routing keys esse worker deve escutar — pode ser todas ou apenas algumas."""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

async def main():
    routing_keys = [
        "ai.summary.generate_summary_text",
        "ai.summary.generate_summary_miro",
    ]

    broker = RabbitMQWorker(
        amqp_url="amqp://guest:guest@localhost/",
        routing_keys=routing_keys,
    )
    await broker.connect()

    worker = WorkerService(broker)
    await worker.start()

if __name__ == "__main__":
    asyncio.run(main())
