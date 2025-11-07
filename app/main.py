from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from .browser_tool import BrowserTool
import uvicorn
from typing import Optional
from contextlib import asynccontextmanager

# Request models
class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 10

class NavigateRequest(BaseModel):
    url: str
    wait_for_element: Optional[str] = None
    wait_time: int = 10

class ExtractContentRequest(BaseModel):
    url: Optional[str] = None
    wait_for_element: Optional[str] = None

class SummarizeRequest(BaseModel):
    text: str
    max_tokens: int = 200

class CrawlRequest(BaseModel):
    url: str
    max_depth: int = 2

class BrowserToolRequest(BaseModel):
    action: str  # 'search', 'get_page', 'summarize'
    query: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    max_results: Optional[int] = 10
    max_tokens: Optional[int] = 200

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
    request: WebSearchRequest,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Perform web search"""
    try:
        results = await browser.web_search(request.query, request.max_results)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/navigate")
async def navigate(
    request: NavigateRequest,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Navigate to URL"""
    try:
        await browser.navigate(request.url, request.wait_for_element, request.wait_time)
        return {"status": "success", "message": "Navigation completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract_content")
async def extract_content(
    request: ExtractContentRequest,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Extract page content"""
    try:
        content = await browser.extract_content(request.url, request.wait_for_element)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize(
    request: SummarizeRequest,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Summarize text using LLM"""
    try:
        summary = await browser.summarize(request.text, request.max_tokens)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl")
async def crawl(
    request: CrawlRequest,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """Crawl website with depth control"""
    # Implement your crawling logic here
    return {"status": "crawling started", "url": request.url, "max_depth": request.max_depth}

@app.post("/browser_tool")
async def browser_tool(
    request: BrowserToolRequest,
    browser: BrowserTool = Depends(get_browser_tool)
):
    """
    Unified browser tool endpoint that handles multiple actions:
    - search: Search the web using SearXNG
    - get_page: Fetch and extract content from a web page
    - summarize: Summarize text using local LLM
    """
    try:
        if request.action == "search":
            if not request.query:
                raise HTTPException(status_code=400, detail="'query' is required for 'search' action")
            results = await browser.web_search(request.query, request.max_results or 10)
            return {"action": "search", "results": results}
        
        elif request.action == "get_page":
            if not request.url:
                raise HTTPException(status_code=400, detail="'url' is required for 'get_page' action")
            content = await browser.extract_content(request.url)
            return {"action": "get_page", "url": request.url, "content": content}
        
        elif request.action == "summarize":
            if not request.text:
                raise HTTPException(status_code=400, detail="'text' is required for 'summarize' action")
            summary = await browser.summarize(request.text, request.max_tokens or 200)
            return {"action": "summarize", "summary": summary}
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action '{request.action}'. Must be one of: search, get_page, summarize"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
