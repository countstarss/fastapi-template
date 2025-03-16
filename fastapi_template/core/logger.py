import logging
import sys
from typing import List, Optional

from fastapi_template.core.config import settings

# MARK: 配置日志记录器
"""
日志记录器配置
- 设置日志格式
- 配置控制台和文件处理器
- 支持不同日志级别
"""

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 创建日志记录器
logger = logging.getLogger("fastapi_template")

# 设置日志级别
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(log_level)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(console_handler)

# 如果配置了日志文件，添加文件处理器
if hasattr(settings, "LOG_FILE") and settings.LOG_FILE:
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logger.addHandler(file_handler)

# 防止日志重复
logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """
    获取命名的日志记录器
    
    参数:
        name: 日志记录器名称
        
    返回:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(f"fastapi_template.{name}")
