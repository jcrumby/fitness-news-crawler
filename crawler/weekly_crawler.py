import asyncio
from crawl4ai import AsyncWebCrawler
from your_gemini_wrapper import gemini_extract_links, gemini_summarize
from email_sender import send_markdown_email

LISTING_URLS = [
    "https://insider.fitt.co/articles/",
    "https://athletechnews.com/all-news/",
    "https://www.healthclubmanagement.co.uk/health-club-management-news"
]

async def crawl_markdown(crawler, url: str) -> str:
    result = await crawler.arun(url=url)
    return result.markdown.raw_markdown if result.success else ""

async def main():
    all_article_markdowns = []

    async with AsyncWebCrawler() as crawler:
        for listing_url in LISTING_URLS:
            print(f"🔎 Crawling listing: {listing_url}")
            listing_md = await crawl_markdown(crawler, listing_url)

            print("🤖 Extracting article links with Gemini...")
            article_urls = gemini_extract_links(listing_md)
            print(f"🔗 Found {len(article_urls)} articles")

            for url in article_urls:
                print(f"📰 Crawling article: {url}")
                article_md = await crawl_markdown(crawler, url)
                if article_md:
                    all_article_markdowns.append(article_md)

    if all_article_markdowns:
        print("📦 Sending all article markdowns to Gemini for summarization...")
        summary = gemini_summarize(all_article_markdowns)

        with open("weekly_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)

        print("✅ Saved summary to weekly_summary.md")
    else:
        print("⚠️ No articles were successfully crawled.")

if __name__ == "__main__":
    asyncio.run(main())                  # Run the full async crawl/summarize
    send_markdown_email("weekly_summary.md")  # Then email the final summary

