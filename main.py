# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import asyncio
import signal
import sys
import os
import logging
import time
import traceback
from typing import Optional, Dict, Any
from shared_client import start_client, client, app, userbot
from utils.health_monitor import start_health_monitoring, stop_health_monitoring, cleanup_resources
from utils.func import init_database
import importlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 全局变量用于存储任务
running = True
restart_count = 0
max_restarts = 5
restart_delay = 5  # 秒

async def cleanup():
    """优雅地关闭所有连接"""
    global running
    running = False
    logger.info("正在关闭连接...")
    
    cleanup_tasks = []
    
    if userbot and userbot.is_connected:
        cleanup_tasks.append(("Userbot", userbot.stop()))
    
    if app and app.is_connected:
        cleanup_tasks.append(("Pyrogram 应用", app.stop()))
    
    if client and client.is_connected():
        cleanup_tasks.append(("Telethon 客户端", client.disconnect()))
    
    # 并行执行所有清理任务
    if cleanup_tasks:
        results = await asyncio.gather(*[task[1] for task in cleanup_tasks], return_exceptions=True)
        for (name, _), result in zip(cleanup_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"关闭 {name} 时出错: {result}")
            else:
                logger.info(f"{name} 已断开连接")
    
    logger.info("所有连接已关闭")

def signal_handler(signum, frame):
    """处理系统信号"""
    logger.info(f"收到信号 {signum}，正在关闭...")
    try:
        # 创建新的事件循环来处理清理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cleanup())
        loop.close()
    except Exception as e:
        logger.error(f"信号处理时出错: {e}")
    finally:
        sys.exit(0)

async def load_and_run_plugins():
    """加载并运行插件"""
    try:
        await start_client()
        logger.info("客户端启动成功")
    except Exception as e:
        logger.error(f"客户端启动失败: {e}")
        raise
    
    plugin_dir = "plugins"
    if not os.path.exists(plugin_dir):
        logger.warning(f"插件目录 {plugin_dir} 不存在")
        return
    
    plugins = [f[:-3] for f in os.listdir(plugin_dir) 
               if f.endswith(".py") and f != "__init__.py"]
    
    if not plugins:
        logger.warning("未找到任何插件")
        return
    
    logger.info(f"找到 {len(plugins)} 个插件: {', '.join(plugins)}")
    
    # 并行加载插件以提高启动速度
    plugin_tasks = []
    for plugin in plugins:
        task = asyncio.create_task(load_single_plugin(plugin))
        plugin_tasks.append(task)
    
    # 等待所有插件加载完成
    results = await asyncio.gather(*plugin_tasks, return_exceptions=True)
    
    # 处理加载结果
    for plugin, result in zip(plugins, results):
        if isinstance(result, Exception):
            logger.error(f"加载插件 {plugin} 时出错: {result}")
        elif result:
            logger.info(f"插件 {plugin} 加载成功")
        else:
            logger.warning(f"插件 {plugin} 加载失败")

async def load_single_plugin(plugin: str) -> bool:
    """加载单个插件"""
    try:
        module = importlib.import_module(f"plugins.{plugin}")
        if hasattr(module, f"run_{plugin}_plugin"):
            logger.info(f"运行 {plugin} 插件...")
            await getattr(module, f"run_{plugin}_plugin")()
            return True
        else:
            logger.warning(f"插件 {plugin} 没有 run_{plugin}_plugin 函数")
            return False
    except Exception as e:
        logger.error(f"加载插件 {plugin} 时出错: {e}")
        return False

async def main():
    """主函数"""
    global running, restart_count
    # 初始化数据库（在事件循环中）
    try:
        await init_database()
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        # 不直接退出，允许无数据库情况下继续运行（如果你的设计允许的话）
        # return
    try:
        await load_and_run_plugins()
        logger.info("所有插件加载完成")
    except Exception as e:
        logger.error(f"插件加载失败: {e}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        return
    
    # 启动健康监控
    health_monitor_task = asyncio.create_task(start_health_monitoring())
    
    # 保持运行直到收到停止信号
    logger.info("机器人开始运行...")
    last_cleanup = time.time()
    cleanup_interval = 3600  # 1小时清理一次资源
    
    try:
        while running:
            try:
                await asyncio.sleep(1)
                
                # 定期资源清理
                current_time = time.time()
                if current_time - last_cleanup > cleanup_interval:
                    await cleanup_resources()
                    last_cleanup = current_time
                    
            except asyncio.CancelledError:
                logger.info("收到取消信号")
                break
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                logger.error(f"错误详情: {traceback.format_exc()}")
                
                # 尝试自动恢复
                if restart_count < max_restarts:
                    restart_count += 1
                    logger.warning(f"尝试自动恢复 ({restart_count}/{max_restarts})...")
                    await asyncio.sleep(restart_delay)
                    try:
                        await cleanup()
                        await asyncio.sleep(2)
                        await load_and_run_plugins()
                        logger.info("自动恢复成功")
                    except Exception as recovery_error:
                        logger.error(f"自动恢复失败: {recovery_error}")
                        break
                else:
                    logger.error("达到最大重启次数，停止运行")
                    break
    finally:
        # 停止健康监控
        stop_health_monitoring()
        if not health_monitor_task.done():
            health_monitor_task.cancel()
            try:
                await health_monitor_task
            except asyncio.CancelledError:
                pass
    
    logger.info("主循环结束")

async def perform_health_check():
    """执行健康检查"""
    try:
        # 检查客户端连接状态
        if client and not client.is_connected():
            logger.warning("Telethon 客户端连接丢失")
        if app and not app.is_connected:
            logger.warning("Pyrogram 应用连接丢失")
        if userbot and not userbot.is_connected:
            logger.warning("用户机器人连接丢失")
        
        logger.debug("健康检查完成")
    except Exception as e:
        logger.error(f"健康检查时出错: {e}")

if __name__ == "__main__":
    # 设置信号处理
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("正在启动客户端...")
    
    try:
        # 使用新的 asyncio.run() 方法
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        logger.info("程序已退出")
