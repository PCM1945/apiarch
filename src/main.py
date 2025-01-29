from fastapi import FastAPI
import asyncio
import aio_pika as aiopika
import json
from pydantic import BaseModel

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "worker"


app = FastAPI()

connection = None
channel = None

async def get_rabbitmq_channel():
    """
    Lazily initialize and return a RabbitMQ channel.
    """
    global connection, channel
    if connection is None or channel is None:
        connection = await aiopika.connect(url = f'amqp://{RABBITMQ_HOST}', password='guest', login='guest')
        channel = await connection.channel()
    return channel

#def publish_task(task_data: dict):

class RequestPrompt(BaseModel):
    message: str

@app.get('/process')
async def queue(input: RequestPrompt):
        # Get the RabbitMQ channel
    channel = await get_rabbitmq_channel()

    # Declare the queue
    await channel.declare_queue(QUEUE_NAME)

    task_data = input.model_dump_json()

    # Publish the message
    await channel.default_exchange.publish(
        aiopika.Message(task_data.encode(), delivery_mode=2),  # Make the message persistent
        routing_key=QUEUE_NAME,
    )