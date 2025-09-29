import asyncio
import json
import aio_pika
import aiohttp

RABBIT_URL = "amqp://guest:guest@localhost/"
REQUEST_QUEUE = "task_queue"
BASE_API_URL = "http://localhost:8009"
fg
async def process_message(message: aio_pika.IncomingMessage, exchange: aio_pika.Exchange):
    async with message.process():
        payload = json.loads(message.body)
        correlation_id = payload.get("correlation_id")
        api_url = payload.get("api_url")
        reply_to = message.reply_to

        api_payload = {
            "message": f"correlation_id: {correlation_id}",
            "sender": correlation_id
        }
    
        print(f"[Worker] Received request with correlation ID: {correlation_id}, calling api {api_url}")

        try:
            print(f"[Worker] Making request to {BASE_API_URL + api_url}")
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                async with session.post(
                    BASE_API_URL + api_url,
                    data=json.dumps(api_payload),
                    headers=headers
                ) as resp:
                    data = await resp.json()
                    print(f"[Worker] Received data from API: {data}")
        except Exception as e:
            data = {"error": str(e)}

        response = json.dumps({
            "correlation_id": correlation_id,
            "result": data
        }).encode()

        # Publica usando a default_exchange persistence
        await exchange.publish(
            aio_pika.Message(
                body=response,
                correlation_id=correlation_id
            ),
            routing_key=reply_to
        )
        print(f"[Worker] Resposta enviada para chave {reply_to}")

async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()   
    queue = await channel.declare_queue(REQUEST_QUEUE, durable=True)

    exchange = await channel.declare_exchange('response_exchange', aio_pika.ExchangeType.DIRECT, durable=True)

    print("[Worker] Aguardando requests...")

    await queue.consume(lambda msg: process_message(msg, exchange))
    return connection


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(main())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())