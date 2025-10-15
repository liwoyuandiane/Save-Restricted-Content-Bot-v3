# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os
import logging
from typing import Dict, Any, Optional
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    BadRequest, 
    SessionPasswordNeeded, 
    PhoneCodeInvalid, 
    PhoneCodeExpired, 
    MessageNotModified
)
from config import API_HASH, API_ID
from shared_client import app as bot
from utils.func import save_user_session, get_user_data, remove_user_session, save_user_bot, remove_user_bot
from utils.encrypt import ecs, dcs
from plugins.batch import UB, UC
from utils.custom_filters import login_in_progress, set_user_step, get_user_step

# 配置日志
logger = logging.getLogger(__name__)

# 常量定义
MODEL = "v3saver Team SPY"
STEP_PHONE = 1
STEP_CODE = 2
STEP_PASSWORD = 3

# 登录缓存
login_cache: Dict[int, Dict[str, Any]] = {}

@bot.on_message(filters.command('login'))
async def login_command(client, message):
    """处理登录命令"""
    user_id = message.from_user.id
    set_user_step(user_id, STEP_PHONE)
    login_cache.pop(user_id, None)
    
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"无法删除消息: {e}")
    
    status_msg = await message.reply(
        """请发送带国家区号的手机号
示例：`+8613812345678`"""
    )
    login_cache[user_id] = {'status_msg': status_msg}
    
    
@bot.on_message(filters.command("setbot"))
async def set_bot_token(client, message):
    """设置用户机器人令牌"""
    user_id = message.from_user.id
    args = message.text.split(" ", 1)
    
    # 清理旧的机器人实例
    if user_id in UB:
        try:
            await UB[user_id].stop()
            if UB.get(user_id, None):
                del UB[user_id]
            
            # 清理会话文件
            session_file = f"user_{user_id}.session"
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                except Exception as e:
                    logger.warning(f"无法删除会话文件 {session_file}: {e}")
            
            logger.info(f"已停止并移除用户 {user_id} 的旧机器人")
        except Exception as e:
            logger.error(f"停止用户 {user_id} 的旧机器人时出错: {e}")
            if UB.get(user_id, None):
                del UB[user_id]

    if len(args) < 2:
        await message.reply_text("⚠️ 请输入机器人令牌，格式：/setbot <token>", quote=True)
        return

    bot_token = args[1].strip()
    if await save_user_bot(user_id, bot_token):
        await message.reply_text("✅ 机器人令牌保存成功。", quote=True)
    else:
        await message.reply_text("❌ 保存机器人令牌失败，请重试。", quote=True)
    
    
@bot.on_message(filters.command("rembot"))
async def rem_bot_token(client, message):
    """移除用户机器人令牌"""
    user_id = message.from_user.id
    
    # 停止并清理机器人实例
    if user_id in UB:
        try:
            await UB[user_id].stop()
            if UB.get(user_id, None):
                del UB[user_id]
            logger.info(f"已停止并移除用户 {user_id} 的机器人")
        except Exception as e:
            logger.error(f"停止用户 {user_id} 的机器人时出错: {e}")
            if UB.get(user_id, None):
                del UB[user_id]
    
    # 清理会话文件
    session_file = f"user_{user_id}.session"
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
        except Exception as e:
            logger.warning(f"无法删除会话文件 {session_file}: {e}")
    
    # 从数据库移除机器人令牌
    if await remove_user_bot(user_id):
        await message.reply_text("✅ 已移除机器人令牌。", quote=True)
    else:
        await message.reply_text("❌ 移除机器人令牌失败，请重试。", quote=True)

    
@bot.on_message(login_in_progress & filters.text & filters.private & ~filters.command([
    'start', 'batch', 'cancel', 'login', 'logout', 'stop', 'set', 'pay',
    'redeem', 'gencode', 'generate', 'keyinfo', 'encrypt', 'decrypt', 'keys', 'setbot', 'rembot']))
