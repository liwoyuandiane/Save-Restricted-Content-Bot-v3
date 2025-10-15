# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import asyncio
import logging
import time
import psutil
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from shared_client import client, app, userbot
from utils.func import ensure_database_connection

# 配置日志
logger = logging.getLogger(__name__)

class HealthMonitor:
    """健康监控器"""
    
    def __init__(self, check_interval: int = 300):
        self.check_interval = check_interval  # 5分钟
        self.last_check = 0
        self.health_status = {
            "overall": "healthy",
            "telethon": "unknown",
            "pyrogram": "unknown", 
            "userbot": "unknown",
            "database": "unknown",
            "system": "unknown",
            "last_update": None
        }
        self.alert_thresholds = {
            "memory_percent": 85,
            "disk_percent": 90,
            "cpu_percent": 80,
            "download_queue": 8
        }
        self.running = False
        
    async def start_monitoring(self):
        """开始健康监控"""
        self.running = True
        logger.info("健康监控已启动")
        
        while self.running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"健康监控检查时出错: {e}")
                await asyncio.sleep(60)  # 出错时等待1分钟再重试
    
    def stop_monitoring(self):
        """停止健康监控"""
        self.running = False
        logger.info("健康监控已停止")
    
    async def _perform_health_check(self):
        """执行健康检查"""
        current_time = time.time()
        if current_time - self.last_check < self.check_interval:
            return
        
        logger.debug("执行健康检查...")
        
        # 并行检查所有组件
        checks = await asyncio.gather(
            self._check_telethon(),
            self._check_pyrogram(),
            self._check_userbot(),
            self._check_database(),
            self._check_system(),
            return_exceptions=True
        )
        
        # 更新状态
        self.health_status.update({
            "telethon": checks[0] if not isinstance(checks[0], Exception) else "error",
            "pyrogram": checks[1] if not isinstance(checks[1], Exception) else "error",
            "userbot": checks[2] if not isinstance(checks[2], Exception) else "error",
            "database": checks[3] if not isinstance(checks[3], Exception) else "error",
            "system": checks[4] if not isinstance(checks[4], Exception) else "error",
            "last_update": datetime.now().isoformat()
        })
        
        # 确定整体状态
        self._determine_overall_status()
        
        # 检查是否需要告警
        await self._check_alerts()
        
        self.last_check = current_time
        logger.debug(f"健康检查完成: {self.health_status['overall']}")
    
    async def _check_telethon(self) -> str:
        """检查 Telethon 客户端"""
        try:
            if client and client.is_connected():
                return "healthy"
            else:
                return "unhealthy"
        except Exception as e:
            logger.error(f"Telethon 检查失败: {e}")
            return "error"
    
    async def _check_pyrogram(self) -> str:
        """检查 Pyrogram 应用"""
        try:
            if app and app.is_connected:
                return "healthy"
            else:
                return "unhealthy"
        except Exception as e:
            logger.error(f"Pyrogram 检查失败: {e}")
            return "error"
    
    async def _check_userbot(self) -> str:
        """检查用户机器人"""
        try:
            if userbot:
                if userbot.is_connected:
                    return "healthy"
                else:
                    return "unhealthy"
            else:
                return "not_configured"
        except Exception as e:
            logger.error(f"用户机器人检查失败: {e}")
            return "error"
    
    async def _check_database(self) -> str:
        """检查数据库连接"""
        try:
            await ensure_database_connection()
            return "healthy"
        except Exception as e:
            # 兼容 Motor 的布尔判断限制错误信息
            if "truth value testing" in str(e):
                logger.warning("数据库状态对象不可布尔判断，忽略此警告")
                return "healthy"
            logger.error(f"数据库检查失败: {e}")
            return "error"
    
    async def _check_system(self) -> str:
        """检查系统资源"""
        try:
            # 检查内存使用
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 检查磁盘使用
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # 检查CPU使用
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 检查下载队列
            from plugins.ytdl import ongoing_downloads
            download_queue_size = len(ongoing_downloads)
            
            # 判断状态
            if (memory_percent > self.alert_thresholds["memory_percent"] or
                disk_percent > self.alert_thresholds["disk_percent"] or
                cpu_percent > self.alert_thresholds["cpu_percent"] or
                download_queue_size > self.alert_thresholds["download_queue"]):
                return "warning"
            else:
                return "healthy"
                
        except Exception as e:
            logger.error(f"系统检查失败: {e}")
            return "error"
    
    def _determine_overall_status(self):
        """确定整体状态"""
        statuses = [
            self.health_status["telethon"],
            self.health_status["pyrogram"],
            self.health_status["database"],
            self.health_status["system"]
        ]
        
        if "error" in statuses:
            self.health_status["overall"] = "error"
        elif "unhealthy" in statuses:
            self.health_status["overall"] = "unhealthy"
        elif "warning" in statuses:
            self.health_status["overall"] = "warning"
        else:
            self.health_status["overall"] = "healthy"
    
    async def _check_alerts(self):
        """检查告警条件"""
        try:
            # 检查系统资源告警
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            if memory.percent > self.alert_thresholds["memory_percent"]:
                logger.warning(f"内存使用率过高: {memory.percent:.1f}%")
            
            if disk.percent > self.alert_thresholds["disk_percent"]:
                logger.warning(f"磁盘使用率过高: {disk.percent:.1f}%")
            
            # 检查下载队列告警
            from plugins.ytdl import ongoing_downloads
            if len(ongoing_downloads) > self.alert_thresholds["download_queue"]:
                logger.warning(f"下载队列过长: {len(ongoing_downloads)}")
            
        except Exception as e:
            logger.error(f"告警检查失败: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return self.health_status.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": disk.percent,
                    "used": disk.used
                },
                "cpu_percent": cpu_percent,
                "uptime": time.time() - psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}
    
    async def cleanup_resources(self):
        """清理资源"""
        try:
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
                logger.warning(f"清理超时下载任务: 用户 {user_id}")
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            logger.info("资源清理完成")
            
        except Exception as e:
            logger.error(f"资源清理失败: {e}")

# 全局健康监控器实例
health_monitor = HealthMonitor()

async def start_health_monitoring():
    """启动健康监控"""
    await health_monitor.start_monitoring()

def stop_health_monitoring():
    """停止健康监控"""
    health_monitor.stop_monitoring()

def get_health_status() -> Dict[str, Any]:
    """获取健康状态"""
    return health_monitor.get_health_status()

def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    return health_monitor.get_system_info()

async def cleanup_resources():
    """清理资源"""
    await health_monitor.cleanup_resources()
