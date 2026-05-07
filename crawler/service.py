from .engine import CrawlerContext
from .infrastructure import NewsRepository, MessageProducer
from .models import NewsArticle

class CrawlerService:
    """The Service Layer that orchestrates the full lifecycle."""
    def __init__(self, context: CrawlerContext, repository: NewsRepository, producer: MessageProducer):
        self.context = context
        self.repository = repository
        self.producer = producer

    async def run_pipeline(self, url: str):
        # 1. Scrape and Process (via Context/Engine)
        article: NewsArticle = await self.context.crawl_and_process(url)
        
        # 2. Persist
        success = await self.repository.save(article)
        
        # 3. Notify (only if persist was successful)
        if success:
            await self.producer.publish(article)
            print(f"Successfully processed and notified: {url}")
        else:
            print(f"Failed to persist article: {url}")
        
        return article
