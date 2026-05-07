import asyncio
import os
from .engine import CrawlerContext
from .infrastructure import NewsRepository, MessageProducer
from .service import CrawlerService

async def main():
    # Configuration (In a real app, these would come from env vars)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    # Initialize components
    context = CrawlerContext(ai_concurrency_limit=2)
    repository = NewsRepository(MONGO_URI, "news_db")
    producer = MessageProducer(RABBITMQ_URL)
    
    # Initialize Service Layer
    service = CrawlerService(context, repository, producer)
    
    # Example URLs
    urls = [
        "https://example.com/news/article-1",
        "https://example.com/api/v1/news/data.json"
    ]
    
    tasks = [service.run_pipeline(url) for url in urls]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
