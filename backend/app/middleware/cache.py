from fastapi import Request
from functools import lru_cache
import json

class CacheMiddleware:
    def __init__(self, app, redis_client=None):
        self.app = app
        self.redis = redis_client
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive)
        
        # 简单缓存：对 GET 请求缓存 5 分钟
        if request.method == "GET" and not request.url.path.startswith("/api/monitor"):
            cache_key = f"cache:{request.url.path}:{request.query_params}"
            
            if self.redis:
                cached = await self.redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    response = JSONResponse(content=data)
                    return await send(response)
        
        async def send_wrapper(response):
            if request.method == "GET" and self.redis:
                # 获取响应体
                body = []
                async for chunk in receive():
                    body.append(chunk)
                full_body = b"".join(body)
                
                # 缓存
                cache_key = f"cache:{request.url.path}:{request.query_params}"
                await self.redis.setex(cache_key, 300, full_body)
            
            await send(response)
        
        await self.app(scope, receive, send_wrapper)
