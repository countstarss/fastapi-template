# fastapi_template/core/cache.py
import json
from typing import Any, Optional, Union

import redis

from fastapi_template.core.config import settings

# MARK: 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# MARK: Redis缓存类
class RedisCache:
    def __init__(self):
        self.client = redis.Redis(connection_pool=redis_pool)
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None
        
    def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        data = json.dumps(value)
        if expire:
            return self.client.setex(key, expire, data)
        return self.client.set(key, data)
        
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        return self.client.delete(key) > 0
        
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.client.exists(key) > 0
        
    def flush(self) -> bool:
        """清空所有缓存"""
        return self.client.flushdb()

# MARK: 创建单例实例
cache = RedisCache()