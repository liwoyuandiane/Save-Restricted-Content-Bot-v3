# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

from pyrogram import filters as f
from shared_client import app
from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M, LabeledPrice as P, PreCheckoutQuery as Q
from datetime import timedelta as T
from utils.func import add_premium_user as apu
from config import P0

@app.on_message(f.command("pay") & f.private)
async def p(c, m):
    kb = M([
        [
            B(f"⭐ {P0['d']['l']} - {P0['d']['s']} 星", callback_data="p_d")
        ],
        [
            B(f"⭐ {P0['w']['l']} - {P0['w']['s']} 星", callback_data="p_w")
        ],
        [
            B(f"⭐ {P0['m']['l']} - {P0['m']['s']} 星", callback_data="p_m")
        ]
    ])
    
    txt = (
        "💎 **请选择你的高级套餐：**\n\n"
        f"📅 **{P0['d']['l']}** — {P0['d']['s']} 星\n"
        f"🗓️ **{P0['w']['l']}** — {P0['w']['s']} 星\n"
        f"📆 **{P0['m']['l']}** — {P0['m']['s']} 星\n\n"
        "从下方选择一个套餐继续 ⤵️"
    )
    await m.reply_text(txt, reply_markup=kb)
    
@app.on_callback_query(f.regex("^p_"))
async def i(c, q):
    pl = q.data.split("_")[1]
    pi = P0[pl]
    try:
        await c.send_invoice(
            chat_id=q.from_user.id,
            title=f"高级会员 {pi['l']}",
            description=f"{pi['du']} {pi['u']} 订阅",
            payload=f"{pl}_{q.from_user.id}",
            currency="XTR",
            prices=[P(label=f"高级会员 {pi['l']}", amount=pi['s'])]
        )
        await q.answer("已发送账单 💫")
    except Exception as e:
        await q.answer(f"错误：{e}", show_alert=True)

@app.on_pre_checkout_query()
async def pc(c, q: Q): 
    await q.answer(ok=True)

@app.on_message(f.successful_payment)
async def sp(c, m):
    p = m.successful_payment
    u = m.from_user.id
    pl = p.invoice_payload.split("_")[0]
    pi = P0[pl]
    ok, r = await apu(u, pi['du'], pi['u'])
    if ok:
        e = r + T(hours=5, minutes=30)
        d = e.strftime('%d-%b-%Y %I:%M:%S %p')
        await m.reply_text(
            f"✅ **支付成功！**\n\n"
            f"💎 高级会员 {pi['l']} 已激活！\n"
            f"⭐ 支付：{p.total_amount}\n"
            f"⏰ 有效期至：{d} IST\n"
            f"🔖 交易号：`{p.telegram_payment_charge_id}`"
        )
        for o in OWNER_ID:
            await c.send_message(f"用户 {u} 刚刚购买了高级会员，交易号：{p.telegram_payment_charge_id}。")
    else:
        await m.reply_text(
            f"⚠️ 已支付但开通失败。\n交易号 `{p.telegram_payment_charge_id}`"
        )
        for o in OWNER_ID:
            await c.send_message(o,
                f"⚠️ 异常！\n用户 {u}\n套餐 {pi['l']}\n交易号 {p.telegram_payment_charge_id}\n错误 {r}"
            )


