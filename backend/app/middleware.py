"""
Anti-scraping middleware — block bots, crawlers, and suspicious User-Agents.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

BOT_KEYWORDS = [
    "bot", "crawler", "spider", "scraper", "curl", "wget",
    "python-requests", "go-http-client", "java/", "libwww",
    "scrapy", "axios/", "node-fetch", "got/",
]


class AntiBotMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ua = (request.headers.get("user-agent") or "").lower()
        for kw in BOT_KEYWORDS:
            if kw in ua:
                return Response(
                    content='{"error":"Forbidden"}',
                    status_code=403,
                    media_type="application/json",
                )

        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-RateLimit-Limit"] = "60/minute"

        return response
