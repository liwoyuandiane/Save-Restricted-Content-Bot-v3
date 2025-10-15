# Copyright (c) 2025 Gagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

from shared_client import client as bot_client, app
from telethon import events
from datetime import timedelta
from config import OWNER_ID
from utils.func import add_premium_user, is_private_chat
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton as IK, InlineKeyboardMarkup as IKM
from config import OWNER_ID, JOIN_LINK as JL , ADMIN_CONTACT as AC
import base64 as spy
from utils.func import a1, a2, a3, a4, a5, a7, a8, a9, a10, a11
from plugins.start import subscribe


@bot_client.on(events.NewMessage(pattern='/add'))
async def add_premium_handler(event):
    if not await is_private_chat(event):
        await event.respond(
            'This command can only be used in private chats for security reasons.'
            )
        return
    """Handle /add command to add premium users (owner only)"""
    user_id = event.sender_id
    if user_id not in OWNER_ID:
        await event.respond('This command is restricted to the bot owner.')
        return
    text = event.message.text.strip()
    parts = text.split(' ')
    if len(parts) != 4:
        await event.respond(
            """Invalid format. Use: /add user_id duration_value duration_unit
Example: /add 123456 1 week"""
            )
        return
    try:
        target_user_id = int(parts[1])
        duration_value = int(parts[2])
        duration_unit = parts[3].lower()
        valid_units = ['min', 'hours', 'days', 'weeks', 'month', 'year',
            'decades']
        if duration_unit not in valid_units:
            await event.respond(
                f"Invalid duration unit. Choose from: {', '.join(valid_units)}"
                )
            return
        success, result = await add_premium_user(target_user_id,
            duration_value, duration_unit)
        if success:
            expiry_utc = result
            expiry_ist = expiry_utc + timedelta(hours=5, minutes=30)
            formatted_expiry = expiry_ist.strftime('%d-%b-%Y %I:%M:%S %p')
            await event.respond(
                f"""✅ User {target_user_id} added as premium member
Subscription valid until: {formatted_expiry} (IST)"""
                )
            await bot_client.send_message(target_user_id,
                f"""✅ Your have been added as premium member
**Validity upto**: {formatted_expiry} (IST)"""
                )
        else:
            await event.respond(f'❌ Failed to add premium user: {result}')
    except ValueError:
        await event.respond(
            'Invalid user ID or duration value. Both must be integers.')
    except Exception as e:
        await event.respond(f'Error: {str(e)}')
        
        
attr1 = spy.b64encode("photo".encode()).decode()
attr2 = spy.b64encode("file_id".encode()).decode()

@app.on_message(filters.command(spy.b64decode(a5.encode()).decode()))
async def start_handler(client, message):
    subscription_status = await subscribe(client, message)
    if subscription_status == 1:
        return

    b1 = spy.b64decode(a1).decode()
    b2 = int(spy.b64decode(a2).decode())
    b3 = spy.b64decode(a3).decode()
    b4 = spy.b64decode(a4).decode()
    b6 = (
        "Hi 👋 欢迎！需要简单介绍吗？\n\n"
        "✅ 我可以保存频道或群里禁止转发的消息；也支持从 YT、INSTA 等站点下载视频/音频。\n"
        "✅ 公共频道：直接发送帖子链接即可。私有频道：先发送 /login 登录。\n"
        "✅ 发送 /help 查看使用说明与所有命令。"
    )
    b7 = "加入频道"
    b8 = "获取高级会员"
    b9 = spy.b64decode(a10).decode()
    b10 = spy.b64decode(a11).decode()

    tm = await getattr(app, b3)(b1, b2)

    pb = getattr(tm, spy.b64decode(attr1.encode()).decode())
    fd = getattr(pb, spy.b64decode(attr2.encode()).decode())

    kb = IKM([
        [IK(b7, url=JL)],
        [IK(b8, url=AC)]
    ])

    await getattr(message, b4)(
        fd,
        caption=b6,
        reply_markup=kb
    )

    # 同步设置中文命令菜单，确保在 /start 后显示
    try:
        from pyrogram.types import BotCommand
        await app.set_bot_commands([
            BotCommand("start", "🚀 启动机器人"),
            BotCommand("batch", "🫠 批量提取"),
            BotCommand("login", "🔑 登录用于私有频道"),
            BotCommand("setbot", "🧸 绑定你的子机器人"),
            BotCommand("logout", "🚪 登出并清除会话"),
            BotCommand("adl", "👻 下载音频（支持多站点）"),
            BotCommand("dl", "💀 下载视频（支持多站点）"),
            BotCommand("status", "⟳ 刷新支付状态"),
            BotCommand("transfer", "💘 转赠高级会员"),
            BotCommand("add", "➕ 添加高级会员"),
            BotCommand("rem", "➖ 移除高级会员"),
            BotCommand("rembot", "🤨 移除自定义子机器人"),
            BotCommand("settings", "⚙️ 个性化设置"),
            BotCommand("plan", "🗓️ 查看套餐与价格"),
            BotCommand("terms", "🥺 使用条款"),
            BotCommand("help", "❓ 帮助与指令说明"),
            BotCommand("cancel", "🚫 取消登录/批量/设置流程"),
            BotCommand("stop", "🚫 终止批量任务")
        ])
    except Exception:
        pass