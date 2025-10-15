#!/usr/bin/env python3
"""
健康检查脚本
用于云平台监控应用状态
"""

import asyncio
import sys
import os
import logging
import time
from typing import Dict, Any
from shared_client import client, app, userbot

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthChecker:
    """健康检查器类"""
    
    def __init__(self):
        self.checks = {
            "telethon": self._check_telethon,
            "pyrogram": self._check_pyrogram,
            "userbot": self._check_userbot,
            "system": self._check_system
        }
        self.results: Dict[str, Any] = {}
    
    async def _check_telethon(self) -> Dict[str, Any]:
        """检查 Telethon 客户端"""
        try:
            if client and client.is_connected():
                return {"status": "healthy", "message": "Telethon 客户端连接正常"}
            else:
                return {"status": "unhealthy", "message": "Telethon 客户端未连接"}
        except Exception as e:
            return {"status": "error", "message": f"Telethon 检查失败: {e}"}
    
    async def _check_pyrogram(self) -> Dict[str, Any]:
        """检查 Pyrogram 应用"""
        try:
            if app and app.is_connected:
                return {"status": "healthy", "message": "Pyrogram 应用连接正常"}
            else:
                return {"status": "unhealthy", "message": "Pyrogram 应用未连接"}
        except Exception as e:
            return {"status": "error", "message": f"Pyrogram 检查失败: {e}"}
    
    async def _check_userbot(self) -> Dict[str, Any]:
        """检查用户机器人（可选）"""
        try:
            if userbot:
                if userbot.is_connected:
                    return {"status": "healthy", "message": "用户机器人连接正常"}
                else:
                    return {"status": "warning", "message": "用户机器人未连接（可选）"}
            else:
                return {"status": "skipped", "message": "用户机器人未配置"}
        except Exception as e:
            return {"status": "error", "message": f"用户机器人检查失败: {e}"}
    
    async def _check_system(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            import psutil
            
            # 检查内存使用
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 检查磁盘使用
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            status = "healthy"
            if memory_percent > 90:
                status = "warning"
            if disk_percent > 90:
                status = "warning"
            
            return {
                "status": status,
                "message": f"系统资源正常 - 内存: {memory_percent:.1f}%, 磁盘: {disk_percent:.1f}%",
                "details": {
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent
                }
            }
        except ImportError:
            return {"status": "skipped", "message": "psutil 未安装，跳过系统检查"}
        except Exception as e:
            return {"status": "error", "message": f"系统检查失败: {e}"}
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        logger.info("开始执行健康检查...")
        start_time = time.time()
        
        # 并行执行所有检查
        tasks = []
        for name, check_func in self.checks.items():
            tasks.append(self._run_single_check(name, check_func))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, (name, check_func) in enumerate(self.checks.items()):
            result = results[i]
            if isinstance(result, Exception):
                self.results[name] = {"status": "error", "message": str(result)}
            else:
                self.results[name] = result
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 确定整体状态
        overall_status = self._determine_overall_status()
        
        return {
            "overall_status": overall_status,
            "duration": duration,
            "timestamp": time.time(),
            "checks": self.results
        }
    
    async def _run_single_check(self, name: str, check_func):
        """运行单个检查"""
        try:
            return await check_func()
        except Exception as e:
            logger.error(f"检查 {name} 时出错: {e}")
            return {"status": "error", "message": str(e)}
    
    def _determine_overall_status(self) -> str:
        """确定整体状态"""
        statuses = [result["status"] for result in self.results.values()]
        
        if "error" in statuses:
            return "error"
        elif "unhealthy" in statuses:
            return "unhealthy"
        elif "warning" in statuses:
            return "warning"
        else:
            return "healthy"
    
    def print_results(self, results: Dict[str, Any]):
        """打印检查结果"""
        print(f"\n{'='*50}")
        print(f"健康检查结果 - {results['overall_status'].upper()}")
        print(f"执行时间: {results['duration']:.2f}秒")
        print(f"{'='*50}")
        
        for name, result in results['checks'].items():
            status_icon = {
                "healthy": "✅",
                "warning": "⚠️",
                "unhealthy": "❌",
                "error": "💥",
                "skipped": "⏭️"
            }.get(result["status"], "❓")
            
            print(f"{status_icon} {name.upper()}: {result['message']}")
        
        print(f"{'='*50}")
        
        if results['overall_status'] == "healthy":
            print("🎉 所有核心服务运行正常")
        elif results['overall_status'] == "warning":
            print("⚠️ 服务运行正常，但有一些警告")
        else:
            print("❌ 服务存在问题，需要检查")

async def main():
    """主函数"""
    checker = HealthChecker()
    results = await checker.run_all_checks()
    checker.print_results(results)
    
    # 根据整体状态返回退出码
    if results['overall_status'] in ['healthy', 'warning']:
        return 0
    else:
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"健康检查脚本执行失败: {e}")
        print(f"❌ 健康检查脚本执行失败: {e}")
        sys.exit(1)
