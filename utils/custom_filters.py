# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import logging
from typing import Dict, Optional, Any
from pyrogram import filters
from pyrogram.types import Message

# 配置日志
logger = logging.getLogger(__name__)

# 用户步骤状态存储
user_steps: Dict[int, Any] = {}

def login_filter_func(_, __, message: Message) -> bool:
    """检查用户是否正在进行登录流程"""
    try:
        user_id = message.from_user.id
        return user_id in user_steps
    except Exception as e:
        logger.error(f"登录过滤器检查时出错: {e}")
        return False

# 创建登录进行中的过滤器
login_in_progress = filters.create(login_filter_func)

def set_user_step(user_id: int, step: Optional[Any] = None) -> None:
    """设置用户当前步骤"""
    try:
        if step is not None:
            user_steps[user_id] = step
            logger.debug(f"用户 {user_id} 步骤设置为: {step}")
        else:
            user_steps.pop(user_id, None)
            logger.debug(f"用户 {user_id} 步骤已清除")
    except Exception as e:
        logger.error(f"设置用户 {user_id} 步骤时出错: {e}")

def get_user_step(user_id: int) -> Optional[Any]:
    """获取用户当前步骤"""
    try:
        return user_steps.get(user_id)
    except Exception as e:
        logger.error(f"获取用户 {user_id} 步骤时出错: {e}")
        return None

def clear_user_step(user_id: int) -> bool:
    """清除用户步骤并返回是否成功"""
    try:
        if user_id in user_steps:
            del user_steps[user_id]
            logger.debug(f"已清除用户 {user_id} 的步骤")
            return True
        return False
    except Exception as e:
        logger.error(f"清除用户 {user_id} 步骤时出错: {e}")
        return False

def get_all_user_steps() -> Dict[int, Any]:
    """获取所有用户步骤（用于调试）"""
    return user_steps.copy()