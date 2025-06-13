# newsletter/personalizer.py

from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class NewsletterPersonalizer:
    def __init__(self, config):
        self.config = config
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",
            google_api_key=config.gemini_api_key
        )
    
    def personalize(self, newsletter: Dict, tone: str = "professional",
                    length: str = "medium") -> Dict:
        personalization_prompt = PromptTemplate(
            template="Rewrite the following article summary in a {tone} tone and {length} length:\n\n{content}",
            input_variables=["tone", "length", "content"]
        )
        
        personalization_chain = LLMChain(
            llm=self.llm,
            prompt=personalization_prompt
        )
        
        personalized = {}
        for category, articles in newsletter.items():
            personalized[category] = []
            for article in articles:
                try:
                    personalized_summary = personalization_chain.run(
                        tone=tone,
                        length=length,
                        content=article["summary"]
                    )
                except Exception:
                    personalized_summary = article["summary"]  # fallback to original
                personalized[category].append({
                    "title": article["title"],
                    "summary": personalized_summary,
                    "url": article["url"]
                })
        
        return personalized
