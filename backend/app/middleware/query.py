from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.monitoring_service import MonitoringService
import time

class QueryMonitorMiddleware:
    def __init__(self, app):
        self.app = app
        self.monitor = MonitoringService()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive)
        start_time = time.time()
        
        async def send_wrapper(response):
            query_time = (time.time() - start_time) * 1000
            
            # 记录性能日志
            if query_time > 100:  # 超过 100ms 记录
                self.monitor.record_performance(request.url.path, query_time)
            
            await send(response)
        
        await self.app(scope, receive, send_wrapper)

# 在 main.py 中注册
# app.add_middleware(QueryMonitorMiddleware)
