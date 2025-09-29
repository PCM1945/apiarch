import asyncio
import aio_pika
import json
import uuid

RABBIT_URL = "amqp://guest:guest@localhost/"
REQUEST_QUEUE = "task_queue"

async def on_response(message: aio_pika.IncomingMessage):
    async with message.process():
        response = json.loads(message.body)
        print("Received response:", response)

async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()

    # Cria fila exclusiva para receber resposta
    callback_queue = await channel.declare_queue(name=f"response_queue", exclusive=False)

    # Declara o exchange de resposta e faz o bind da fila de callback
    response_exchange = await channel.declare_exchange('response_exchange', aio_pika.ExchangeType.DIRECT)
    await callback_queue.bind(response_exchange, routing_key=callback_queue.name)

    # Prepara request
    correlation_id = str(uuid.uuid4())
    api_url = "/send"

    request = json.dumps({
        "correlation_id": correlation_id,
        "api_url": api_url
    }).encode()    

    # Publica request com reply_to
    
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=request,
            correlation_id=correlation_id,
            reply_to=callback_queue.name
        ),
        routing_key=REQUEST_QUEUE
    )

    print("Request enviado, aguardando resposta...")

    # consome a response queue
    await callback_queue.consume(on_response)

    return connection

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(main())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())