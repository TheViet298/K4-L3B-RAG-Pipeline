"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"
URLS_FILE = Path(__file__).parent.parent / "data" / "urls.csv"

ARTICLE_URLS = [
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/cau-hoi-thuong-gap/tuyen-sinh/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/cau-hoi-thuong-gap/chuong-trinh-dao-tao/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/cau-hoi-thuong-gap/hoc-phi-hoc-bong-va-ho-tro-tai-chinh/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/cau-hoi-thuong-gap/yeu-cau-trinh-do-tieng-anh/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/cau-hoi-thuong-gap/cuoc-song-tai-ky-tuc-xa/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/cau-hoi-thuong-gap/viec-lam-thuc-tap/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/ung-tuyen-vao-vinuni/ung-vien-nam-nhat/quy-trinh-ung-tuyen/",
]

if URLS_FILE.exists():
    loaded_urls = [
        line.strip()
        for line in URLS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and line.strip().startswith("http")
    ]
    if loaded_urls:
        ARTICLE_URLS = loaded_urls


def _crawl_with_soup(url: str) -> dict:
    from datetime import datetime
    import re
    import requests
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()
    else:
        title = "Thong tin tuyen sinh VinUni"

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "button"]):
        tag.decompose()

    main_container = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_=re.compile(r"content|entry|post|faq", re.I))
        or soup.body
    )

    lines = []
    if main_container:
        for element in main_container.descendants:
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = element.name[1]
                header_text = element.get_text(strip=True)
                if header_text:
                    lines.append(f"\n{'#' * int(level)} {header_text}\n")
            elif element.name == "p":
                p_text = element.get_text(strip=True)
                if p_text:
                    lines.append(f"{p_text}\n")
            elif element.name == "li":
                li_text = element.get_text(strip=True)
                if li_text:
                    lines.append(f"- {li_text}")

    content_markdown = "\n".join(lines).strip()
    if not content_markdown and main_container:
        content_markdown = main_container.get_text("\n", strip=True)

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content_markdown,
    }


async def crawl_article(url: str) -> dict:
    from datetime import datetime

    try:
        from crawl4ai import AsyncWebCrawler

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return {
                "url": url,
                "title": result.metadata.get("title", "Unknown"),
                "date_crawled": datetime.now().isoformat(),
                "content_markdown": result.markdown,
            }
    except Exception:
        # Fallback to requests + BeautifulSoup
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _crawl_with_soup, url)


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