async def handle_login_steps(client, message):
    """处理登录流程的各个步骤"""
    user_id = message.from_user.id
    text = message.text.strip()
    step = get_user_step(user_id)
    
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f'无法删除消息: {e}')
    
    status_msg = login_cache.get(user_id, {}).get('status_msg')
    if not status_msg:
        status_msg = await message.reply('处理中…')
        if user_id not in login_cache:
            login_cache[user_id] = {}
        login_cache[user_id]['status_msg'] = status_msg
    try:
        if step == STEP_PHONE:
            if not text.startswith('+'):
                await edit_message_safely(status_msg,
                    '❌ 请输入以 + 开头的有效手机号')
                return
            
            await edit_message_safely(status_msg, '🔄 正在处理手机号…')
            temp_client = Client(
                f'temp_{user_id}', 
                api_id=API_ID, 
                api_hash=API_HASH, 
                device_model=MODEL, 
                in_memory=True
            )
            
            try:
                await temp_client.connect()
                sent_code = await temp_client.send_code(text)
                
                # 更新登录缓存
                login_cache[user_id].update({
                    'phone': text,
                    'phone_code_hash': sent_code.phone_code_hash,
                    'temp_client': temp_client
                })
                
                set_user_step(user_id, STEP_CODE)
                await edit_message_safely(status_msg,
                    """✅ 验证码已发送至你的 Telegram。
                    
请输入你收到的验证码，如：1 2 3 4 5（空格分隔）:"""
                )
            except BadRequest as e:
                await edit_message_safely(status_msg,
                    f"""❌ 错误：{str(e)}
请使用 /login 重试。""")
                await temp_client.disconnect()
                set_user_step(user_id, None)
        elif step == STEP_CODE:
            code = text.replace(' ', '')
            user_cache = login_cache.get(user_id, {})
            phone = user_cache.get('phone')
            phone_code_hash = user_cache.get('phone_code_hash')
            temp_client = user_cache.get('temp_client')
            
            if not all([phone, phone_code_hash, temp_client]):
                await edit_message_safely(status_msg, '❌ 登录会话已过期，请重新开始。')
                set_user_step(user_id, None)
                return
            
            try:
                await edit_message_safely(status_msg, '🔄 正在验证验证码…')
                await temp_client.sign_in(phone, phone_code_hash, code)
                session_string = await temp_client.export_session_string()
                encrypted_session = ecs(session_string)
                
                if await save_user_session(user_id, encrypted_session):
                    await temp_client.disconnect()
                    temp_status_msg = login_cache[user_id]['status_msg']
                    login_cache.pop(user_id, None)
                    login_cache[user_id] = {'status_msg': temp_status_msg}
                    await edit_message_safely(status_msg, "✅ 登录成功！")
                    set_user_step(user_id, None)
                else:
                    await edit_message_safely(status_msg, "❌ 保存会话失败，请重试。")
                    
            except SessionPasswordNeeded:
                set_user_step(user_id, STEP_PASSWORD)
                await edit_message_safely(status_msg,
                    """🔒 你已开启两步验证。
请输入你的密码："""
                )
            except (PhoneCodeInvalid, PhoneCodeExpired) as e:
                await edit_message_safely(status_msg,
                    f'❌ {str(e)}。请使用 /login 重试。')
                await temp_client.disconnect()
                login_cache.pop(user_id, None)
                set_user_step(user_id, None)
        elif step == STEP_PASSWORD:
            user_cache = login_cache.get(user_id, {})
            temp_client = user_cache.get('temp_client')
            
            if not temp_client:
                await edit_message_safely(status_msg, '❌ 登录会话已过期，请重新开始。')
                set_user_step(user_id, None)
                return
            
            try:
                await edit_message_safely(status_msg, '🔄 正在验证密码…')
                await temp_client.check_password(text)
                session_string = await temp_client.export_session_string()
                encrypted_session = ecs(session_string)
                
                if await save_user_session(user_id, encrypted_session):
                    await temp_client.disconnect()
                    temp_status_msg = login_cache[user_id]['status_msg']
                    login_cache.pop(user_id, None)
                    login_cache[user_id] = {'status_msg': temp_status_msg}
                    await edit_message_safely(status_msg, "✅ 登录成功！")
                    set_user_step(user_id, None)
                else:
                    await edit_message_safely(status_msg, "❌ 保存会话失败，请重试。")
                    
            except BadRequest as e:
                await edit_message_safely(status_msg,
                    f"""❌ 密码错误：{str(e)}
请重试：""")
    except Exception as e:
        logger.error(f'登录流程中发生错误: {str(e)}')
        await edit_message_safely(status_msg,
            f"""❌ 发生错误：{str(e)}
请使用 /login 重试。""")
        
        # 清理资源
        if user_id in login_cache and 'temp_client' in login_cache[user_id]:
            try:
                await login_cache[user_id]['temp_client'].disconnect()
            except Exception as cleanup_error:
                logger.warning(f"清理临时客户端时出错: {cleanup_error}")
        
        login_cache.pop(user_id, None)
        set_user_step(user_id, None)

