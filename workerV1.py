import aio_pika as aiopika
import json
import asyncio

RABBITMQ_HOST = 'localhost'
QUEUE_NAME  = 'worker'
RABBIT_LOGIN = 'guest'
RABBIT_PASSWORD = 'guest'

class Worker:
    async def porcess_message(self, message: aiopika.abc.AbstractIncomingMessage):

        print(f'processed: {message.body}')
        try:
            await message.ack()
        except Exception as e:
            await message.reject(requeue=True)

        return {'procecessed': message.body}
    
        



async def main():

    worker = Worker()

    # Connect to RabbitMQ
    connection = await aiopika.connect(url = f'amqp://{RABBITMQ_HOST}', password='guest', login='guest')
    channel = await connection.channel()

    # Declare the queue
    queue = await channel.declare_queue(QUEUE_NAME)

    # Start consuming messages
    print("Waiting for tasks. To exit, press CTRL+C.")
    await queue.consume(callback=worker.porcess_message)

    try:
        await asyncio.Future()  # Run indefinitely
    except asyncio.CancelledError:
        print("Worker shutting down.")
    finally:
        await connection.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped.")