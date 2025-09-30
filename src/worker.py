import asyncio
import json
import aio_pika
import aiohttp
from typing import Optional, Dict, Any, Callable
import logging
import abc

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestProcessor(abc.ABC):
    """Abstract base class for processing requests."""
    
    @abc.abstractmethod
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process the incoming request and return a response."""
        pass


class DefaultRequestProcessor(RequestProcessor):
    """Default implementation of RequestProcessor that makes HTTP API calls."""
    
    def __init__(self, base_api_url: str = "http://localhost:8009"):
        self.base_api_url = base_api_url
    
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request by making HTTP call to API.
        
        Args:
            payload: Request payload containing correlation_id and api_url
            
        Returns:
            Response data from API or error information
        """
        correlation_id = payload.get("correlation_id")
        api_url = payload.get("api_url")
        
        api_payload = {
            "message": f"correlation_id: {correlation_id}",
            "sender": correlation_id
        }
        
        logger.info(f"Processing request with correlation ID: {correlation_id}, calling API {api_url}")
        
        try:
            logger.info(f"Making request to {self.base_api_url + api_url}")
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                async with session.post(
                    self.base_api_url + api_url,
                    data=json.dumps(api_payload),
                    headers=headers
                ) as resp:
                    data = await resp.json()
                    logger.info(f"Received data from API: {data}")
                    return data
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return {"error": str(e)}


class RabbitMQWorker:
    """Reusable RabbitMQ worker for processing messages and sending responses."""
    
    def __init__(
        self,
        rabbit_url: str = "amqp://guest:guest@localhost/",
        request_queue: str = "task_queue",
        response_exchange: str = "response_exchange",
        processor: Optional[RequestProcessor] = None
    ):
        self.rabbit_url = rabbit_url
        self.request_queue = request_queue
        self.response_exchange = response_exchange
        self.processor = processor or DefaultRequestProcessor()
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self._is_consuming = False
    
    async def connect(self):
        """Establish connection with RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            return
        
        try:
            self.connection = await aio_pika.connect_robust(self.rabbit_url)
            self.channel = await self.connection.channel()
            
            # Declare request queue
            self.queue = await self.channel.declare_queue(
                self.request_queue, 
                durable=True
            )
            
            # Declare response exchange
            self.exchange = await self.channel.declare_exchange(
                self.response_exchange, 
                aio_pika.ExchangeType.DIRECT, 
                durable=True
            )
            
            logger.info("Successfully connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Close connection with RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    async def _process_message(self, message: aio_pika.IncomingMessage):
        """Internal method to process incoming messages."""
        async with message.process():
            try:
                # Parse message payload
                payload = json.loads(message.body)
                correlation_id = payload.get("correlation_id")
                reply_to = message.reply_to
                
                if not correlation_id:
                    logger.warning("Received message without correlation_id")
                    return
                
                if not reply_to:
                    logger.warning(f"Received message without reply_to: {correlation_id}")
                    return
                
                # Process the request using the configured processor
                result = await self.processor.process_request(payload)
                
                # Prepare response
                response = json.dumps({
                    "correlation_id": correlation_id,
                    "result": result
                }).encode()
                
                # Send response back to client
                await self.exchange.publish(
                    aio_pika.Message(
                        body=response,
                        correlation_id=correlation_id
                    ),
                    routing_key=reply_to
                )
                
                logger.info(f"Response sent to queue {reply_to}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def start_consuming(self):
        """Start consuming messages from the request queue."""
        if not self.connection or self.connection.is_closed:
            await self.connect()
        
        if not self._is_consuming and self.queue:
            await self.queue.consume(self._process_message)
            self._is_consuming = True
            logger.info("Started consuming messages")
    
    async def stop_consuming(self):
        """Stop consuming messages."""
        if self._is_consuming and self.queue:
            await self.queue.cancel()
            self._is_consuming = False
            logger.info("Stopped consuming messages")
    
    async def run(self):
        """Run the worker (connect and start consuming)."""
        await self.connect()
        await self.start_consuming()
        logger.info("Worker is running and waiting for requests...")
        return self.connection


# Custom processor example
class CustomRequestProcessor(RequestProcessor):
    """Example of a custom request processor."""
    
    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Custom processing logic."""
        correlation_id = payload.get("correlation_id")
        
        # Custom processing logic here
        result = {
            "message": f"Custom processing for {correlation_id}",
            "processed_at": asyncio.get_event_loop().time(),
            "payload": payload
        }
        
        logger.info(f"Custom processing completed for {correlation_id}")
        return result


# Example usage function
async def example_usage():
    """Example of how to use the RabbitMQWorker class."""
    
    # Example 1: Using default processor
    worker1 = RabbitMQWorker()
    
    # Example 2: Using custom processor
    custom_processor = CustomRequestProcessor()
    worker2 = RabbitMQWorker(
        request_queue="custom_queue",
        processor=custom_processor
    )
    
    # Example 3: Using custom API URL
    api_processor = DefaultRequestProcessor(base_api_url="http://localhost:9000")
    worker3 = RabbitMQWorker(processor=api_processor)
    
    # Run a worker
    try:
        connection = await worker1.run()
        # Keep running
        return connection
    except Exception as e:
        logger.error(f"Error in worker: {e}")
        await worker1.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(example_usage())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())