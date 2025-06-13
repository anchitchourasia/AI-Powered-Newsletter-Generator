# newsletter/content_curator.py

from typing import List, Dict
import feedparser
from bs4 import BeautifulSoup
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class ContentCurator:
    def __init__(self, config):
        self.config = config
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",
            google_api_key=config.gemini_api_key
        )
    
    def fetch_articles(self) -> List[Dict]:
        articles = []
        for category, feeds in self.config.rss_feeds.items():
            for feed_url in feeds:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    articles.append({
                        "title": entry.title,
                        "content": entry.summary,
                        "url": entry.link,
                        "category": category
                    })
        return articles
    
    def categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        categorized = {}
        for article in articles:
            if article["category"] not in categorized:
                categorized[article["category"]] = []
            categorized[article["category"]].append(article)
        return categorized
    
    def score_articles(self, categorized_articles: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        scoring_prompt = PromptTemplate(
            template="Rate the relevance of this article from 1 to 10 for a newsletter:\n\n{content}\n\nRespond only with a number.",
            input_variables=["content"]
        )
        
        scoring_chain = LLMChain(llm=self.llm, prompt=scoring_prompt)
        
        scored_articles = {}
        for category, articles in categorized_articles.items():
            scored_articles[category] = []
            for article in articles:
                try:
                    score_str = scoring_chain.run(content=article["content"])
                    score = int(''.join(filter(str.isdigit, score_str)))
                    article["relevance_score"] = min(max(score, 1), 10)
                except Exception:
                    article["relevance_score"] = 5  # fallback default score
                scored_articles[category].append(article)
            
            # Sort by relevance score descending
            scored_articles[category].sort(
                key=lambda x: x["relevance_score"],
                reverse=True
            )
        
        return scored_articles
