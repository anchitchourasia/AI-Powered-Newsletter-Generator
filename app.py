import streamlit as st
from newsletter.content_curator import ContentCurator
from newsletter.generator import NewsletterGenerator
from newsletter.personalizer import NewsletterPersonalizer
from newsletter.config import Config

st.set_page_config(page_title="AI Newsletter Generator", layout="wide")
st.title("📰 AI-Powered Newsletter Generator")

with st.sidebar:
    st.header("Settings")
    tone = st.selectbox("Tone", ["professional", "casual", "enthusiastic"])
    length = st.selectbox("Summary Length", ["short", "medium", "long"])
    format_option = st.multiselect("Export Format", ["html", "text"], default=["html"])

if st.button("Generate Newsletter"):
    with st.spinner("Fetching and curating articles..."):
        config = Config()
        curator = ContentCurator(config)
        generator = NewsletterGenerator(config)
        personalizer = NewsletterPersonalizer(config)

        articles = curator.fetch_articles()
        categorized = curator.categorize_articles(articles)
        scored = curator.score_articles(categorized)

        with st.spinner("Creating newsletter..."):
            newsletter = generator.create_newsletter(scored)

        with st.spinner("Personalizing content..."):
            personalized = personalizer.personalize(newsletter, tone=tone, length=length)

        with st.spinner("Generating subject lines..."):
            subject_lines = generator.generate_subject_lines(personalized)

        generator.export_newsletter(personalized, subject_lines, formats=format_option)

        st.success("✅ Newsletter Generated!")
        st.write(f"**Subject Line Option 1**: {subject_lines[0]}")
        st.write(f"**Subject Line Option 2**: {subject_lines[1]}")
        st.download_button("📩 Download HTML", open("output/newsletter.html").read(), file_name="newsletter.html")
        st.download_button("📄 Download Text", open("output/newsletter.txt").read(), file_name="newsletter.txt")
