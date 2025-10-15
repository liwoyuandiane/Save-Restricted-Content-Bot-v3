# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

from shared_client import app
from pyrogram import filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_GROUP, OWNER_ID, FORCE_SUB

async def subscribe(app, message):
    # 仅当 FORCE_SUB 为有效的频道ID时才进行强制订阅检查
    if isinstance(FORCE_SUB, int) and FORCE_SUB > 0:
        try:
            user = await app.get_chat_member(FORCE_SUB, message.from_user.id)
            if str(user.status) == "ChatMemberStatus.BANNED":
                await message.reply_text("你已被禁止使用，请联系管理员")
                return 1
        except UserNotParticipant:
            try:
                link = await app.export_chat_invite_link(FORCE_SUB)
            except Exception:
                # 退化到给出固定提示，不暴露具体异常
                await message.reply_text("请先加入指定频道后再使用本机器人。")
                return 1
            caption = "请先加入频道后再使用本机器人"
            await message.reply_photo(
                photo="https://graph.org/file/d44f024a08ded19452152.jpg",
                caption=caption,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("立即加入", url=f"{link}")]])
            )
            return 1
        except Exception:
            # 不把底层异常直接展示给用户，避免出现 Peer id invalid 等原始信息
            await message.reply_text("处理请求时发生异常，请稍后重试或联系管理员。")
            return 1
    # 未配置 FORCE_SUB 时直接放行
    return 0
     
@app.on_message(filters.command("set"))
async def set(_, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("你没有权限使用此命令。")
        return
     
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
 
    await message.reply("✅ 指令已成功配置！")
 
 
 
 
help_pages = [
    (
        "📝 **指令总览 (1/2)**:\n\n"
        "1. **/add userID**\n"
        "> 将用户加入高级会员（仅限所有者）\n\n"
        "2. **/rem userID**\n"
        "> 从高级会员移除用户（仅限所有者）\n\n"
        "3. **/transfer userID**\n"
        "> 向他人转赠高级会员（仅限高级会员/分销）\n\n"
        "4. **/get**\n"
        "> 获取所有用户ID（仅限所有者）\n\n"
        "5. **/lock**\n"
        "> 锁定频道，禁止被提取（仅限所有者）\n\n"
        "6. **/dl link**\n"
        "> 下载视频（v3 默认可能不可用）\n\n"
        "7. **/adl link**\n"
        "> 下载音频（v3 默认可能不可用）\n\n"
        "8. **/login**\n"
        "> 登录以访问私有频道/群\n\n"
        "9. **/batch**\n"
        "> 批量提取帖子（登录后可用）\n\n"
    ),
    (
        "📝 **指令总览 (2/2)**:\n\n"
        "10. **/logout**\n"
        "> 退出登录\n\n"
        "11. **/stats**\n"
        "> 查看机器人统计\n\n"
        "12. **/plan**\n"
        "> 查看套餐与价格\n\n"
        "13. **/speedtest**\n"
        "> 测试服务器速度（v3 不提供）\n\n"
        "14. **/terms**\n"
        "> 使用条款\n\n"
        "15. **/cancel**\n"
        "> 取消当前批量任务\n\n"
        "16. **/myplan**\n"
        "> 查看你的套餐详情\n\n"
        "17. **/session**\n"
        "> 生成 Pyrogram V2 会话\n\n"
        "18. **/settings**\n"
        "> 1. SETCHATID：直接上传到某个聊天（-100开头ID）\n"
        "> 2. SETRENAME：设置重命名标签/频道署名\n"
        "> 3. CAPTION：设置自定义说明文字\n"
        "> 4. REPLACEWORDS：按规则替换/删除文字\n"
        "> 5. RESET：恢复默认设置\n\n"
        "> 你还可以在设置里配置自定义封面、PDF/视频水印、会话登录等功能\n\n"
        "**__由 Team SPY 驱动__**"
    )
]
 
 
async def send_or_edit_help_page(_, message, page_number):
    if page_number < 0 or page_number >= len(help_pages):
        return
 
     
    prev_button = InlineKeyboardButton("◀️ 上一页", callback_data=f"help_prev_{page_number}")
    next_button = InlineKeyboardButton("下一页 ▶️", callback_data=f"help_next_{page_number}")
 
     
    buttons = []
    if page_number > 0:
        buttons.append(prev_button)
    if page_number < len(help_pages) - 1:
        buttons.append(next_button)
 
     
    keyboard = InlineKeyboardMarkup([buttons])
 
     
    await message.delete()
 
     
    await message.reply(
        help_pages[page_number],
        reply_markup=keyboard
    )
 
 
@app.on_message(filters.command("help"))
async def help(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
     
    await send_or_edit_help_page(client, message, 0)
 
 
@app.on_callback_query(filters.regex(r"help_(prev|next)_(\d+)"))
async def on_help_navigation(client, callback_query):
    action, page_number = callback_query.data.split("_")[1], int(callback_query.data.split("_")[2])
 
    if action == "prev":
        page_number -= 1
    elif action == "next":
        page_number += 1

    await send_or_edit_help_page(client, callback_query.message, page_number)
     
    await callback_query.answer()

 
@app.on_message(filters.command("terms") & filters.private)
async def terms(client, message):
    terms_text = (
        "> 📜 **使用条款** 📜\n\n"
        "✨ 我们不对用户的任何行为负责，亦不鼓励或宣传侵犯版权的内容。若用户自行进行相关操作，责任自负。\n"
        "✨ 购买后不保证服务持续可用或套餐时效。__是否授予/取消权限由我们自行决定，我们保留随时封禁或放行的权利。__\n"
        "✨ 付款**__并不保证__**获得 /batch 指令的使用权限，一切以我们最终决定为准。\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📋 查看套餐", callback_data="see_plan")],
            [InlineKeyboardButton("💬 立即联系", url="https://t.me/kingofpatal")],
        ]
    )
    await message.reply_text(terms_text, reply_markup=buttons)
 
 
