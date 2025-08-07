import re
from google.generativeai import GenerativeModel
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
from datetime import date

# Load API key from .env
load_dotenv()
from google import generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = GenerativeModel("gemini-2.0-flash")

# Define common substrings to filter
NON_ARTICLE_SUBSTRINGS = [
    "/category/", "/tag/", "/author/", "/about/",
    "/advertise/", "/media-kit/", "/contact/",
    "/events/", "/privacy", "/terms", "/faq", "/health-club-management-features/", "/property/",
    "/health-club-management-press-releases/", "/health-club-management-company-profile/"
]

today = date.today().strftime("%B %d, %Y")

def gemini_extract_links(markdown: str) -> list:

    prompt = (
        "Below is markdown of a website listing recent articles.\n"
        "Please extract ONLY the URLs which are articles from the last 7 days, and avoid any other links, as well as promotions, or sponsored content. "
        "Return the list as plain text links (one per line, no bullets or formatting):\n\n"
        f"Today's date is {today}\n"
        f"{markdown}"
    )

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Extract URLs using regex
    urls = re.findall(r'https?://[^\s\)\]]+', text)

    # Filter out known non-article links
    filtered = [
        url for url in urls
        if not any(substr in url.lower() for substr in NON_ARTICLE_SUBSTRINGS)
    ]

    # Deduplicate
    return list(dict.fromkeys(filtered))

def gemini_summarize(article_markdowns: list) -> str:
    
    prompt = (
        f"# Weekly Fitness Industry Summary\n"
        f"**Date:** {today}\n\n"
        "You are given multiple full articles in markdown format, from three different websites:\n"
        "- FITT Insider\n"
        "- Athletech News\n"
        "- Health Club Management (HCM)\n\n"
        "Please generate a clear, well-structured weekly summary with the following rules:\n"
        "1. Group articles into 3 sections, one per source.\n"
        "2. Use each site's name as the section heading.\n"
        "3. For each article:\n"
        "   - Provide the title, and a brief, clear summary (2–4 sentences)\n"
        "   - Include the article's **publication date** (if available)\n"
        "   - Include the **URL** to the full article\n"
        "4. Separate articles cleanly with spacing or dividers.\n"
        "5. Ensure that only articles from the last seven days are included.\n"
        "6. Do **not** include any introduction like 'Here is a summary...'\n"
        "Here are the articles:\n\n"
        + "\n\n---\n\n".join(article_markdowns)
    )

    response = model.generate_content(prompt)
    return response.text.strip()

def gemini_extract_companies(summary_md: str) -> str:
    prompt = (
        "You are a research analyst reading the following weekly industry summary.\n\n"
        "Please extract a list of all companies mentioned in the summary.\n"
        "- Include company names only (no extra commentary).\n"
        "- Return a comma-separated (', ') plain text list.\n"
        "- Avoid duplicate names.\n\n"
        f"Here is the summary:\n\n{summary_md}"
    )

    response = model.generate_content(prompt)
    return response.text.strip()