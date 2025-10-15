# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import logging
from datetime import timedelta, datetime
from typing import Optional, Union, List
from shared_client import client as bot_client
from telethon import events
from utils.func import (
    get_premium_details, 
    is_private_chat, 
    get_display_name, 
    get_user_data, 
    premium_users_collection, 
    is_premium_user
)
from config import OWNER_ID

# 配置日志
logger = logging.getLogger(__name__)


@bot_client.on(events.NewMessage(pattern='/status'))
async def status_handler(event):
    """处理 /status 命令，检查用户会话和机器人状态"""
    try:
        if not await is_private_chat(event):
            await event.respond("出于安全考虑，此命令只能在私聊中使用。")
            return
        
        user_id = event.sender_id
        user_data = await get_user_data(user_id)
        
        # 检查会话状态
        session_active = bool(user_data and "session_string" in user_data)
        
        # 检查自定义机器人状态
        bot_active = bool(user_data and "bot_token" in user_data)
        
        # 检查高级会员状态
        premium_status = "❌ 非高级会员"
        premium_details = await get_premium_details(user_id)
        
        if premium_details:
            try:
                # 转换为IST时区
                expiry_utc = premium_details["subscription_end"]
                expiry_ist = expiry_utc + timedelta(hours=5, minutes=30)
                formatted_expiry = expiry_ist.strftime("%d-%b-%Y %I:%M:%S %p")
                premium_status = f"✅ 高级会员有效期至 {formatted_expiry} (IST)"
            except Exception as e:
                logger.error(f"格式化高级会员过期时间时出错: {e}")
                premium_status = "✅ 高级会员（时间格式错误）"
        
        # 构建状态消息
        status_message = (
            "**你当前的状态：**\n\n"
            f"**登录状态：** {'✅ 已登录' if session_active else '❌ 未登录'}\n"
            f"**自定义机器人：** {'✅ 已配置' if bot_active else '❌ 未配置'}\n"
            f"**会员状态：** {premium_status}"
        )
        
        await event.respond(status_message)
        logger.info(f"用户 {user_id} 查询状态成功")
        
    except Exception as e:
        logger.error(f"处理状态命令时出错: {e}")
        await event.respond("❌ 获取状态信息时发生错误，请稍后重试。")

