from fastapi import FastAPI, Depends, HTTPException
from .browser_tool import BrowserTool
import uvicorn
from typing import Optional
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize global configurations if needed
    yield

app = FastAPI(title="Browser Tool API", version="1.0.0", lifespan=lifespan)

# Dependency to manage browser instances
async def get_browser_tool():
    browser = BrowserTool()
    try:
        yield browser
    finally:
        await browser.close()

@app.post("/web_search")
async def web_search(
    query: str,
    max_results: int = 10,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Perform web search"""
    try:
        results = await browser.web_search(query, max_results)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/navigate")
async def navigate(
    url: str,
    wait_for_element: Optional[str] = None,
    wait_time: int = 10,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Navigate to URL"""
    try:
        await browser.navigate(url, wait_for_element, wait_time)
        return {"status": "success", "message": "Navigation completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract_content")
async def extract_content(
    url: Optional[str] = None,
    wait_for_element: Optional[str] = None,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Extract page content"""
    try:
        content = await browser.extract_content(url, wait_for_element)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize(
    text: str,
    max_tokens: int = 200,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Summarize text using LLM"""
    try:
        summary = await browser.summarize(text, max_tokens)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl")
async def crawl(
    url: str,
    max_depth: int = 2,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Crawl website with depth control"""
    # Implement your crawling logic here
    return {"status": "crawling started"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
