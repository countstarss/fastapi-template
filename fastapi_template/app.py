import io
import os

from fastapi import FastAPI

from .db import create_db_and_tables, engine
from .routes import main_router
from fastapi_template.api.v1.api import api_router
from fastapi_template.core.config import settings
from fastapi_template.core.middleware import setup_middlewares
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# MARK: 读取文件内容
def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("VERSION")
    """
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


# MARK: 项目描述
description = """
FastAPI helps you do awesome stuff. 🚀
"""

# MARK: 创建应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# NOTE: 如果需要使用Jinja2模板，请取消注释以下代码
# NOTE: 挂载静态文件
# app.mount("/static", StaticFiles(directory="fastapi_template/static"), name="static")
# NOTE: 配置模板
# templates = Jinja2Templates(directory="fastapi_template/templates")


# MARK: 设置中间件
setup_middlewares(app)



# MARK: 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    create_db_and_tables(engine)