@bot_client.on(events.NewMessage(pattern='/transfer'))
async def transfer_premium_handler(event):
    """处理高级会员转赠命令"""
    try:
        if not await is_private_chat(event):
            await event.respond('出于安全考虑，此命令仅能在私聊中使用。')
            return
        
        user_id = event.sender_id
        sender = await event.get_sender()
        sender_name = get_display_name(sender)
        
        # 检查用户是否有高级会员
        if not await is_premium_user(user_id):
            await event.respond("❌ 你当前没有可转赠的高级会员。")
            return
        
        # 解析命令参数
        args = event.text.split()
        if len(args) != 2:
            await event.respond('用法：/transfer user_id\n示例：/transfer 123456789')
            return
        
        try:
            target_user_id = int(args[1])
        except ValueError:
            await event.respond('❌ 用户ID无效，请提供数字ID。')
            return
        
        # 验证目标用户
        if target_user_id == user_id:
            await event.respond('❌ 不能把会员转给自己。')
            return
        
        if await is_premium_user(target_user_id):
            await event.respond('❌ 目标用户已经是高级会员。')
            return
        
        # 获取转赠者的会员详情
        premium_details = await get_premium_details(user_id)
        if not premium_details:
            await event.respond('❌ 获取你的会员信息失败。')
            return
        
        # 获取目标用户名称
        target_name = 'Unknown'
        try:
            target_entity = await bot_client.get_entity(target_user_id)
            target_name = get_display_name(target_entity)
        except Exception as e:
            logger.warning(f'无法获取目标用户名称: {e}')
        
        # 执行转赠
        now = datetime.now()
        expiry_date = premium_details['subscription_end']
        
        # 更新目标用户的会员信息
        await premium_users_collection.update_one(
            {'user_id': target_user_id}, 
            {'$set': {
                'user_id': target_user_id,
                'subscription_start': now, 
                'subscription_end': expiry_date,
                'expireAt': expiry_date, 
                'transferred_from': user_id,
                'transferred_from_name': sender_name
            }}, 
            upsert=True
        )
        
        # 删除转赠者的会员信息
        await premium_users_collection.delete_one({'user_id': user_id})
        
        # 格式化过期时间
        expiry_ist = expiry_date + timedelta(hours=5, minutes=30)
        formatted_expiry = expiry_ist.strftime('%d-%b-%Y %I:%M:%S %p')
        
        # 通知转赠者
        await event.respond(
            f'✅ 已成功将高级会员转给 {target_name} ({target_user_id})，你的会员资格已移除。'
        )
        
        # 通知目标用户
        try:
            await bot_client.send_message(
                target_user_id,
                f'🎁 你收到了 {sender_name} ({user_id}) 转赠的高级会员，有效期至 {formatted_expiry} (IST)。'
            )
        except Exception as e:
            logger.error(f'无法通知目标用户 {target_user_id}: {e}')
        
        # 通知管理员
        try:
            owner_id = int(OWNER_ID) if isinstance(OWNER_ID, str) else OWNER_ID[0] if isinstance(OWNER_ID, list) else OWNER_ID
            await bot_client.send_message(
                owner_id,
                f'♻️ 会员转赠：{sender_name} ({user_id}) 已将会员转给 {target_name} ({target_user_id})。到期：{formatted_expiry}'
            )
        except Exception as e:
            logger.error(f'无法通知管理员关于会员转赠: {e}')
        
        logger.info(f"用户 {user_id} 成功将会员转赠给 {target_user_id}")
        
    except Exception as e:
        logger.error(f'转赠高级会员时出错: {e}')
        await event.respond(f'❌ 转赠过程中发生错误：{str(e)}')
@bot_client.on(events.NewMessage(pattern='/rem'))
async def remove_premium_handler(event):
    """处理移除高级会员命令（仅限管理员）"""
    try:
        user_id = event.sender_id
        
        # 检查是否为私聊
        if not await is_private_chat(event):
            return
        
        # 检查管理员权限
        if user_id not in OWNER_ID:
            await event.respond("❌ 你没有权限使用此命令。")
            return
        
        # 解析命令参数
        args = event.text.split()
        if len(args) != 2:
            await event.respond('用法：/rem user_id\n示例：/rem 123456789')
            return
        
        try:
            target_user_id = int(args[1])
        except ValueError:
            await event.respond('❌ 用户ID无效，请提供数字ID。')
            return
        
        # 检查目标用户是否有高级会员
        if not await is_premium_user(target_user_id):
            await event.respond(f'❌ 用户 {target_user_id} 没有高级会员。')
            return
        
        # 获取目标用户名称
        target_name = 'Unknown'
        try:
            target_entity = await bot_client.get_entity(target_user_id)
            target_name = get_display_name(target_entity)
        except Exception as e:
            logger.warning(f'无法获取目标用户名称: {e}')
        
        # 移除高级会员
        result = await premium_users_collection.delete_one({'user_id': target_user_id})
        
        if result.deleted_count > 0:
            await event.respond(
                f'✅ 已成功移除 {target_name} ({target_user_id}) 的高级会员。'
            )
            
            # 通知被移除的用户
            try:
                await bot_client.send_message(
                    target_user_id,
                    '⚠️ 你的高级会员已被管理员移除。如有疑问，请联系管理员。'
                )
            except Exception as e:
                logger.error(f'无法通知用户 {target_user_id} 关于会员移除: {e}')
            
            logger.info(f"管理员 {user_id} 移除了用户 {target_user_id} 的高级会员")
        else:
            await event.respond(f'❌ 无法移除用户 {target_user_id} 的高级会员。')
            
    except Exception as e:
        logger.error(f'移除高级会员时出错: {e}')
        await event.respond(f'❌ 移除过程中发生错误：{str(e)}')

async def run_stats_plugin():
    """运行统计插件"""
    logger.info("统计插件已加载")