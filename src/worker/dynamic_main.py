import asyncio
import logging
from infrastructure.dynamic_worker import DynamicWorker as RabbitMQWorker
from application.dynamic_worker_service import WorkerService

"""Worker dinâmico que processa mensagens conforme o routing_key."""
"""Aqui você escolhe quais routing keys esse worker deve escutar — pode ser todas ou apenas algumas."""

async def main():
    routing_keys = [
        "ai.summary.generate_summary_text",
        "ai.summary.generate_summary_miro",
        "app.show_message"
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
