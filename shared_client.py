# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import asyncio
import logging
import time
from typing import Optional, Tuple
from telethon import TelegramClient
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING

# 配置日志
logger = logging.getLogger(__name__)

# 初始化客户端
client: Optional[TelegramClient] = None
app: Optional[Client] = None
userbot: Optional[Client] = None

# 连接配置
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒
CONNECTION_TIMEOUT = 30  # 秒

async def start_client() -> Tuple[Optional[TelegramClient], Optional[Client], Optional[Client]]:
    """启动所有客户端"""
    global client, app, userbot
    
    try:
        # 验证必要的配置
        if not all([API_ID, API_HASH, BOT_TOKEN]):
            raise ValueError("缺少必要的配置: API_ID, API_HASH, BOT_TOKEN")
        
        # 启动 Telethon 客户端
        logger.info("正在启动 Telethon 客户端...")
        client = await start_telethon_client()
        
        # 启动 Pyrogram 应用
        logger.info("正在启动 Pyrogram 应用...")
        app = await start_pyrogram_app()
        
        # 启动用户机器人（如果提供了 STRING）
        if STRING:
            userbot = await start_userbot()
        else:
            logger.info("未提供 STRING，跳过用户机器人启动")
            userbot = None
            
        return client, app, userbot
        
    except Exception as e:
        logger.error(f"启动客户端时出错: {e}")
        # 如果启动失败，尝试清理已启动的客户端
        await cleanup_clients()
        raise e

async def start_telethon_client() -> TelegramClient:
    """启动 Telethon 客户端（带重试机制）"""
    for attempt in range(MAX_RETRIES):
        try:
            client = TelegramClient("telethonbot", API_ID, API_HASH)
            if not client.is_connected():
                await asyncio.wait_for(
                    client.start(bot_token=BOT_TOKEN),
                    timeout=CONNECTION_TIMEOUT
                )
            logger.info("Telethon 客户端已启动")
            return client
        except asyncio.TimeoutError:
            logger.warning(f"Telethon 客户端连接超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
        except Exception as e:
            logger.warning(f"Telethon 客户端启动失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
        
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_DELAY)
    
    raise Exception("Telethon 客户端启动失败，已达到最大重试次数")

async def start_pyrogram_app() -> Client:
    """启动 Pyrogram 应用（带重试机制）"""
    for attempt in range(MAX_RETRIES):
        try:
            app = Client("pyrogrambot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
            await asyncio.wait_for(
                app.start(),
                timeout=CONNECTION_TIMEOUT
            )
            logger.info("Pyrogram 应用已启动")
            return app
        except asyncio.TimeoutError:
            logger.warning(f"Pyrogram 应用连接超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
        except Exception as e:
            logger.warning(f"Pyrogram 应用启动失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
        
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_DELAY)
    
    raise Exception("Pyrogram 应用启动失败，已达到最大重试次数")

async def start_userbot() -> Optional[Client]:
    """启动用户机器人（带重试机制）"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info("正在启动用户机器人...")
            userbot = Client("4gbbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
            await asyncio.wait_for(
                userbot.start(),
                timeout=CONNECTION_TIMEOUT
            )
            logger.info("用户机器人已启动")
            return userbot
        except asyncio.TimeoutError:
            logger.warning(f"用户机器人连接超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
        except Exception as e:
            logger.warning(f"用户机器人启动失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
        
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_DELAY)
    
    logger.warning("用户机器人启动失败，请检查你的高级会话字符串是否有效或已过期")
    return None

async def cleanup_clients():
    """清理所有客户端连接"""
    global client, app, userbot
    
    cleanup_tasks = []
    
    if userbot and userbot.is_connected:
        cleanup_tasks.append(("用户机器人", userbot.stop()))
    
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

