# # fastapi_template/routes/frontend.py
# from fastapi import APIRouter, Request
# from fastapi.templating import Jinja2Templates
# from pathlib import Path

# # NOTE: 如果需要使用Jinja2模板，可以继续把静态资源通过Router挂载到app.py中


# # MARK: 创建前端路由
# router = APIRouter()


# # MARK: 配置模板
# templates = Jinja2Templates(directory="fastapi_template/templates")


# # MARK: 首页
# @router.get("/", include_in_schema=False)
# async def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# # MARK: 登录
# @router.get("/login", include_in_schema=False)
# async def login(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})


# # MARK: 仪表盘
# @router.get("/dashboard", include_in_schema=False)
# async def dashboard(request: Request):
#     return templates.TemplateResponse("dashboard.html", {"request": request})