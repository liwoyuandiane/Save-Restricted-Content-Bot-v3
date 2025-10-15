# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import asyncio
import logging
import time
import psutil
import gc
import os
from typing import Dict, Any, Optional, Callable
from functools import wraps
from config import ENABLE_CACHING, MAX_CONCURRENT_DOWNLOADS

# 配置日志
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            "function_calls": {},
            "execution_times": {},
            "memory_usage": [],
            "cpu_usage": [],
            "start_time": time.time()
        }
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存过期时间
        
    def track_function(self, func_name: str = None):
        """装饰器：跟踪函数执行时间和调用次数"""
        def decorator(func: Callable):
            name = func_name or func.__name__
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self._record_metric(name, execution_time)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self._record_metric(name, execution_time)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def _record_metric(self, func_name: str, execution_time: float):
        """记录性能指标"""
        if func_name not in self.metrics["function_calls"]:
            self.metrics["function_calls"][func_name] = 0
            self.metrics["execution_times"][func_name] = []
        
        self.metrics["function_calls"][func_name] += 1
        self.metrics["execution_times"][func_name].append(execution_time)
        
        # 只保留最近100次执行时间
        if len(self.metrics["execution_times"][func_name]) > 100:
            self.metrics["execution_times"][func_name] = self.metrics["execution_times"][func_name][-100:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        stats = {
            "uptime": time.time() - self.metrics["start_time"],
            "function_stats": {},
            "system_stats": self._get_system_stats()
        }
        
        for func_name, times in self.metrics["execution_times"].items():
            if times:
                stats["function_stats"][func_name] = {
                    "calls": self.metrics["function_calls"][func_name],
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "total_time": sum(times)
                }
        
        return stats
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "cpu_percent": cpu_percent,
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"获取系统统计失败: {e}")
            return {}
    
    def clear_metrics(self):
        """清除性能指标"""
        self.metrics["function_calls"].clear()
        self.metrics["execution_times"].clear()
        self.metrics["memory_usage"].clear()
        self.metrics["cpu_usage"].clear()

class MemoryManager:
    """内存管理器"""
    
    def __init__(self):
        self.memory_threshold = 80  # 内存使用率阈值
        self.cleanup_interval = 300  # 5分钟清理一次
        self.last_cleanup = time.time()
    
    async def check_memory_usage(self):
        """检查内存使用情况"""
        try:
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                logger.warning(f"内存使用率过高: {memory.percent:.1f}%")
                await self.cleanup_memory()
        except Exception as e:
            logger.error(f"检查内存使用失败: {e}")
    
    async def cleanup_memory(self):
        """清理内存"""
        try:
            logger.info("开始内存清理...")
            
            # 强制垃圾回收
            collected = gc.collect()
            logger.info(f"垃圾回收清理了 {collected} 个对象")
            
            # 清理缓存
            if ENABLE_CACHING:
                self._clear_expired_cache()
            
            # 清理下载队列中的超时任务
            from plugins.ytdl import ongoing_downloads
            current_time = time.time()
            timeout_threshold = 1800  # 30分钟
            
            expired_downloads = []
            for user_id, download_info in ongoing_downloads.items():
                if current_time - download_info.get("start_time", 0) > timeout_threshold:
                    expired_downloads.append(user_id)
            
            for user_id in expired_downloads:
                ongoing_downloads.pop(user_id, None)
                logger.info(f"清理超时下载任务: 用户 {user_id}")
            
            logger.info("内存清理完成")
            
        except Exception as e:
            logger.error(f"内存清理失败: {e}")
    
    def _clear_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, (value, timestamp) in self.cache.items():
            if current_time - timestamp > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not ENABLE_CACHING:
            return None
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        if ENABLE_CACHING:
            self.cache[key] = (value, time.time())
    
    def clear(self):
        """清除所有缓存"""
        self.cache.clear()
    
    def clear_expired(self):
        """清除过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, (value, timestamp) in self.cache.items():
            if current_time - timestamp >= self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]

class ConnectionPool:
    """连接池管理器"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.active_connections = 0
        self.connection_queue = asyncio.Queue()
    
    async def acquire_connection(self):
        """获取连接"""
        if self.active_connections < self.max_connections:
            self.active_connections += 1
            return True
        else:
            # 等待可用连接
            await self.connection_queue.get()
            return True
    
    def release_connection(self):
        """释放连接"""
        if self.active_connections > 0:
            self.active_connections -= 1
            if not self.connection_queue.empty():
                self.connection_queue.put_nowait(None)

# 全局实例
performance_monitor = PerformanceMonitor()
memory_manager = MemoryManager()
cache_manager = CacheManager()
connection_pool = ConnectionPool(max_connections=MAX_CONCURRENT_DOWNLOADS)

# 便捷函数
def track_performance(func_name: str = None):
    """性能跟踪装饰器"""
    return performance_monitor.track_function(func_name)

def get_performance_stats() -> Dict[str, Any]:
    """获取性能统计"""
    return performance_monitor.get_performance_stats()

async def cleanup_memory():
    """清理内存"""
    await memory_manager.cleanup_memory()

def get_cache(key: str) -> Optional[Any]:
    """获取缓存"""
    return cache_manager.get(key)

def set_cache(key: str, value: Any):
    """设置缓存"""
    cache_manager.set(key, value)

def clear_cache():
    """清除缓存"""
    cache_manager.clear()

async def acquire_connection():
    """获取连接"""
    return await connection_pool.acquire_connection()

def release_connection():
    """释放连接"""
    connection_pool.release_connection()

# 定期清理任务
async def periodic_cleanup():
    """定期清理任务"""
    while True:
        try:
            await asyncio.sleep(300)  # 5分钟
            await memory_manager.check_memory_usage()
            cache_manager.clear_expired()
        except Exception as e:
            logger.error(f"定期清理任务失败: {e}")

# 启动定期清理任务
asyncio.create_task(periodic_cleanup())
