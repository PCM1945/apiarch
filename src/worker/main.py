import asyncio
from application.worker_service import WorkerService
from infrastructure.rabbitmq_worker import RabbitMQWorker


async def main():
    broker = RabbitMQWorker(amqp_url="amqp://guest:guest@localhost/", parity_key="42")
    await broker.connect()

    service = WorkerService(broker, parity_key="42")
    print("[*] Worker started. Waiting for messages...")
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())