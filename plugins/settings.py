# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

from telethon import events, Button
import re
import os
import asyncio
import string
import random
from shared_client import client as gf
from config import OWNER_ID
from utils.func import get_user_data_key, save_user_data, users_collection

VIDEO_EXTENSIONS = {
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm',
    'mpeg', 'mpg', '3gp'
}
SET_PIC = 'settings.jpg'
MESS = '自定义你的文件处理设置…'

active_conversations = {}

@gf.on(events.NewMessage(incoming=True, pattern='/settings'))
async def settings_command(event):
    user_id = event.sender_id
    await send_settings_message(event.chat_id, user_id)

async def send_settings_message(chat_id, user_id):
    buttons = [
        [
            Button.inline('📝 设置聊天ID', b'setchat'),
            Button.inline('🏷️ 设置重命名标签', b'setrename')
        ],
        [
            Button.inline('📋 设置说明文字', b'setcaption'),
            Button.inline('🔄 替换文字', b'setreplacement')
        ],
        [
            Button.inline('🗑️ 删除文字', b'delete'),
            Button.inline('🔄 重置设置', b'reset')
        ],
        [
            Button.inline('🔑 会话登录', b'addsession'),
            Button.inline('🚪 登出', b'logout')
        ],
        [
            Button.inline('🖼️ 设置缩略图', b'setthumb'),
            Button.inline('❌ 移除缩略图', b'remthumb')
        ],
        [
            Button.url('🆘 反馈问题', 'https://t.me/team_spy_pro')
        ]
    ]
    await gf.send_message(chat_id, MESS, buttons=buttons)

@gf.on(events.CallbackQuery)
async def callback_query_handler(event):
    user_id = event.sender_id
    
    callback_actions = {
        b'setchat': {
            'type': 'setchat',
            'message': """请发送目标聊天的ID（以 -100 开头）：
__👉 提示：如果你使用的是“子机器人”上传，则子机器人必须在该聊天中具备管理员权限；否则需要当前本机器人具备管理员权限。__
👉 如果要上传到“话题群”的指定话题，请按 **-100频道ID/话题ID** 的格式设置，例如：**-1004783898/12**"""
        },
        b'setrename': {
            'type': 'setrename',
            'message': '发送重命名标签（会追加在文件名后）：'
        },
        b'setcaption': {
            'type': 'setcaption',
            'message': '发送自定义说明文字（caption）：'
        },
        b'setreplacement': {
            'type': 'setreplacement',
            'message': "请按格式发送替换规则：'原词' '替换为'"
        },
        b'addsession': {
            'type': 'addsession',
            'message': '发送你的 Pyrogram V2 会话字符串（用于4GB上传等）：'
        },
        b'delete': {
            'type': 'deleteword',
            'message': '发送要删除的词（空格分隔），将从说明文字/文件名中移除…'
        },
        b'setthumb': {
            'type': 'setthumb',
            'message': '请发送要设置为自定义缩略图的图片。'
        }
    }
    
    if event.data in callback_actions:
        action = callback_actions[event.data]
        await start_conversation(event, user_id, action['type'], action['message'])
    elif event.data == b'logout':
        result = await users_collection.update_one(
            {'user_id': user_id},
            {'$unset': {'session_string': ''}}
        )
        if result.modified_count > 0:
            await event.respond('✅ 已登出并删除会话。')
        else:
            await event.respond('当前未登录。')
    elif event.data == b'reset':
        try:
            await users_collection.update_one(
                {'user_id': user_id},
                {'$unset': {
                    'delete_words': '',
                    'replacement_words': '',
                    'rename_tag': '',
                    'caption': '',
                    'chat_id': ''
                }}
            )
            thumbnail_path = f'{user_id}.jpg'
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            await event.respond('✅ 已成功重置全部设置。如需登出，请发送 /logout')
        except Exception as e:
            await event.respond(f'重置设置出错：{e}')
    elif event.data == b'remthumb':
        try:
            os.remove(f'{user_id}.jpg')
            await event.respond('✅ 已移除缩略图！')
        except FileNotFoundError:
            await event.respond('未找到可移除的缩略图。')

async def start_conversation(event, user_id, conv_type, prompt_message):
    if user_id in active_conversations:
        await event.respond('已取消上一次对话，开始新的设置。')
    
    msg = await event.respond(f'{prompt_message}\n\n（发送 /cancel 取消本次操作）')
    active_conversations[user_id] = {'type': conv_type, 'message_id': msg.id}

