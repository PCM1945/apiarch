import asyncio
import logging
from infrastructure.dynamic_worker import DynamicWorker as RabbitMQWorker
from application.dynamic_worker_service import WorkerService

"""Dynamic worker that processes messages according to the routing_key."""
"""Here you choose which routing keys this worker should listen to — can be all or just some."""

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
