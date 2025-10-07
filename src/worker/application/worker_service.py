import logging
from domain.interfaces import Message, MessageBroker
from application.registry import UseCaseRegistry
from utils.logger import AppLogger

logger = AppLogger(__name__)

class WorkerService:
    """Processa mensagens dinamicamente conforme o routing_key."""

    def __init__(self, broker: MessageBroker):
        self.broker = broker

    async def start(self):
        logger.info("Worker dinâmico iniciado. Aguardando mensagens...")
        await self.broker.consume(self._handle_message)

    async def _handle_message(self, message: Message):
        logger.info(f"[Worker] Mensagem recebida: {message.body}")

        try:
            use_case = UseCaseRegistry.get_use_case(message.reply_to)
            result = await use_case.execute(message.body)

            response = Message(result, message.correlation_id, message.reply_to)
            await self.broker.publish(response, routing_key=message.reply_to)

            logger.info(f"[Worker] Resposta enviada para {message.reply_to}")

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)