@gf.on(events.NewMessage(pattern='/cancel'))
async def cancel_conversation(event):
    user_id = event.sender_id
    if user_id in active_conversations:
        await event.respond('已取消。')
        del active_conversations[user_id]

@gf.on(events.NewMessage())
async def handle_conversation_input(event):
    user_id = event.sender_id
    if user_id not in active_conversations or event.message.text.startswith('/'):
        return
        
    conv_type = active_conversations[user_id]['type']
    
    handlers = {
        'setchat': handle_setchat,
        'setrename': handle_setrename,
        'setcaption': handle_setcaption,
        'setreplacement': handle_setreplacement,
        'addsession': handle_addsession,
        'deleteword': handle_deleteword,
        'setthumb': handle_setthumb
    }
    
    if conv_type in handlers:
        await handlers[conv_type](event, user_id)
    
    if user_id in active_conversations:
        del active_conversations[user_id]

async def handle_setchat(event, user_id):
    try:
        chat_id = event.text.strip()
        await save_user_data(user_id, 'chat_id', chat_id)
        await event.respond('✅ 已成功设置聊天ID！')
    except Exception as e:
        await event.respond(f'❌ 设置聊天ID失败：{e}')

async def handle_setrename(event, user_id):
    rename_tag = event.text.strip()
    await save_user_data(user_id, 'rename_tag', rename_tag)
    await event.respond(f'✅ 重命名标签已设置为：{rename_tag}')

async def handle_setcaption(event, user_id):
    caption = event.text
    await save_user_data(user_id, 'caption', caption)
    await event.respond(f'✅ 已成功设置说明文字！')

async def handle_setreplacement(event, user_id):
    match = re.match("'(.+)' '(.+)'", event.text)
    if not match:
        await event.respond("❌ 格式无效。用法：'原词' '替换为'")
    else:
        word, replace_word = match.groups()
        delete_words = await get_user_data_key(user_id, 'delete_words', [])
        if word in delete_words:
            await event.respond(f"❌ 词语 '{word}' 已在删除列表中，无法替换。")
        else:
            replacements = await get_user_data_key(user_id, 'replacement_words', {})
            replacements[word] = replace_word
            await save_user_data(user_id, 'replacement_words', replacements)
            await event.respond(f"✅ 已保存替换规则：'{word}' 将替换为 '{replace_word}'")

async def handle_addsession(event, user_id):
    session_string = event.text.strip()
    await save_user_data(user_id, 'session_string', session_string)
    await event.respond('✅ 已添加会话字符串！')

async def handle_deleteword(event, user_id):
    words_to_delete = event.message.text.split()
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    delete_words = list(set(delete_words + words_to_delete))
    await save_user_data(user_id, 'delete_words', delete_words)
    await event.respond(f"✅ 已加入删除列表：{', '.join(words_to_delete)}")

async def handle_setthumb(event, user_id):
    if event.photo:
        temp_path = await event.download_media()
        try:
            thumb_path = f'{user_id}.jpg'
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            os.rename(temp_path, thumb_path)
            await event.respond('✅ 缩略图保存成功！')
        except Exception as e:
            await event.respond(f'❌ Error saving thumbnail: {e}')
    else:
        await event.respond('❌ 请发送一张图片，已取消操作。')

def generate_random_name(length=7):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def rename_file(file, sender, edit):
    try:
        delete_words = await get_user_data_key(sender, 'delete_words', [])
        custom_rename_tag = await get_user_data_key(sender, 'rename_tag', '')
        replacements = await get_user_data_key(sender, 'replacement_words', {})
        
        last_dot_index = str(file).rfind('.')
        if last_dot_index != -1 and last_dot_index != 0:
            ggn_ext = str(file)[last_dot_index + 1:]
            if ggn_ext.isalpha() and len(ggn_ext) <= 9:
                if ggn_ext.lower() in VIDEO_EXTENSIONS:
                    original_file_name = str(file)[:last_dot_index]
                    file_extension = 'mp4'
                else:
                    original_file_name = str(file)[:last_dot_index]
                    file_extension = ggn_ext
            else:
                original_file_name = str(file)[:last_dot_index]
                file_extension = 'mp4'
        else:
            original_file_name = str(file)
            file_extension = 'mp4'
        
        for word in delete_words:
            original_file_name = original_file_name.replace(word, '')
        
        for word, replace_word in replacements.items():
            original_file_name = original_file_name.replace(word, replace_word)
        
        new_file_name = f'{original_file_name} {custom_rename_tag}.{file_extension}'
        
        os.rename(file, new_file_name)
        return new_file_name
    except Exception as e:
        print(f"Rename error: {e}")
        return file
        
