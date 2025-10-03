import asyncio
import aio_pika
from protobuf import test_pb2 
from datetime import datetime, timezone


async def main():
    # Conexão assíncrona
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()

        # Garantir que a exchange existe
        exchange = await channel.declare_exchange("events", aio_pika.ExchangeType.TOPIC, durable=True)

        # Criar mensagem protobuf
        msg = test_pb2.UserCreated()
        msg.user_id = "123"
        msg.email = "teste@example.com"
        msg.created_at = str(datetime.now(timezone.utc))

        # Serializar
        payload = msg.SerializeToString()

        # Publicar
        await exchange.publish(
            aio_pika.Message(
                body=payload,
                content_type="application/protobuf",
                headers={"schema": "UserCreated:v1"}
            ),
            routing_key="user.created"
        )

        print("Mensagem Protobuf publicada")

if __name__ == "__main__":
    asyncio.run(main())
