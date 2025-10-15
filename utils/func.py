# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import concurrent.futures
import time
import os
import re
import cv2
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB as MONGO_URI, DB_NAME

# 配置日志
logger = logging.getLogger(__name__)

PUBLIC_LINK_PATTERN = re.compile(r'(https?://)?(t\.me|telegram\.me)/([^/]+)(/(\d+))?')
PRIVATE_LINK_PATTERN = re.compile(r'(https?://)?(t\.me|telegram\.me)/c/(\d+)(/(\d+))?')
VIDEO_EXTENSIONS = {"mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpeg", "mpg", "3gp"}

# 数据库连接配置
MAX_RETRIES = 3
RETRY_DELAY = 2
CONNECTION_TIMEOUT = 30

# 数据库连接
mongo_client = None
db = None
users_collection = None
premium_users_collection = None
statistics_collection = None
codedb = None

async def init_database():
    """初始化数据库连接"""
    global mongo_client, db, users_collection, premium_users_collection, statistics_collection, codedb
    
    for attempt in range(MAX_RETRIES):
        try:
            mongo_client = AsyncIOMotorClient(
                MONGO_URI,
                serverSelectionTimeoutMS=CONNECTION_TIMEOUT * 1000,
                connectTimeoutMS=CONNECTION_TIMEOUT * 1000,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=30000
            )
            
            # 测试连接
            await mongo_client.admin.command('ping')
            
            db = mongo_client[DB_NAME]
            users_collection = db["users"]
            premium_users_collection = db["premium_users"]
            statistics_collection = db["statistics"]
            codedb = db["redeem_code"]
            
            # 创建索引
            await create_indexes()
            
            logger.info("数据库连接成功")
            return True
            
        except Exception as e:
            logger.warning(f"数据库连接失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.error("数据库连接失败，已达到最大重试次数")
                raise

async def create_indexes():
    """创建数据库索引"""
    try:
        # 用户集合索引
        await users_collection.create_index("user_id", unique=True)
        await users_collection.create_index("updated_at")
        
        # 高级用户集合索引
        await premium_users_collection.create_index("user_id", unique=True)
        await premium_users_collection.create_index("subscription_end")
        await premium_users_collection.create_index("expireAt", expireAfterSeconds=0)
        
        # 统计集合索引
        await statistics_collection.create_index("date")
        
        logger.debug("数据库索引创建完成")
    except Exception as e:
        logger.warning(f"创建数据库索引时出错: {e}")

async def ensure_database_connection():
    """确保数据库连接正常"""
    global mongo_client, db
    
    if mongo_client is None or db is None:
        await init_database()
        return
    
    try:
        # 测试连接
        await mongo_client.admin.command('ping')
    except Exception as e:
        logger.warning(f"数据库连接丢失，尝试重新连接: {e}")
        await init_database()

# 注意：不要在导入时创建异步任务来初始化数据库。
# 数据库初始化应在事件循环已经运行后由启动流程显式调用。

# ------- < start > Session Encoder don't change -------

a1 = "c2F2ZV9yZXN0cmljdGVkX2NvbnRlbnRfYm90cw=="
a2 = "Nzk2"
a3 = "Z2V0X21lc3NhZ2Vz" 
a4 = "cmVwbHlfcGhvdG8=" 
a5 = "c3RhcnQ="
attr1 = "cGhvdG8="
attr2 = "ZmlsZV9pZA=="
a7 = "SGkg8J+RiyBXZWxjb21lLCBXYW5uYSBpbnRyby4uLj8gCgrinLPvuI8gSSBjYW4gc2F2ZSBwb3N0cyBmcm9tIGNoYW5uZWxzIG9yIGdyb3VwcyB3aGVyZSBmb3J3YXJkaW5nIGlzIG9mZi4gSSBjYW4gZG93bmxvYWQgdmlkZW9zL2F1ZGlvIGZyb20gWVQsIElOU1RBLCAuLi4gc29jaWFsIHBsYXRmb3JtcwrinLPvuI8gU2ltcGx5IHNlbmQgdGhlIHBvc3QgbGluayBvZiBhIHB1YmxpYyBjaGFubmVsLiBGb3IgcHJpdmF0ZSBjaGFubmVscywgZG8gL2xvZ2luLiBTZW5kIC9oZWxwIHRvIGtub3cgbW9yZS4="
a8 = "Sm9pbiBDaGFubmVs"
a9 = "R2V0IFByZW1pdW0=" 
a10 = "aHR0cHM6Ly90Lm1lL3RlYW1fc3B5X3Bybw==" 
a11 = "aHR0cHM6Ly90Lm1lL2tpbmdvZnBhdGFs" 

# ------- < end > Session Encoder don't change --------

def is_private_link(link: str) -> bool:
    """检查链接是否为私有频道链接"""
    return bool(PRIVATE_LINK_PATTERN.match(link))


def thumbnail(sender: Union[int, str]) -> Optional[str]:
    """获取用户缩略图路径"""
    thumb_path = f'{sender}.jpg'
    return thumb_path if os.path.exists(thumb_path) else None


def hhmmss(seconds: int) -> str:
    """将秒数转换为 HH:MM:SS 格式"""
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


def E(link: str) -> tuple[Optional[str], Optional[int], Optional[str]]:
    """解析 Telegram 链接，返回频道ID、消息ID和类型"""
    private_match = re.match(r'https://t\.me/c/(\d+)/(?:\d+/)?(\d+)', link)
    public_match = re.match(r'https://t\.me/([^/]+)/(?:\d+/)?(\d+)', link)
    
    if private_match:
        return f'-100{private_match.group(1)}', int(private_match.group(2)), 'private'
    elif public_match:
        return public_match.group(1), int(public_match.group(2)), 'public'
    
    return None, None, None


def get_display_name(user) -> str:
    """获取用户显示名称"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    elif user.last_name:
        return user.last_name
    elif user.username:
        return user.username
    else:
        return "Unknown User"


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def get_dummy_filename(info: Dict[str, Any]) -> str:
    """根据文件信息生成虚拟文件名"""
    file_type = info.get("type", "file")
    extension = {
        "video": "mp4",
        "photo": "jpg",
        "document": "pdf",
        "audio": "mp3"
    }.get(file_type, "bin")
    
    return f"downloaded_file_{int(time.time())}.{extension}"


async def is_private_chat(event) -> bool:
    """检查是否为私聊"""
    return event.is_private


async def save_user_data(user_id: int, key: str, value: Any) -> bool:
    """保存用户数据"""
    try:
        await ensure_database_connection()
        
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {key: value, "updated_at": datetime.now()}},
            upsert=True
        )
        logger.debug(f"保存用户 {user_id} 的数据: {key} = {value}")
        return True
    except Exception as e:
        logger.error(f"保存用户 {user_id} 数据时出错: {e}")
        return False


async def get_user_data_key(user_id: int, key: str, default: Any = None) -> Any:
    """获取用户数据的特定键值"""
    try:
        user_data = await users_collection.find_one({"user_id": int(user_id)})
        return user_data.get(key, default) if user_data else default
    except Exception as e:
        logger.error(f"获取用户 {user_id} 数据键 {key} 时出错: {e}")
        return default


async def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """获取用户完整数据"""
    try:
        user_data = await users_collection.find_one({"user_id": user_id})
        return user_data
    except Exception as e:
        logger.error(f"获取用户 {user_id} 数据时出错: {e}")
        return None


async def save_user_session(user_id: int, session_string: str) -> bool:
    """保存用户会话字符串"""
    try:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "session_string": session_string,
                "updated_at": datetime.now()
            }},
            upsert=True
        )
        logger.info(f"已保存用户 {user_id} 的会话")
        return True
    except Exception as e:
        logger.error(f"保存用户 {user_id} 会话时出错: {e}")
        return False


async def remove_user_session(user_id: int) -> bool:
    """移除用户会话字符串"""
    try:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$unset": {"session_string": ""}}
        )
        logger.info(f"已移除用户 {user_id} 的会话")
        return True
    except Exception as e:
        logger.error(f"移除用户 {user_id} 会话时出错: {e}")
        return False


async def save_user_bot(user_id: int, bot_token: str) -> bool:
    """保存用户机器人令牌"""
    try:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "bot_token": bot_token,
                "updated_at": datetime.now()
            }},
            upsert=True
        )
        logger.info(f"已保存用户 {user_id} 的机器人令牌")
        return True
    except Exception as e:
        logger.error(f"保存用户 {user_id} 机器人令牌时出错: {e}")
        return False


async def remove_user_bot(user_id: int) -> bool:
    """移除用户机器人令牌"""
    try:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$unset": {"bot_token": ""}}
        )
        logger.info(f"已移除用户 {user_id} 的机器人令牌")
        return True
    except Exception as e:
        logger.error(f"移除用户 {user_id} 机器人令牌时出错: {e}")
        return False


async def process_text_with_rules(user_id: int, text: str) -> str:
    """根据用户规则处理文本"""
    if not text:
        return ""
    
    try:
        replacements = await get_user_data_key(user_id, "replacement_words", {})
        delete_words = await get_user_data_key(user_id, "delete_words", [])
        
        processed_text = text
        
        # 应用替换规则
        for word, replacement in replacements.items():
            processed_text = processed_text.replace(word, replacement)
        
        # 应用删除规则
        if delete_words:
            words = processed_text.split()
            filtered_words = [w for w in words if w not in delete_words]
            processed_text = " ".join(filtered_words)
        
        return processed_text
    except Exception as e:
        logger.error(f"处理文本规则时出错: {e}")
        return text


async def screenshot(video: str, duration: int, sender: Union[int, str]) -> Optional[str]:
    """从视频生成截图"""
    existing_screenshot = f"{sender}.jpg"
    if os.path.exists(existing_screenshot):
        return existing_screenshot

    time_stamp = hhmmss(duration // 2)
    output_file = datetime.now().isoformat("_", "seconds") + ".jpg"

    cmd = [
        "ffmpeg",
        "-ss", time_stamp,
        "-i", video,
        "-frames:v", "1",
        output_file,
        "-y"
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()

        if os.path.isfile(output_file):
            logger.debug(f"成功生成截图: {output_file}")
            return output_file
        else:
            logger.error(f"FFmpeg 错误: {stderr.decode().strip()}")
            return None
    except Exception as e:
        logger.error(f"生成截图时出错: {e}")
        return None


async def get_video_metadata(file_path: str) -> Dict[str, int]:
    """获取视频元数据"""
    default_values = {'width': 1, 'height': 1, 'duration': 1}
    
    if not os.path.exists(file_path):
        logger.warning(f"视频文件不存在: {file_path}")
        return default_values
    
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    
    try:
        def _extract_metadata():
            try:
                vcap = cv2.VideoCapture(file_path)
                if not vcap.isOpened():
                    logger.warning(f"无法打开视频文件: {file_path}")
                    return default_values

                width = round(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = round(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = vcap.get(cv2.CAP_PROP_FPS)
                frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)

                if fps <= 0:
                    logger.warning(f"视频 FPS 无效: {fps}")
                    vcap.release()
                    return default_values

                duration = round(frame_count / fps)
                if duration <= 0:
                    logger.warning(f"视频时长无效: {duration}")
                    vcap.release()
                    return default_values

                vcap.release()
                metadata = {'width': width, 'height': height, 'duration': duration}
                logger.debug(f"视频元数据: {metadata}")
                return metadata
            except Exception as e:
                logger.error(f"提取视频元数据时出错: {e}")
                return default_values
        
        return await loop.run_in_executor(executor, _extract_metadata)
        
    except Exception as e:
        logger.error(f"获取视频元数据时出错: {e}")
        return default_values
    finally:
        executor.shutdown(wait=False)


async def add_premium_user(user_id: int, duration_value: int, duration_unit: str) -> tuple[bool, Union[str, datetime]]:
    """添加高级用户"""
    try:
        now = datetime.now()
        expiry_date = None
        
        # 计算过期时间
        duration_units = {
            "min": lambda x: now + timedelta(minutes=x),
            "hours": lambda x: now + timedelta(hours=x),
            "days": lambda x: now + timedelta(days=x),
            "weeks": lambda x: now + timedelta(weeks=x),
            "month": lambda x: now + timedelta(days=30 * x),
            "year": lambda x: now + timedelta(days=365 * x),
            "decades": lambda x: now + timedelta(days=3650 * x)
        }
        
        if duration_unit in duration_units:
            expiry_date = duration_units[duration_unit](duration_value)
        else:
            return False, "无效的时长单位"
            
        await premium_users_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "subscription_start": now,
                "subscription_end": expiry_date,
                "expireAt": expiry_date
            }},
            upsert=True
        )
        
        # 创建 TTL 索引
        await premium_users_collection.create_index("expireAt", expireAfterSeconds=0)
        
        logger.info(f"已添加高级用户 {user_id}，过期时间: {expiry_date}")
        return True, expiry_date
    except Exception as e:
        logger.error(f"添加高级用户 {user_id} 时出错: {e}")
        return False, str(e)


async def is_premium_user(user_id: int) -> bool:
    """检查用户是否为高级用户"""
    try:
        user = await premium_users_collection.find_one({"user_id": user_id})
        if user and "subscription_end" in user:
            now = datetime.now()
            is_premium = now < user["subscription_end"]
            logger.debug(f"用户 {user_id} 高级状态: {is_premium}")
            return is_premium
        return False
    except Exception as e:
        logger.error(f"检查用户 {user_id} 高级状态时出错: {e}")
        return False


async def get_premium_details(user_id: int) -> Optional[Dict[str, Any]]:
    """获取用户高级会员详情"""
    try:
        user = await premium_users_collection.find_one({"user_id": user_id})
        if user and "subscription_end" in user:
            return user
        return None
    except Exception as e:
        logger.error(f"获取用户 {user_id} 高级详情时出错: {e}")
        return None
