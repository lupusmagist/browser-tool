import os
import time
import urllib.parse
from llama_cpp import Llama
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        """Search using SearXNG instance"""
        await self._setup_browser()
        
        # Use SearXNG API endpoint
        searxng_url = os.getenv("SEARXNG_URL", "http://192.168.77.8:8888")
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"{searxng_url}/search?q={encoded_query}&format=json"
        
        logger.info(f"Searching for: {query}")
        logger.info(f"SearXNG URL: {search_url}")
        
        try:
            # Navigate to the search API endpoint
            response = await self.page.goto(search_url, wait_until="networkidle")
            
            if response and response.status == 200:
                # Get the JSON response
                content = await self.page.content()
                
                # Extract JSON from the page
                soup = BeautifulSoup(content, 'html.parser')
                pre_tag = soup.find('pre')
                
                if pre_tag:
                    import json
                    json_text = pre_tag.get_text()
                    data = json.loads(json_text)
                    
                    results = []
                    search_results = data.get('results', [])
                    
                    for result in search_results[:max_results]:
                        title = result.get('title', '')
                        url = result.get('url', '')
                        content_snippet = result.get('content', '')
                        
                        if title and url:
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": content_snippet
                            })
                            logger.info(f"Found result: {title[:50]}...")
                    
                    logger.info(f"Total results found: {len(results)}")
                    return results
            
            logger.warning(f"Failed to get results from SearXNG, status: {response.status if response else 'None'}")
            return []
            
        except Exception as e:
            logger.error(f"SearXNG search error: {str(e)}")
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
