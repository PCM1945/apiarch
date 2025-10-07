import asyncio
import aio_pika
import json
import uuid
from typing import Optional, Callable, Dict, Any
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQClient:
    """Reusable RabbitMQ client for asynchronous communication with workers."""
    
    def __init__(
        self,
        rabbit_url: str = "amqp://guest:guest@localhost/",
        request_queue: str = "task_queue",
        response_exchange: str = "response_exchange"
    ):
        self.rabbit_url = rabbit_url
        self.request_queue = request_queue
        self.response_exchange = response_exchange
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.callback_queue: Optional[aio_pika.Queue] = None
        self.response_handlers: Dict[str, Callable] = {}
        self._is_consuming = False
    
    async def connect(self):
        """Establishes connection with RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            return
            
        try:
            self.connection = await aio_pika.connect_robust(self.rabbit_url)
            self.channel = await self.connection.channel()
            
            # Create exclusive queue to receive responses
            self.callback_queue = await self.channel.declare_queue(
                name="response_queue", 
                exclusive=False
            )
            
            # Declare response exchange and bind callback queue
            response_exchange = await self.channel.declare_exchange(
                self.response_exchange, 
                aio_pika.ExchangeType.DIRECT, 
                durable=True
            )
            await self.callback_queue.bind(response_exchange, routing_key=self.callback_queue.name)
            
            logger.info("Successfully connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Closes the connection with RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    async def _on_response(self, message: aio_pika.IncomingMessage):
        """Internal handler to process responses."""
        async with message.process():
            try:
                response = json.loads(message.body)
                correlation_id = message.correlation_id
                
                if correlation_id in self.response_handlers:
                    handler = self.response_handlers.pop(correlation_id)
                    await handler(response)
                else:
                    logger.warning(f"Response received without corresponding handler: {correlation_id}")
                    
            except Exception as e:
                logger.error(f"Error processing response: {e}")
    
    async def start_consuming(self):
        """Starts consuming responses."""
        if not self._is_consuming and self.callback_queue:
            await self.callback_queue.consume(self._on_response)
            self._is_consuming = True
            logger.info("Started consuming responses")
            
    async def send_request(self, api_url: str, data: Optional[Dict[str, Any]] = None, response_handler: Optional[Callable] = None) -> str:
        """
        Sends a request to the worker.
        
        Args:
            api_url: API URL to be called
            data: Additional data for the request
            response_handler: Function to handle the response (optional)
            
        Returns:
            correlation_id: Request correlation ID
        """
        if not self.connection or self.connection.is_closed:
            await self.connect()
        
        if not self._is_consuming:
            await self.start_consuming()
        
        correlation_id = str(uuid.uuid4())
        
        # Prepare request
        request_data = {
            "correlation_id": correlation_id,
            "api_url": api_url
        }
        
        if data:
            request_data.update(data)
        
        request = json.dumps(request_data).encode()
        
        # Register response handler if provided
        if response_handler:
            self.response_handlers[correlation_id] = response_handler
        
        # Publish request
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=request,
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name
            ),
            routing_key='process.42'
        )
        
        logger.info(f"Request sent - correlation_id: {correlation_id}, api_url: {api_url}")
        return correlation_id

    async def send_request_and_wait(self, api_url: str, data: Optional[Dict[str, Any]] = None, timeout: float = 30.0) -> Dict[str, Any]:
        """
        Sends a request and waits for response synchronously.
        
        Args:
            api_url: API URL to be called
            data: Additional data for the request
            timeout: Timeout in seconds to wait for response
            
        Returns:
            Worker response
        """
        response_future = asyncio.Future()
        
        async def response_handler(response):
            if not response_future.done():
                response_future.set_result(response)
        
        correlation_id = await self.send_request(api_url, data, response_handler)
        
        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            # Remove handler on timeout
            self.response_handlers.pop(correlation_id, None)
            raise asyncio.TimeoutError(f"Timeout waiting for response for correlation_id: {correlation_id}")


# Example function for class usage
async def example_usage():
    """Example of how to use the RabbitMQClient class."""
    client = RabbitMQClient()
    
    try:
        await client.connect()
        
        # Example 1: Send request and wait for response
        response = await client.send_request_and_wait("/send", {"message": "Hello World"})
        print("Response received:", response)
        
        # Example 2: Send request with custom handler
        async def custom_handler(response):
            print("Custom handler:", response)
        
        await client.send_request("/send", {"message": "Async message"}, custom_handler)
        
        # Keep client running to receive asynchronous responses
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"Error in example: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(example_usage())