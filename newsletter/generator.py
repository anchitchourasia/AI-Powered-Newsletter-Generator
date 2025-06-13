# newsletter/generator.py

from typing import Dict, List, Tuple
from jinja2 import Environment, FileSystemLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class NewsletterGenerator:
    def __init__(self, config):
        self.config = config
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",
            google_api_key=config.gemini_api_key
        )
        self.jinja_env = Environment(
            loader=FileSystemLoader(config.templates_dir)
        )
    
    def create_newsletter(self, scored_articles: Dict[str, List[Dict]]) -> Dict:
        summary_prompt = PromptTemplate(
            template="Summarize this article in a professional tone:\n{content}",
            input_variables=["content"]
        )
        
        summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        
        newsletter_content = {}
        for category, articles in scored_articles.items():
            newsletter_content[category] = []
            for article in articles[:5]:  # Top 5 articles per category
                try:
                    summary = summary_chain.run(content=article["content"])
                except Exception:
                    summary = "Summary unavailable due to an error."
                newsletter_content[category].append({
                    "title": article["title"],
                    "summary": summary,
                    "url": article["url"]
                })
        
        return newsletter_content
    
    def generate_subject_lines(self, newsletter: Dict) -> Tuple[str, str]:
        subject_prompt = PromptTemplate(
            template="Generate two catchy and engaging email subject lines for a newsletter based on the following content headlines:\n\n{content}\n\nRespond with two subject lines only.",
            input_variables=["content"]
        )
        
        subject_chain = LLMChain(llm=self.llm, prompt=subject_prompt)
        
        # Build sample input from top headlines
        sample_content = ""
        for category, articles in newsletter.items():
            if articles:
                sample_content += f"{category.title()}: {articles[0]['title']}\n"
        
        try:
            response = subject_chain.run(content=sample_content)
            lines = response.strip().split("\n")
            return tuple(lines[:2]) if len(lines) >= 2 else (lines[0], "Stay Informed with Our Latest News")
        except Exception:
            return ("Your Weekly Newsletter is Here!", "Check Out This Week's Highlights")
    
    def export_newsletter(self, newsletter: Dict, subject_lines: Tuple[str, str],
                         formats: List[str] = ["html"]):
        if "html" in formats:
            template = self.jinja_env.get_template("newsletter.html")
            html_content = template.render(
                newsletter=newsletter,
                subject=subject_lines[0]
            )
            with open(f"{self.config.output_dir}/newsletter.html", "w", encoding="utf-8") as f:
                f.write(html_content)
        
        if "text" in formats:
            template = self.jinja_env.get_template("newsletter.txt")
            text_content = template.render(
                newsletter=newsletter,
                subject=subject_lines[0]
            )
            with open(f"{self.config.output_dir}/newsletter.txt", "w", encoding="utf-8") as f:
                f.write(text_content)