async def edit_message_safely(message, text):
    """安全地编辑消息并处理错误"""
    try:
        await message.edit(text)
    except MessageNotModified:
        pass
    except Exception as e:
        logger.error(f'编辑消息时出错: {e}')
        
@bot.on_message(filters.command('cancel'))
async def cancel_command(client, message):
    """取消当前登录流程"""
    user_id = message.from_user.id
    
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"无法删除消息: {e}")
    
    if get_user_step(user_id):
        status_msg = login_cache.get(user_id, {}).get('status_msg')
        
        # 清理临时客户端
        if user_id in login_cache and 'temp_client' in login_cache[user_id]:
            try:
                await login_cache[user_id]['temp_client'].disconnect()
            except Exception as e:
                logger.warning(f"清理临时客户端时出错: {e}")
        
        login_cache.pop(user_id, None)
        set_user_step(user_id, None)
        
        if status_msg:
            await edit_message_safely(status_msg,
                '✅ 已取消登录流程。可用 /login 重新开始。')
        else:
            temp_msg = await message.reply(
                '✅ 已取消登录流程。可用 /login 重新开始。')
            await temp_msg.delete(5)
    else:
        temp_msg = await message.reply('当前没有可取消的登录流程。')
        await temp_msg.delete(5)
        
@bot.on_message(filters.command('logout'))
async def logout_command(client, message):
    """处理登出命令"""
    user_id = message.from_user.id
    
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"无法删除消息: {e}")
    
    status_msg = await message.reply('🔄 正在处理登出请求…')
    
    try:
        session_data = await get_user_data(user_id)
        
        if not session_data or 'session_string' not in session_data:
            await edit_message_safely(status_msg, '❌ 未找到你的活动会话。')
            return
        
        encss = session_data['session_string']
        session_string = dcs(encss)
        temp_client = Client(
            f'temp_logout_{user_id}', 
            api_id=API_ID,
            api_hash=API_HASH, 
            session_string=session_string
        )
        
        try:
            await temp_client.connect()
            await temp_client.log_out()
            await edit_message_safely(status_msg,
                '✅ 已成功终止 Telegram 会话，正在从数据库移除…'
            )
        except Exception as e:
            logger.error(f'终止会话时出错: {str(e)}')
            await edit_message_safely(status_msg,
                f"""⚠️ 终止 Telegram 会话出错：{str(e)}
仍将从数据库移除…"""
            )
        finally:
            await temp_client.disconnect()
        
        # 从数据库移除会话
        if await remove_user_session(user_id):
            await edit_message_safely(status_msg, '✅ 已成功登出！')
        else:
            await edit_message_safely(status_msg, '⚠️ 登出完成，但数据库更新可能失败。')
        
        # 清理本地文件
        session_file = f"{user_id}_client.session"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except Exception as e:
                logger.warning(f"无法删除会话文件 {session_file}: {e}")
        
        # 清理用户客户端缓存
        if UC.get(user_id, None):
            del UC[user_id]
            
    except Exception as e:
        logger.error(f'登出命令中发生错误: {str(e)}')
        
        # 即使出错也尝试清理
        try:
            await remove_user_session(user_id)
        except Exception as cleanup_error:
            logger.warning(f"清理用户会话时出错: {cleanup_error}")
        
        if UC.get(user_id, None):
            del UC[user_id]
        
        await edit_message_safely(status_msg,
            f'❌ 登出过程中发生错误：{str(e)}')
        
        # 清理会话文件
        session_file = f"{user_id}_client.session"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except Exception as e:
                logger.warning(f"无法删除会话文件 {session_file}: {e}")

async def run_login_plugin():
    """运行登录插件"""
    logger.info("登录插件已加载")
