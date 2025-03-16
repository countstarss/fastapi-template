# fastapi_template/core/middleware.py
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_template.core.config import settings
from fastapi_template.core.logger import logger

# MARK: 日志中间件
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 处理请求
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 记录请求信息
            logger.info(
                f"{request.method} {request.url.path} {response.status_code} {process_time:.4f}s"
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"{request.method} {request.url.path} 500 {process_time:.4f}s - {str(e)}"
            )
            raise

# MARK: 设置中间件
def setup_middlewares(app: FastAPI) -> None:
    # NOTE: 设置CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # NOTE: 添加日志中间件
    app.add_middleware(LoggingMiddleware)