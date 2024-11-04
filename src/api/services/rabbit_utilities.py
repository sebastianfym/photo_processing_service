import asyncio
from dotenv import load_dotenv
load_dotenv()
import aio_pika
from uuid import UUID
from tenacity import retry, wait_fixed, stop_after_attempt
from config import settings


class RabbitMQPublisher:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection = None
        self.channel = None


    @retry(wait=wait_fixed(2), stop=stop_after_attempt(50))
    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(self.connection_url)
            self.channel = await self.connection.channel()
            settings.logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            settings.logger.warning(f"Failed to connect to RabbitMQ: {e}")


    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    async def send_image_event(self, event_type: str, image_id: UUID, details: dict):
        try:
            await self.connect()
            message_body = {
                "event_type": event_type,
                "image_id": str(image_id),
                "details": details,
            }
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=str(message_body).encode()),
                routing_key="image_events",
            )
        except Exception as e:
            settings.logger.warning(f"Failed to send image event: {e}")
            await asyncio.sleep(5)


    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    async def close(self):
        try:
            if self.connection:
                await self.connection.close()
        except Exception as e:
            settings.logger.warning(f"Failed close connection: {e}")
            await asyncio.sleep(5)


    async def notify_image_event(self, event_type, image_model):
        await self.send_image_event(
            event_type=event_type,
            image_id=image_model.id,
            details={
                "title": image_model.title,
                "filepath": image_model.filepath,
                "quality": image_model.quality,
                "size": str(image_model.size),
            }
        )
        await self.close()


    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            settings.logger.info(f"Message has been received: \n{message.body.decode()}")

    async def consume_image_events(self):
        if not self.channel:
            await self.connect()

        queue = await self.channel.declare_queue("image_events", durable=True)
        await queue.consume(self.process_message)

        settings.logger.info("Waiting for messages.")
        await asyncio.Future()


RABBITMQ_PUBLISHER = RabbitMQPublisher(settings.RABBITMQ_URL)
