import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")

        self.rss_feeds = {
            "tech": ["https://techcrunch.com/feed/"],
            "health": ["https://www.healthline.com/rss/news"],
            "finance": ["https://www.forbes.com/money/feed/"]
        }

        self.templates_dir = "templates"
        self.output_dir = "output"

        # ✅ Create output directory if not exists
        os.makedirs(self.output_dir, exist_ok=True)

        self.languages = ["en", "hi", "fr"]