@app.on_message(filters.command("plan") & filters.private)
async def plan(client, message):
    plan_text = (
        "> 💰 **高级会员价格**：\n\n 起价 $2 或 200 INR，接受 **__亚马逊礼品卡__**（具体以条款为准）。\n"
        "📥 **下载上限**：单次批量指令最多可下载 100,000 条文件。\n"
        "🛑 **批量模式**：提供 /bulk 与 /batch 两种模式。\n"
        "   - 建议在当前任务自动结束/取消后再进行新的下载或上传。\n\n"
        "📜 **使用条款**：更多细节请发送 /terms 查看。\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📜 查看条款", callback_data="see_terms")],
            [InlineKeyboardButton("💬 立即联系", url="https://t.me/kingofpatal")],
        ]
    )
    await message.reply_text(plan_text, reply_markup=buttons)
 
 
@app.on_callback_query(filters.regex("see_plan"))
async def see_plan(client, callback_query):
    plan_text = (
        "> 💰**高级会员价格**\n\n 起价 $2 或 200 INR，接受 **__亚马逊礼品卡__**（以条款为准）。\n"
        "📥 **下载上限**：单次批量最多 100,000 条。\n"
        "🛑 **批量模式**：提供 /bulk 与 /batch。\n"
        "   - 建议等待当前流程自动取消后再继续其他下载/上传。\n\n"
        "📜 **使用条款**：详情请发送 /terms 或点击下方“查看条款”👇\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📜 查看条款", callback_data="see_terms")],
            [InlineKeyboardButton("💬 立即联系", url="https://t.me/kingofpatal")],
        ]
    )
    await callback_query.message.edit_text(plan_text, reply_markup=buttons)
 
 
@app.on_callback_query(filters.regex("see_terms"))
async def see_terms(client, callback_query):
    terms_text = (
        "> 📜 **使用条款** 📜\n\n"
        "✨ 我们不对用户的任何行为负责，亦不鼓励或宣传侵犯版权的内容。若用户自行进行相关操作，责任自负。\n"
        "✨ 购买后不保证服务持续可用或套餐时效。__是否授予/取消权限由我们自行决定，我们保留随时封禁或放行的权利。__\n"
        "✨ 付款**__并不保证__**获得 /batch 指令的使用权限，一切以我们最终决定为准。\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📋 查看套餐", callback_data="see_plan")],
            [InlineKeyboardButton("💬 立即联系", url="https://t.me/kingofpatal")],
        ]
    )
    await callback_query.message.edit_text(terms_text, reply_markup=buttons)
 
 
