# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os, re, time, asyncio, json, asyncio 
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant
from config import API_ID, API_HASH, LOG_GROUP, STRING, FORCE_SUB, FREEMIUM_LIMIT, PREMIUM_LIMIT
from utils.func import get_user_data, screenshot, thumbnail, get_video_metadata
from utils.func import get_user_data_key, process_text_with_rules, is_premium_user, E
from shared_client import app as X
from plugins.settings import rename_file
from plugins.start import subscribe as sub
from utils.custom_filters import login_in_progress
from utils.encrypt import dcs
from typing import Dict, Any, Optional


Y = None if not STRING else __import__('shared_client').userbot
Z, P, UB, UC, emp = {}, {}, {}, {}, {}

ACTIVE_USERS = {}
ACTIVE_USERS_FILE = "active_users.json"

# fixed directory file_name problems 
def sanitize(filename):
    return re.sub(r'[<>:"/\\|?*\']', '_', filename).strip(" .")[:255]

def load_active_users():
    try:
        if os.path.exists(ACTIVE_USERS_FILE):
            with open(ACTIVE_USERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

async def save_active_users_to_file():
    try:
        with open(ACTIVE_USERS_FILE, 'w') as f:
            json.dump(ACTIVE_USERS, f)
    except Exception as e:
        print(f"Error saving active users: {e}")

async def add_active_batch(user_id: int, batch_info: Dict[str, Any]):
    ACTIVE_USERS[str(user_id)] = batch_info
    await save_active_users_to_file()

def is_user_active(user_id: int) -> bool:
    return str(user_id) in ACTIVE_USERS

async def update_batch_progress(user_id: int, current: int, success: int):
    if str(user_id) in ACTIVE_USERS:
        ACTIVE_USERS[str(user_id)]["current"] = current
        ACTIVE_USERS[str(user_id)]["success"] = success
        await save_active_users_to_file()

async def request_batch_cancel(user_id: int):
    if str(user_id) in ACTIVE_USERS:
        ACTIVE_USERS[str(user_id)]["cancel_requested"] = True
        await save_active_users_to_file()
        return True
    return False

def should_cancel(user_id: int) -> bool:
    user_str = str(user_id)
    return user_str in ACTIVE_USERS and ACTIVE_USERS[user_str].get("cancel_requested", False)

async def remove_active_batch(user_id: int):
    if str(user_id) in ACTIVE_USERS:
        del ACTIVE_USERS[str(user_id)]
        await save_active_users_to_file()

def get_batch_info(user_id: int) -> Optional[Dict[str, Any]]:
    return ACTIVE_USERS.get(str(user_id))

ACTIVE_USERS = load_active_users()

async def upd_dlg(c):
    try:
        async for _ in c.get_dialogs(limit=100): pass
        return True
    except Exception as e:
        print(f'Failed to update dialogs: {e}')
        return False

# fixed the old group of 2021-2022 extraction 🌝 (buy krne ka fayda nhi ab old group) ✅ 
async def get_msg(c, u, i, d, lt):
    try:
        if lt == 'public':
            try:
                if str(i).lower().endswith('bot'):
                    emp[i] = False
                    xm = await u.get_messages(i, d)
                    emp[i] = getattr(xm, "empty", False)
                    if not emp[i]:
                        emp[i] = True
                        print(f"Bot chat found successfully...")
                        return xm
                    
                # 初始化 emp 字典中的键
                if i not in emp:
                    emp[i] = True
                
                if emp[i]:
                    xm = await c.get_messages(i, d)
                    print(f"fetched by {c.me.username}")
                    emp[i] = getattr(xm, "empty", False)
                    if emp[i]:
                        print(f"Not fetched by {c.me.username}")
                        try: await u.join_chat(i)
                        except: pass
                        xm = await u.get_messages((await u.get_chat(f"@{i}")).id, d)
                    
                    return xm
                else:
                    # 如果 emp[i] 为 False，直接尝试获取消息
                    xm = await c.get_messages(i, d)
                    print(f"fetched by {c.me.username} (direct)")
                    return xm                   
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                print(f'Error fetching public message from {i}: {error_type} - {error_msg}')
                print(f'Channel: {i}, Message ID: {d}, Type: {lt}')
                print(f'Full exception: {repr(e)}')
                
                # 检查是否是权限问题
                if 'CHAT_ADMIN_REQUIRED' in error_msg or 'CHAT_WRITE_FORBIDDEN' in error_msg:
                    print(f'Permission denied for channel {i}')
                elif 'CHAT_INVALID' in error_msg or 'USERNAME_NOT_OCCUPIED' in error_msg:
                    print(f'Channel {i} does not exist or is invalid')
                elif 'FLOOD_WAIT' in error_msg:
                    print(f'Rate limited for channel {i}')
                elif 'USERNAME_INVALID' in error_msg:
                    print(f'Invalid username for channel {i}')
                elif 'PEER_ID_INVALID' in error_msg:
                    print(f'Invalid peer ID for channel {i}')
                
                return None
        else:
            if u:
                try:
                    async for _ in u.get_dialogs(limit=50): pass
                    
                    # Try with -100 prefix first
                    if str(i).startswith('-100'):
                        chat_id_100 = i
                        # For - prefix, remove -100 and add just -
                        base_id = str(i)[4:]  # Remove -100
                        chat_id_dash = f"-{base_id}"
                    elif i.isdigit():
                        chat_id_100 = f"-100{i}"
                        chat_id_dash = f"-{i}"
                    else:
                        chat_id_100 = i
                        chat_id_dash = i
                    
                    # Try -100 format first
                    try:
                        result = await u.get_messages(chat_id_100, d)
                        if result and not getattr(result, "empty", False):
                            return result
                    except Exception:
                        pass
                    
                    # Try - format second
                    try:
                        result = await u.get_messages(chat_id_dash, d)
                        if result and not getattr(result, "empty", False):
                            return result
                    except Exception:
                        pass
                    
                    # Final fallback - refresh dialogs and try original
                    try:
                        async for _ in u.get_dialogs(limit=200): pass
                        result = await u.get_messages(i, d)
                        if result and not getattr(result, "empty", False):
                            return result
                    except Exception:
                        pass
                    
                    return None
                            
                except Exception as e:
                    print(f'Private channel error: {e}')
                    return None
            return None
    except Exception as e:
        print(f'Error fetching message: {e}')
        return None


async def get_ubot(uid):
    bt = await get_user_data_key(uid, "bot_token", None)
    if not bt: return None
    if uid in UB: return UB.get(uid)
    try:
        bot = Client(f"user_{uid}", bot_token=bt, api_id=API_ID, api_hash=API_HASH)
        await bot.start()
        UB[uid] = bot
        return bot
    except Exception as e:
        print(f"Error starting bot for user {uid}: {e}")
        return None

async def get_uclient(uid):
    ud = await get_user_data(uid)
    ubot = UB.get(uid)
    cl = UC.get(uid)
    if cl: return cl
    if not ud: return ubot if ubot else None
    xxx = ud.get('session_string')
    if xxx:
        try:
            ss = dcs(xxx)
            gg = Client(f'{uid}_client', api_id=API_ID, api_hash=API_HASH, device_model="v3saver", session_string=ss)
            await gg.start()
            await upd_dlg(gg)
            UC[uid] = gg
            return gg
        except Exception as e:
            print(f'User client error: {e}')
            return ubot if ubot else Y
    return Y

async def prog(c, t, C, h, m, st):
    global P
    p = c / t * 100
    interval = 10 if t >= 100 * 1024 * 1024 else 20 if t >= 50 * 1024 * 1024 else 30 if t >= 10 * 1024 * 1024 else 50
    step = int(p // interval) * interval
    if m not in P or P[m] != step or p >= 100:
        P[m] = step
        c_mb = c / (1024 * 1024)
        t_mb = t / (1024 * 1024)
        bar = '🟢' * int(p / 10) + '🔴' * (10 - int(p / 10))
        speed = c / (time.time() - st) / (1024 * 1024) if time.time() > st else 0
        eta = time.strftime('%M:%S', time.gmtime((t - c) / (speed * 1024 * 1024))) if speed > 0 else '00:00'
        await C.edit_message_text(h, m, f"__**Pyro Handler...**__\n\n{bar}\n\n⚡**__Completed__**: {c_mb:.2f} MB / {t_mb:.2f} MB\n📊 **__Done__**: {p:.2f}%\n🚀 **__Speed__**: {speed:.2f} MB/s\n⏳ **__ETA__**: {eta}\n\n**__Powered by Team SPY__**")
        if p >= 100: P.pop(m, None)

async def send_direct(c, m, tcid, ft=None, rtmid=None):
    try:
        if m.video:
            await c.send_video(tcid, m.video.file_id, caption=ft, duration=m.video.duration, width=m.video.width, height=m.video.height, reply_to_message_id=rtmid)
        elif m.video_note:
            await c.send_video_note(tcid, m.video_note.file_id, reply_to_message_id=rtmid)
        elif m.voice:
            await c.send_voice(tcid, m.voice.file_id, reply_to_message_id=rtmid)
        elif m.sticker:
            await c.send_sticker(tcid, m.sticker.file_id, reply_to_message_id=rtmid)
        elif m.audio:
            await c.send_audio(tcid, m.audio.file_id, caption=ft, duration=m.audio.duration, performer=m.audio.performer, title=m.audio.title, reply_to_message_id=rtmid)
        elif m.photo:
            photo_id = m.photo.file_id if hasattr(m.photo, 'file_id') else m.photo[-1].file_id
            await c.send_photo(tcid, photo_id, caption=ft, reply_to_message_id=rtmid)
        elif m.document:
            await c.send_document(tcid, m.document.file_id, caption=ft, file_name=m.document.file_name, reply_to_message_id=rtmid)
        else:
            return False
        return True
    except Exception as e:
        print(f'Direct send error: {e}')
        return False

async def process_msg(c, u, m, d, lt, uid, i):
    try:
        cfg_chat = await get_user_data_key(d, 'chat_id', None)
        tcid = d
        rtmid = None
        if cfg_chat:
            if '/' in cfg_chat:
                parts = cfg_chat.split('/', 1)
                tcid = int(parts[0])
                rtmid = int(parts[1]) if len(parts) > 1 else None
            else:
                tcid = int(cfg_chat)
        
        if m.media:
            orig_text = m.caption.markdown if m.caption else ''
            proc_text = await process_text_with_rules(d, orig_text)
            user_cap = await get_user_data_key(d, 'caption', '')
            ft = f'{proc_text}\n\n{user_cap}' if proc_text and user_cap else user_cap if user_cap else proc_text
            
            if lt == 'public' and not emp.get(i, False):
                await send_direct(c, m, tcid, ft, rtmid)
                return 'Sent directly.'
            
            st = time.time()
            p = await c.send_message(d, '正在下载…')

            c_name = f"{time.time()}"
            if m.video:
                file_name = m.video.file_name
                if not file_name:
                    file_name = f"{time.time()}.mp4"
                    c_name = sanitize(file_name)
            elif m.audio:
                file_name = m.audio.file_name
                if not file_name:
                    file_name = f"{time.time()}.mp3"
                    c_name = sanitize(file_name)
            elif m.document:
                file_name = m.document.file_name
                if not file_name:
                    file_name = f"{time.time()}"
                    c_name = sanitize(file_name)
            elif m.photo:
                file_name = f"{time.time()}.jpg"
                c_name = sanitize(file_name)
    
            f = await u.download_media(m, file_name=c_name, progress=prog, progress_args=(c, d, p.id, st))
            
            if not f:
                await c.edit_message_text(d, p.id, '失败。')
                return '失败。'
            
            await c.edit_message_text(d, p.id, '正在重命名…')
            if (
                (m.video and m.video.file_name) or
                (m.audio and m.audio.file_name) or
                (m.document and m.document.file_name)
            ):
                f = await rename_file(f, d, p)
            
            fsize = os.path.getsize(f) / (1024 * 1024 * 1024)
            th = thumbnail(d)
            
            if fsize > 2 and Y:
                st = time.time()
                await c.edit_message_text(d, p.id, '文件大于 2GB，切换到备用上传方式…')
                await upd_dlg(Y)
                mtd = await get_video_metadata(f)
                dur, h, w = mtd['duration'], mtd['width'], mtd['height']
                th = await screenshot(f, dur, d)
                
                send_funcs = {'video': Y.send_video, 'video_note': Y.send_video_note, 
                            'voice': Y.send_voice, 'audio': Y.send_audio, 
                            'photo': Y.send_photo, 'document': Y.send_document}
                
                for mtype, func in send_funcs.items():
                    if f.endswith('.mp4'): mtype = 'video'
                    if getattr(m, mtype, None):
                        sent = await func(LOG_GROUP, f, thumb=th if mtype == 'video' else None, 
                                        duration=dur if mtype == 'video' else None,
                                        height=h if mtype == 'video' else None,
                                        width=w if mtype == 'video' else None,
                                        caption=ft if m.caption and mtype not in ['video_note', 'voice'] else None, 
                                        reply_to_message_id=rtmid, progress=prog, progress_args=(c, d, p.id, st))
                        break
                else:
                    sent = await Y.send_document(LOG_GROUP, f, thumb=th, caption=ft if m.caption else None,
                                                reply_to_message_id=rtmid, progress=prog, progress_args=(c, d, p.id, st))
                
                await c.copy_message(d, LOG_GROUP, sent.id)
                os.remove(f)
                await c.delete_messages(d, p.id)
                
                return 'Done (Large file).'
            
            await c.edit_message_text(d, p.id, '正在上传…')
            st = time.time()

            try:
                video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv']
                audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff', '.ac3']
                file_ext = os.path.splitext(f)[1].lower()
                if m.video or (m.document and file_ext in video_extensions):
                    mtd = await get_video_metadata(f)
                    dur, h, w = mtd['duration'], mtd['width'], mtd['height']
                    th = await screenshot(f, dur, d)
                    await c.send_video(tcid, video=f, caption=ft if m.caption else None, 
                                    thumb=th, width=w, height=h, duration=dur, 
                                    progress=prog, progress_args=(c, d, p.id, st), 
                                    reply_to_message_id=rtmid)
                elif m.video_note:
                    await c.send_video_note(tcid, video_note=f, progress=prog, 
                                        progress_args=(c, d, p.id, st), reply_to_message_id=rtmid)
                elif m.voice:
                    await c.send_voice(tcid, f, progress=prog, progress_args=(c, d, p.id, st), 
                                    reply_to_message_id=rtmid)
                elif m.sticker:
                    await c.send_sticker(tcid, m.sticker.file_id, reply_to_message_id=rtmid)
                elif m.audio or (m.document and file_ext in audio_extensions):
                    await c.send_audio(tcid, audio=f, caption=ft if m.caption else None, 
                                    thumb=th, progress=prog, progress_args=(c, d, p.id, st), 
                                    reply_to_message_id=rtmid)
                elif m.photo:
                    await c.send_photo(tcid, photo=f, caption=ft if m.caption else None, 
                                    progress=prog, progress_args=(c, d, p.id, st), 
                                    reply_to_message_id=rtmid)
                elif m.document:
                    await c.send_document(tcid, document=f, caption=ft if m.caption else None, 
                                        progress=prog, progress_args=(c, d, p.id, st), 
                                        reply_to_message_id=rtmid)
                else:
                    await c.send_document(tcid, document=f, caption=ft if m.caption else None, 
                                        progress=prog, progress_args=(c, d, p.id, st), 
                                        reply_to_message_id=rtmid)
            except Exception as e:
                await c.edit_message_text(d, p.id, f'上传失败：{str(e)[:30]}')
                if os.path.exists(f): os.remove(f)
            return '失败。'
            
            os.remove(f)
            await c.delete_messages(d, p.id)
            
            return 'Done.'
            
        elif m.text:
            await c.send_message(tcid, text=m.text.markdown, reply_to_message_id=rtmid)
            return 'Sent.'
    except Exception as e:
        return f'Error: {str(e)[:50]}'
        
@X.on_message(filters.command(['batch', 'single']))
async def process_cmd(c, m):
    uid = m.from_user.id
    cmd = m.command[0]
    
    if FREEMIUM_LIMIT == 0 and not await is_premium_user(uid):
        await m.reply_text("本机器人不提供免费服务，请联系所有者购买订阅。")
        return
    
    if await sub(c, m) == 1: return
    pro = await m.reply_text('正在检查，请稍候…')
    
    if is_user_active(uid):
        await pro.edit('你已有一个进行中的任务。使用 /stop 取消后再试。')
        return
    
    ubot = await get_ubot(uid)
    if not ubot:
        await pro.edit('请先使用 /setbot 绑定你的子机器人')
        return
    
    Z[uid] = {'step': 'start' if cmd == 'batch' else 'start_single'}
    await pro.edit(f'请发送 {"起始链接…" if cmd == "batch" else "要处理的链接"}。')

@X.on_message(filters.command(['cancel', 'stop']))
async def cancel_cmd(c, m):
    uid = m.from_user.id
    if is_user_active(uid):
        if await request_batch_cancel(uid):
            await m.reply_text('已请求取消。当前下载完成后将停止本次批量任务。')
        else:
            await m.reply_text('取消请求失败，请重试。')
    else:
        await m.reply_text('没有正在进行的批量任务。')

@X.on_message(filters.text & filters.private & ~login_in_progress & ~filters.command([
    'start', 'batch', 'cancel', 'login', 'logout', 'stop', 'set', 
    'pay', 'redeem', 'gencode', 'single', 'generate', 'keyinfo', 'encrypt', 'decrypt', 'keys', 'setbot', 'rembot']))
async def text_handler(c, m):
    uid = m.from_user.id
    
    # 如果用户不在处理流程中，检查是否是直接发送的链接
    if uid not in Z:
        # 检查是否是 Telegram 链接
        if 't.me/' in m.text and ('/' in m.text.split('t.me/')[1] if 't.me/' in m.text else False):
            # 自动启动单个消息处理
            if await sub(c, m) == 1: return
            
            ubot = await get_ubot(uid)
            if not ubot:
                await m.reply("请先使用 /setbot 绑定你的子机器人")
                return
            
            if is_user_active(uid):
                await m.reply('你已有一个进行中的任务。使用 /stop 取消后再试。')
                return
            
            # 解析链接
            L = m.text
            i, d, lt = E(L)
            if not i or not d:
                await m.reply('链接格式不正确。')
                return
            
            # 开始处理
            pt = await m.reply('正在处理链接...')
            uc = await get_uclient(uid)
            if not uc:
                await pt.edit('缺少用户客户端，无法继续。')
                return
            
            try:
                msg = await get_msg(ubot, uc, i, d, lt)
                if msg:
                    res = await process_msg(ubot, uc, msg, str(m.chat.id), lt, uid, i)
                    await pt.edit(f'处理完成: {res}')
                else:
                    await pt.edit('❌ 该链接不存在或无法访问。请检查链接是否正确。')
            except Exception as e:
                error_msg = str(e)
                if 'CHAT_INVALID' in error_msg or 'USERNAME_NOT_OCCUPIED' in error_msg:
                    await pt.edit('❌ 频道不存在或链接无效。')
                elif 'CHAT_ADMIN_REQUIRED' in error_msg:
                    await pt.edit('❌ 没有权限访问该频道。')
                elif 'FLOOD_WAIT' in error_msg:
                    await pt.edit('❌ 请求过于频繁，请稍后再试。')
                else:
                    await pt.edit(f'❌ 处理失败：{error_msg[:50]}')
        return
    
    # 原有的处理流程
    s = Z[uid].get('step')
    x = await get_ubot(uid)
    if not x:
        await m.reply("请先使用 /setbot 绑定你的子机器人 `token`")
        return

    if s == 'start':
        L = m.text
        i, d, lt = E(L)
        if not i or not d:
            await m.reply_text('链接格式不正确。')
            Z.pop(uid, None)
            return
        Z[uid].update({'step': 'count', 'cid': i, 'sid': d, 'lt': lt})
        await m.reply_text('需要提取多少条消息？')

    elif s == 'start_single':
        L = m.text
        i, d, lt = E(L)
        if not i or not d:
            await m.reply_text('链接格式不正确。')
            Z.pop(uid, None)
            return

        Z[uid].update({'step': 'process_single', 'cid': i, 'sid': d, 'lt': lt})
        i, s, lt = Z[uid]['cid'], Z[uid]['sid'], Z[uid]['lt']
        pt = await m.reply_text('处理中…')
        
        ubot = UB.get(uid)
        if not ubot:
            await pt.edit('请先使用 /setbot 绑定子机器人')
            Z.pop(uid, None)
            return
        
        uc = await get_uclient(uid)
        if not uc:
            await pt.edit('缺少用户客户端，无法继续。')
            Z.pop(uid, None)
            return
            
        if is_user_active(uid):
            await pt.edit('已存在进行中的任务，请先 /stop。')
            Z.pop(uid, None)
            return

        try:
            msg = await get_msg(ubot, uc, i, s, lt)
            if msg:
                res = await process_msg(ubot, uc, msg, str(m.chat.id), lt, uid, i)
                await pt.edit(f'1/1: {res}')
            else:
                await pt.edit('❌ 该消息不存在或无法访问。')
        except Exception as e:
            error_msg = str(e)
            if 'CHAT_INVALID' in error_msg or 'USERNAME_NOT_OCCUPIED' in error_msg:
                await pt.edit('❌ 频道不存在或链接无效。')
            elif 'CHAT_ADMIN_REQUIRED' in error_msg:
                await pt.edit('❌ 没有权限访问该频道。')
            elif 'FLOOD_WAIT' in error_msg:
                await pt.edit('❌ 请求过于频繁，请稍后再试。')
            elif 'NoneType' in error_msg:
                await pt.edit('❌ 消息处理失败。')
            else:
                await pt.edit(f'❌ 处理失败：{error_msg[:50]}')
        finally:
            Z.pop(uid, None)

    elif s == 'count':
        if not m.text.isdigit():
            await m.reply_text('请输入有效的数字。')
            return
        
        count = int(m.text)
        maxlimit = PREMIUM_LIMIT if await is_premium_user(uid) else FREEMIUM_LIMIT

        if count > maxlimit:
            await m.reply_text(f'超出上限，最大可处理 {maxlimit} 条。')
            return

        Z[uid].update({'step': 'process', 'did': str(m.chat.id), 'num': count})
        i, s, n, lt = Z[uid]['cid'], Z[uid]['sid'], Z[uid]['num'], Z[uid]['lt']
        success = 0

        pt = await m.reply_text('正在批量处理…')
        uc = await get_uclient(uid)
        ubot = UB.get(uid)
        
        if not uc or not ubot:
            await pt.edit('缺少必要的客户端配置')
            Z.pop(uid, None)
            return
            
        if is_user_active(uid):
            await pt.edit('已有进行中的任务')
            Z.pop(uid, None)
            return
        
        await add_active_batch(uid, {
            "total": n,
            "current": 0,
            "success": 0,
            "cancel_requested": False,
            "progress_message_id": pt.id
            })
        
        try:
            for j in range(n):
                
                if should_cancel(uid):
                    await pt.edit(f'Cancelled at {j}/{n}. Success: {success}')
                    break
                
                await update_batch_progress(uid, j, success)
                
                mid = int(s) + j
                
                try:
                    msg = await get_msg(ubot, uc, i, mid, lt)
                    if msg:
                        res = await process_msg(ubot, uc, msg, str(m.chat.id), lt, uid, i)
                        if 'Done' in res or 'Copied' in res or 'Sent' in res:
                            success += 1
                    else:
                        try: await pt.edit(f'{j+1}/{n}: ❌ 消息不存在或无法访问')
                        except: pass
                except Exception as e:
                    error_msg = str(e)
                    if 'CHAT_INVALID' in error_msg or 'USERNAME_NOT_OCCUPIED' in error_msg:
                        try: await pt.edit(f'{j+1}/{n}: ❌ 频道不存在')
                        except: pass
                    elif 'CHAT_ADMIN_REQUIRED' in error_msg:
                        try: await pt.edit(f'{j+1}/{n}: ❌ 无权限访问')
                        except: pass
                    elif 'FLOOD_WAIT' in error_msg:
                        try: await pt.edit(f'{j+1}/{n}: ❌ 请求过于频繁')
                        except: pass
                    elif 'NoneType' in error_msg:
                        try: await pt.edit(f'{j+1}/{n}: ❌ 消息处理失败')
                        except: pass
                    else:
                        try: await pt.edit(f'{j+1}/{n}: ❌ 处理失败 - {error_msg[:20]}')
                        except: pass
                
                await asyncio.sleep(10)
            
            if j+1 == n:
                await m.reply_text(f'批量完成 ✅ 成功：{success}/{n}')
        
        finally:
            await remove_active_batch(uid)
            Z.pop(uid, None)


