from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import dateparser

class NewsArticle(BaseModel):
    title: str = Field(..., description="The title of the news article")
    summary: str = Field(..., description="A short summary of the content")
    date: datetime = Field(..., description="The publication date of the article")
    sentiment: str = Field(..., description="Sentiment analysis result (e.g., positive, negative, neutral)")
    url: str = Field(..., description="The source URL")

    @validator("date", pre=True)
    def parse_date(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Using dateparser to handle inconsistent AI/web date formats
            parsed_date = dateparser.parse(v)
            if parsed_date:
                return parsed_date
        raise ValueError(f"Could not parse date: {v}")
