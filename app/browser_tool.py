import os
import time
from llama_cpp import Llama
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Optional

class BrowserTool:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        # Initialize Llama model from .env
        model_path = os.getenv("LLM")
        if model_path and os.path.exists(model_path):
            self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4)
        else:
            self.llm = None

    async def _setup_browser(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        if self.browser is None:
            self.browser = await self.playwright.chromium.launch(headless=True)
        if self.page is None:
            self.page = await self.browser.new_page()

    async def web_search(self, query: str, max_results: int = 10):
        await self._setup_browser()
        search_url = f"https://duckduckgo.com/html?q={query.replace(' ', '+')}"
        await self.page.goto(search_url)

        try:
            await self.page.wait_for_selector(".result", timeout=10000)

            results = []
            search_results = await self.page.query_selector_all(".result")

            for result in search_results[:max_results]:
                try:
                    title_element = await result.query_selector("h2 a")
                    url_element = await result.query_selector("h2 a")
                    snippet_element = await result.query_selector(".result__snippet")

                    title = await title_element.inner_text() if title_element else ""
                    url = await url_element.get_attribute("href") if url_element else ""
                    snippet = await snippet_element.inner_text() if snippet_element else ""
                    results.append({"title": title, "url": url, "snippet": snippet})
                except Exception:
                    continue

            return results

        except Exception:
            return []

    async def navigate(self, url: str, wait_for_element: Optional[str] = None, wait_time: int = 10):
        await self._setup_browser()
        await self.page.goto(url)

        if wait_for_element:
            try:
                await self.page.wait_for_selector(wait_for_element, timeout=wait_time * 1000)
            except Exception:
                raise Exception(f"Element '{wait_for_element}' not found on page")

    async def extract_content(self, url: Optional[str] = None, wait_for_element: Optional[str] = None):
        if url:
            await self.navigate(url, wait_for_element)

        await self._setup_browser()
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        return ' '.join(text.split())

    async def summarize(self, text: str, max_tokens: int = 200):
        if not self.llm:
            raise Exception("LLM not configured. Set LLM environment variable.")

        prompt = f"Summarize the following text concisely:\n\n{text}\n\nSummary:"
        output = self.llm(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            stop=["\n\n"],
            echo=False
        )
        return output["choices"][0]["text"].strip()

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
