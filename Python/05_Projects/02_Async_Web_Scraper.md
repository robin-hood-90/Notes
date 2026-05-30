---
tags: [python, project, scraper, async, aiohttp, beautifulsoup, crawling]
aliases: ["Project: Async Web Scraper", "Web Scraper", "aiohttp Scraper"]
status: draft
updated: 2026-05-29
---

# Project: Async Web Scraper

> [!summary] Goal
> Build an asynchronous web scraper using `aiohttp` and `BeautifulSoup` with rate limiting, retries, structured logging, and data persistence.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Scraper Core](#scraper-core)
3. [Rate Limiting](#rate-limiting)
4. [Data Persistence](#data-persistence)
5. [Running](#running)

---

## Project Structure

```
scraper/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── scraper.py           # Crawling logic
│   ├── parser.py            # HTML parsing
│   ├── storage.py           # Save results
│   ├── settings.py          # Config
│   └── utils.py             # Rate limiter, retry
├── data/
├── pyproject.toml
└── Dockerfile
```

---

## Scraper Core

```python
# src/scraper.py
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from asyncio import Semaphore
from src.settings import settings

class Scraper:
    def __init__(self):
        self.sem = Semaphore(settings.max_concurrent)
        self.seen_urls: set[str] = set()

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str | None:
        async with self.sem:
            try:
                async with session.get(url, timeout=30) as resp:
                    if resp.status == 429:
                        retry_after = int(resp.headers.get("Retry-After", 60))
                        await asyncio.sleep(retry_after)
                        return await self.fetch(session, url)
                    resp.raise_for_status()
                    return await resp.text()
            except Exception as e:
                logger.error("Failed %s: %s", url, e)
                return None

    async def parse(self, html: str, url: str) -> dict | None:
        soup = BeautifulSoup(html, "lxml")
        # Extract data — customise per target
        return {
            "url": url,
            "title": soup.title.text if soup.title else None,
            "text": soup.get_text(separator=" ", strip=True)[:1000],
        }

    async def crawl(self, start_url: str, max_pages: int = 100):
        async with aiohttp.ClientSession(headers=settings.headers) as session:
            queue = asyncio.Queue()
            await queue.put(start_url)

            while not queue.empty() and len(self.seen_urls) < max_pages:
                url = await queue.get()
                if url in self.seen_urls:
                    continue
                self.seen_urls.add(url)

                html = await self.fetch(session, url)
                if html:
                    data = await self.parse(html, url)
                    if data:
                        await storage.save(data)
```

---

## Rate Limiting

```python
# src/utils.py
import asyncio
import time

class RateLimiter:
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.timestamps: list[float] = []

    async def acquire(self):
        now = time.monotonic()
        self.timestamps = [t for t in self.timestamps if now - t < self.period]
        if len(self.timestamps) >= self.calls:
            sleep = self.timestamps[0] + self.period - now
            if sleep > 0:
                await asyncio.sleep(sleep)
        self.timestamps.append(time.monotonic())

# Usage
limiter = RateLimiter(calls=10, period=1.0)   # 10 requests per second

async def fetch(session, url):
    await limiter.acquire()
    return await session.get(url)
```

---

## Data Persistence

```python
# src/storage.py
import json, csv
from pathlib import Path

class JSONStorage:
    def __init__(self, path: str):
        self.path = Path(path)
        self.buffer: list[dict] = []

    async def save(self, data: dict):
        self.buffer.append(data)
        if len(self.buffer) >= 100:
            await self.flush()

    async def flush(self):
        existing = []
        if self.path.exists():
            existing = json.loads(self.path.read_text())
        existing.extend(self.buffer)
        self.path.write_text(json.dumps(existing, indent=2, default=str))
        self.buffer.clear()
```

---

## Running

```python
# src/main.py
import asyncio
import logging
from src.scraper import Scraper
from src.storage import JSONStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    storage = JSONStorage("data/results.json")
    scraper = Scraper()
    await scraper.crawl("https://example.com", max_pages=50)
    await storage.flush()
    logger.info("Scraped %d pages", len(scraper.seen_urls))

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
# Run
python -m src.main

# Output
# data/results.json — scraped data
# logs output to stdout
```

---

## Cross-Links

- [[Python/02_Core/04_Web_Scraping]] for scraping concepts
- [[Python/01_Foundations/11_Async_Python_Basics]] for async patterns
- [[Python/02_Core/03_Network_Programming_HTTP]] for HTTP clients
- [[Python/04_Playbooks/03_Production_Readiness]] for logging config
