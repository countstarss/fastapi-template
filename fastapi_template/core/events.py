# fastapi_template/core/events.py
from typing import Any, Callable, Dict, List, Optional

# MARK: 事件总线类
class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """取消订阅事件"""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            
    def publish(self, event_type: str, data: Optional[Any] = None) -> None:
        """发布事件"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)

# MARK: 创建单例实例
event_bus = EventBus()



# MARK: 事件类型常量
class EventTypes:
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    CONTENT_CREATED = "content_created"
    CONTENT_UPDATED = "content_updated"
    CONTENT_DELETED = "content_deleted"