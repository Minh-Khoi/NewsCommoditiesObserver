import motor.motor_asyncio
import aio_pika
import json
from .models import NewsArticle

class NewsRepository:
    def __init__(self, mongo_uri: str, db_name: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            mongo_uri,
            maxPoolSize=10,
            # WiredTiger cache limit is usually set in docker-compose, 
            # but we can ensure the connection is efficient.
        )
        self.db = self.client[db_name]
        self.collection = self.db["news_articles"]

    async def save(self, article: NewsArticle) -> bool:
        try:
            await self.collection.update_one(
                {"url": article.url},
                {"$set": article.dict()},
                upsert=True
            )
            return True
        except Exception:
            return False

class MessageProducer:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url

    async def publish(self, article: NewsArticle):
        connection = await aio_pika.connect_robust(self.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({"url": article.url, "event": "news_crawled"}).encode()
                ),
                routing_key="news_crawled"
            )
