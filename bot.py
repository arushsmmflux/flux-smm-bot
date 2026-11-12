import os
import io
import sqlite3
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters,
)
import qrcode

# ==========================================
# CONFIGURATION SECTION (Fully Editable)
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "123456789").split(",") if x.strip().isdigit()]

UPI_ID = os.getenv("UPI_ID", "haaland78@axl")
PAYEE_NAME = os.getenv("PAYEE_NAME", "premium")

PROOF_URL = "https://t.me/fluxproofs"
SUPPORT_URL = "https://t.me/fluxsupport"

START_IMAGE_URL = "https://i.ibb.co/5X0hc5dd/logo.png"
START_CAPTION = (
    "✨ <b>𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝙎𝙊𝘾𝙄𝘼𝙇 𝙁𝙇𝙐𝙓 𝘽𝙊𝙏</b> ✨\n\n"
    "❤️ Please verify your age to enter securely.\n"
    "🔥 Tap below to continue."
)

WELCOME_IMAGE_URL = "https://ibb.co/RGL77cpn"
WELCOME_CAPTION = (
   "<b> 𝙃𝙀𝙔 👋🏻, 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙤𝙪𝙧 𝙫𝙞𝙥 𝙗𝙤𝙩  😍</b> \n\n"
"𝙏𝙃𝙄𝙎 𝘽𝙊𝙏 𝘾𝙊𝙉𝘼𝙏𝘼𝙄𝙉 𝙁𝙊𝙇𝙇𝙊𝙒𝙄𝙉𝙂 𝙋𝙇𝘼𝙉𝙎 ✅\n" 
"𝙎𝙏𝘼𝙍𝙏𝙄𝙉𝙂 𝙋𝙍𝙄𝘾𝙀 𝙄𝙎 𝙅𝙐𝙎𝙏 ₹39 ‼️\n\n"
"| 🔥𝘾𝙃𝙄!𝙇𝘿 𝙑𝙄𝘿𝙀𝙊𝙎 ( 𝘾𝙋 ) ( 𝘾𝙃𝙊𝙏𝙀 𝘽𝘼𝘾𝘾𝙃𝙀 ) \n" 
"| 🔥𝘽𝙃𝘼𝘽𝙃𝙄 𝙑𝙄𝘿𝙀0𝙎 \n" 
"| 🔥𝙈0𝙈 𝘼𝙉𝘿 𝙎𝙊#𝙉 \n" 
"| 🔥𝙍!@𝙋𝙀 𝙑𝙄𝘿𝙀0𝙎\n" 
"| 🔥𝘽𝘼#𝙋 𝘽𝙀𝙏𝙄 \n" 
"| 🔥𝗜𝗡𝗦𝗧𝗚𝗥𝗔𝗠 𝗠𝗠#𝗦 𝗔𝗟𝗟 \n"  
"| 🔥𝙂𝙄𝙍𝙇𝙎 𝙒𝙄𝙏𝙃 𝘼𝙉𝙄𝙈!𝘼𝙇 \n" 
"| 🔥 𝙈𝙄𝙓 𝙂𝙍𝙊𝙐𝙋 70𝙆 𝙑𝙄𝘿𝙀𝙊 \n" 
"| 🔥𝘽𝙃𝘼𝙄 𝘽𝙀𝙃𝘼𝙉 \n" 
"| 🔥𝗔𝗟𝗟 𝗩𝗜𝗣  𝗠𝗘𝗚𝗔 𝗣𝗔𝗖𝗞 \n\n"
"𝘽𝙀𝙉𝙄𝙁𝙄𝙏𝙎 𝙊𝙁 𝙊𝙐𝙍 𝘽𝙊𝙏 ✅ \n" 
"1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙑𝙄𝘿𝙀𝙊𝙎 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅ \n" 
"2. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝘿𝙊𝙒𝙉𝙇𝙊𝘼𝘿 𝙁𝙍𝙀𝙀 ✅ \n" 
"3. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ✅ \n" 
"4. 𝘿𝙄𝙍𝙀𝘾𝙏 𝙒𝘼𝙏𝘾𝙃 𝙑𝙄𝘿𝙀𝙊𝙎 ✅ \n" 
"<b>𝙏𝙊 𝘽𝙐𝙔 𝙋𝙇𝘼𝙉𝙎 𝘾𝙃𝙀𝘾𝙇 𝘽𝙐𝙏𝙏𝙊𝙉𝙎 𝘽𝙀𝙇𝙊𝙒 𝘼𝙉𝘿 𝘾𝙃𝙀𝘾𝙆 𝘿𝙀𝙈𝙊 𝘼𝙇𝙎𝙊</b> 😍🔥"
)

SHARED_CAPTION_TEMPLATE = (
    "📦 <b>𝙋𝙡𝙖𝙣:</b> {plan_name}\n"
    "🎬 <b>𝙑𝙞𝙙𝙚𝙤𝙨:</b> {number_of_videos}\n"
    "💰 <b>𝙋𝙧𝙞𝙘𝙚:</b> ₹{price}\n\n"
    "⏳ <b>𝙑𝙖𝙡𝙞𝙙𝙞𝙩𝙮:</b> {validity}\n"
    "⚡ <b>𝘼𝙘𝙘𝙚𝙨𝙨 𝙏𝙞𝙢𝙚:</b> Instant Delivery ✅\n\n"
    "<b>𝘿𝙚𝙨𝙘𝙧𝙞𝙥𝙩𝙞𝙤𝙣:</b>\n{description}"
)

# Configurable VC & Contact Placeholders
VC_WHATSAPP_NUMBER = os.getenv("VC_WHATSAPP_NUMBER", "919876543210")
VC_TELEGRAM_USERNAME = os.getenv("VC_TELEGRAM_USERNAME", "your_telegram_username")

# ==========================================
# PLANS CONFIGURATION (14 Temporary Plan Templates)
# ==========================================
# Ten Plans Configuration with Updated Data
PLAN = {
    "plan_1": {
        "id": "plan_1",
        "name": " 𝗜𝗡𝗦𝗧𝗚𝗥𝗔𝗠 𝗠𝗠𝗦 𝗔𝗟𝗟 😍🔥",
        "number_of_videos": "50000+",
        "price": 50,
        "validity": "180 days",
        "image_url": "https://ibb.co/Fb6S1mYg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4",
            "https://videotourl.com/videos/1791607674607-203922d8-e261-4085-90fc-4be2fd62a6fb.mp4",
            "https://videotourl.com/videos/1791607662133-116f8c11-861a-4d4c-94a4-411fbd79a4f4.mp4",
            "https://videotourl.com/videos/1791607553470-a87b7709-29e5-449b-89d2-49ce97c8e367.mp4",
            "https://videotourl.com/videos/1791607607288-b1cc3341-7d49-473e-8544-840992806dab.mp4",
            "https://videotourl.com/videos/1791607617748-9c8da0dd-313e-4a4d-862b-7ccf034383b7.mp4"
        ]
    },
    "plan_2": {
        "id": "plan_2",
        "name": "𝙈𝙊𝙈 𝘼𝙉𝘿 𝙎𝙊𝙉 😍🔥",
        "number_of_videos": "45000+",
        "price": 50,
        "validity": "180 days",
        "image_url": "https://ibb.co/ZRqKVvRQ",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791609530271-d1845e11-78bd-4465-a0e3-3e0dd57fb424.mp4",
            "https://videotourl.com/videos/1791610410648-c50ab2d2-b1b2-4998-8f5f-43a5f719b603.mp4",
            "https://videotourl.com/videos/1791609652325-1646ca32-e73f-4a5a-9874-a0f4e401c6bb.mp4",
            "https://videotourl.com/videos/1791609624603-358124e2-dbc4-43b2-9772-e18c1df57397.mp4",
            "https://videotourl.com/videos/1791609569957-a7ce2e8a-e185-4dc6-893c-298a2d9c1b4c.mp4"
        ]
    },
    "plan_3": {
        "id": "plan_3",
        "name": "𝘾𝙃𝙄!𝙇𝘿 𝙑𝙄𝘿!𝙀𝙊 ( 𝘾.𝙋) 🔥👀",
        "number_of_videos": "70000+",
        "price": 50,
        "validity": "180 days",
        "image_url": "https://ibb.co/21H7BGM2",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791598226633-9d219b40-bf0b-4774-b493-6449c47d5ef1.mp4",
            "https://videotourl.com/videos/1791598035486-79178a34-a631-49d2-870e-ff3425f1c058.mp4",
            "https://videotourl.com/videos/1791611314862-1e0e5b81-0a04-436a-9749-4f5e9115404f.mp4",
            "https://videotourl.com/videos/1791598059935-f6722923-e315-4b97-aaeb-e7b0af379f2b.mp4",
            "https://videotourl.com/videos/1791598126801-a117ace0-e399-46e6-b697-0d3da6efeedd.mp4",
            "https://videotourl.com/videos/1791598104865-7bca6c3f-db24-465d-9688-d153131af1e5.mp4",
            "https://videotourl.com/videos/1791598207010-15f8101c-d87e-4e83-bd6a-43a333204662.mp4"
        ]
    },
    "plan_4": {
        "id": "plan_4",
        "name": "𝙍!@𝙋𝙀 𝙑𝙄𝘿𝙀𝙊𝙎 💦👀",
        "number_of_videos": "40000+",
        "price": 70,
        "validity": "180 days",
        "image_url": "https://ibb.co/QF2v05qK",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791598317965-12b2368c-6035-4e43-b708-df28bcd246b6.mp4",
            "https://videotourl.com/videos/1791609986226-0b727823-bf05-42b7-80e8-c949f04b95ab.mp4",
            "https://videotourl.com/videos/1791598333066-6d6fc74f-945c-4641-99d1-d862e59790d4.mp4",
            "https://videotourl.com/videos/1791598348006-882fbe39-db59-4bb7-8636-1c2645fb93c0.mp4",
            "https://videotourl.com/videos/1791611260635-789f7a13-25cd-4204-8ffc-455168319040.mp4",
            "https://videotourl.com/videos/1791598360862-d0ddd962-c4e7-4c98-a860-d360bf6779f8.mp4",
            "https://videotourl.com/videos/1791601968259-cb7b49a5-a8c5-45f9-9156-e08f71b052d0.mp4",
            "https://videotourl.com/videos/1791598382840-4245fa8e-38f8-4737-8bb9-a2b8641a3d0f.mp4",
            "https://videotourl.com/videos/1791598397313-ff9dd5ef-d489-4715-a2ca-a71c8923f162.mp4"
        ]
    },
    "plan_5": {
        "id": "plan_5",
        "name": "𝘽𝘼𝘼𝙋 𝘽𝙀𝙏𝙄 🔥💦",
        "number_of_videos": "30000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://ibb.co/5X0hc5dd",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791609855846-9b6bac98-1fcf-4d60-b612-3e5abaf6be7e.mp4",
            "https://videotourl.com/videos/1791614058029-1220e2df-44c4-467d-bbd7-755af32ada0c.mp4"
        ]
    },
    "plan_6": {
        "id": "plan_6",
        "name": "𝘽𝙃𝘼𝘽𝙃𝙄 𝙑𝙄𝘿𝙀𝙊𝙎  💦👅",
        "number_of_videos": "56000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://ibb.co/N6wzXDHw",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791611037316-4db456f2-f82c-4468-9f48-381341ed6e55.mp4",
            "https://videotourl.com/videos/1791611085614-c863517b-d989-4d6f-b6ef-d23db0b73f5a.mp4",
            "https://videotourl.com/videos/1791611220352-ba6538bc-4db1-401e-81f7-88c53824e27f.mp4",
            "https://videotourl.com/videos/1791609479203-02acf86c-6132-4bc2-8041-9f43ab529748.mp4",
            "https://videotourl.com/videos/1791611168222-86d679dd-8a24-46fb-8b06-d59cc97e84c2.mp4",
            "https://videotourl.com/videos/1791611005214-c25159ac-d514-4eff-8061-a25465ff6eba.mp4"
        ]
    },
    "plan_7": {
        "id": "plan_7",
        "name": "𝘽𝙃𝘼𝙄 𝘽𝙀𝙃𝘼𝙉 🔥🥵 ",
        "number_of_videos": "67000+",
        "price": 45,
        "validity": "180 days",
        "image_url": "https://ibb.co/9kKCd6ZF",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791611423923-36dbbbf3-84c1-4754-a7e4-dc05798eaa03.mp4",
            "https://videotourl.com/videos/1791611350514-052fe889-5ac7-4446-91ef-2f928070e131.mp4",
            "https://videotourl.com/videos/1791609591492-b5b0f616-27c5-436f-9aa9-e70720337677.mp4",
            "https://videotourl.com/videos/1791609952353-7ee9382f-6db6-4c43-86ed-c8f418a3282c.mp4",
            "https://videotourl.com/videos/1791609450717-98fd3d4d-533c-46fc-a290-9f9f937b6721.mp4"
        ]
    },
    "plan_8": {
        "id": "plan_8",
        "name": "𝙂𝙄𝙍𝙇𝙎 𝙒𝙄𝙏𝙃 𝘼𝙉!𝙈@𝙇🔥",
        "number_of_videos": "18000+",
        "price": 45,
        "validity": "180 days",
        "image_url": "https://ibb.co/WNP6gCzD",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demo_videos": [
            "https://videotourl.com/videos/1791611713436-2f106a4b-9ee1-4d9b-8e06-c30a0fe309e7.mp4",
            "https://videotourl.com/videos/1791611779829-f05b75a9-65c7-441d-ad89-5d5f15301b01.mp4"
        ]
    },
    "plan_9": {
        "id": "plan_9",
        "name": "𝙈𝙄𝙓 𝙂𝙍𝙊𝙐𝙋 1LAKH 𝙑𝙄𝘿𝙀𝙊𝙎 🥵  ",
        "number_of_videos": "100000+",
        "price": 70,
        "validity": "180 days",
        "image_url": "https://ibb.co/zVvdkf09",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙁𝙍𝙄𝘿𝘼𝙔 ✅.",
        "demo_videos": [
            "https://videotourl.com/videos/1791611593469-187437c5-8f84-41c6-afa1-3d61feb9ff72.mp4",
            "https://videotourl.com/videos/1791611552865-c2cf6f7d-1544-4c34-9bdb-5e5fb2092584.mp4"
        ]
    },
  "plan_10": {
    "id": "plan_10",
    "name": "𝗔𝗟𝗟 𝗩𝗜𝗣  𝗠𝗘𝗚𝗔 𝗣𝗔𝗖𝗞 🔥",
    "number_of_videos": "10000+",
    "price": 200,
    "validity": "180 days",
    "image_url": "https://ibb.co/84598K8j",
    "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙢𝙎 😍",
    "demos": [
        "https://ibb.co/F49kN3Td"
    ]
 },
    "plan_1": {
        "id": "plan_11",
        "name": "Ultimate Masterclass Pack 1",
        "number_of_videos": "5000+",
        "price": 49,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ]
    },
    # 2. Normal Plan 2
    "plan_2": {
        "id": "plan_12",
        "name": "Exclusive Video Bundle 2",
        "number_of_videos": "4000+",
        "price": 59,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/ZRqKVvRQ/course2.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": [
            "https://videotourl.com/videos/1791609530271-d1845e11-78bd-4465-a0e3-3e0dd57fb424.mp4"
        ]
    },
    # 3. Normal Plan 3
    "plan_3": {
        "id": "plan_13",
        "name": "Premium Creator Pack 3",
        "number_of_videos": "7000+",
        "price": 79,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/21H7BGM2/course3.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demo_videos": [
            "https://videotourl.com/videos/1791598226633-9d219b40-bf0b-4774-b493-6449c47d5ef1.mp4"
        ]
    },
    # 4. Normal Plan 4
    "plan_4": {
        "id": "plan_14",
        "name": "Pro Video Collection 4",
        "number_of_videos": "3500+",
        "price": 99,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ]
    },
    # 5. Normal Plan 5
    "plan_5": {
        "id": "plan_15",
        "name": "Elite Creator Pack 5",
        "number_of_videos": "6000+",
        "price": 149,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ]
    },
    # 6. Normal Plan 6
    "plan_6": {
        "id": "plan_16",
        "name": "Advanced Masterclass 6",
        "number_of_videos": "8000+",
        "price": 179,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ]
    },
    # 7. Normal Plan 7
    "plan_7": {
        "id": "plan_17",
        "name": "Super Creator Pack 7",
        "number_of_videos": "9000+",
        "price": 199,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ]
    },
    # 8. Special Plan: ₹23 Multi-Pack Selection Plan
    "plan_multi_pack": {
        "id": "plan_multi_pack",
        "name": "✨ Multi-Pack Custom Bundle (₹23 Pack)",
        "number_of_videos": "Custom Selection (4 Packs)",
        "price": 120,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "Select exactly 4 packs from our list to build your custom bundle for ₹120!"
    },
    # 9. Special Plan: ₹20 Direct-Demo Plan
    "plan_direct_demo": {
        "id": "plan_direct_demo",
        "name": "🔥 Instant Demo Pack (₹20 Plan)",
        "number_of_videos": "1000+",
        "price": 20,
        "validity": "30 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "Instant preview direct-demo pack with rapid access.",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4",
            "https://videotourl.com/videos/1791609530271-d1845e11-78bd-4465-a0e3-3e0dd57fb424.mp4"
        ]
    },
    # 10. Special VC Plan 1: 10 Minutes VC – ₹69
    "plan_vc_10": {
        "id": "plan_vc_10",
        "name": "🎙️ 10 Minutes VC Session",
        "number_of_videos": "1-on-1 Live",
        "price": 69,
        "validity": "Live Session",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "10 Minutes Live Video Call Session with personal attention and direct interaction."
    },
    # 11. Special VC Plan 2: 20 Minutes VC – ₹130
    "plan_vc_20": {
        "id": "plan_vc_20",
        "name": "🎙️ 20 Minutes VC Session",
        "number_of_videos": "1-on-1 Live",
        "price": 130,
        "validity": "Live Session",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "20 Minutes Live Video Call Session with extended duration and exclusive interaction."
    },
    # 12. Special VC Plan 3: 30 Minutes VC – ₹249
    "plan_vc_30": {
        "id": "plan_vc_30",
        "name": "🎙️ 30 Minutes VC Session",
        "number_of_videos": "1-on-1 Live",
        "price": 249,
        "validity": "Live Session",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "30 Minutes Live Video Call Session featuring complete priority access and detailed interaction."
    },
    # 13. Normal Plan 13
    "plan_13": {
        "id": "plan_19",
        "name": "Mega Creator Bundle 13",
        "number_of_videos": "12000+",
        "price": 299,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉🇴 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ]
    },
    # 14. Normal Plan 14 (Reference Plan 10 structure)
    "plan_10": {
        "id": "plan_20",
        "name": "𝗔𝗟𝗟 𝗩𝗜𝗣  𝗠𝗘𝗚𝗔 𝗣𝗔𝗖𝗞 🔥",
        "number_of_videos": "10000+",
        "price": 200,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demos": [
            "https://i.ibb.co/5X0hc5dd/logo.png"
        ],
        "gallery": [
            "https://i.ibb.co/5X0hc5dd/logo.png"
        ]
    }
}

# Available individual selectable packs for the ₹23 Multi-Pack feature
AVAILABLE_PACKS = [
    {"id": "pack_a", "name": "Bollywood Masala Pack"},
    {"id": "pack_b", "name": "South HD Collection"},
    {"id": "pack_c", "name": "Web Series Special"},
    {"id": "pack_d", "name": "Exclusive Hot Vault"},
    {"id": "pack_e", "name": "Desi MMS Collection"},
    {"id": "pack_f", "name": "International VIP Pack"},
    {"id": "pack_g", "name": "Uncensored Clips Pack"}
]

DB_FILE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_id TEXT,
            price REAL,
            status TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_id TEXT,
            price REAL,
            file_id TEXT,
            status TEXT,
            submitted_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_id TEXT,
            price REAL,
            approved_at TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('upi_id', ?)", (UPI_ID,))
    conn.commit()
    conn.close()

def get_current_upi():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key='upi_id'")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else UPI_ID

# ==========================================
# LOGGING SETUP
# ==========================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================================
# HANDLERS & BOT LOGIC
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)",
        (user.id, user.username, user.first_name, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    keyboard = [
        [
            InlineKeyboardButton("𝙔𝙀𝙎 𝙄 𝘼𝙈 18+ ✅", callback_data="start"),
            InlineKeyboardButton("𝙄 𝘼𝙈 𝙉𝙊𝙏 18+ ❌", callback_data="exit")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.delete()
        await context.bot.send_photo(
            chat_id=user.id,
            photo=START_IMAGE_URL,
            caption=START_CAPTION,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        try:
            await update.message.reply_photo(
                photo=START_IMAGE_URL,
                caption=START_CAPTION,
                reply_markup=reply_markup,
                parse_mode="HTML",
                read_timeout=60,
                write_timeout=60,
                connect_timeout=60,
                pool_timeout=30
            )
        except Exception:
            logger.exception("START PHOTO ERROR")
            await update.message.reply_text(
                START_CAPTION,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

async def exit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Access Cancelled ❌", show_alert=True)
    await query.edit_message_caption(
        caption="⚠️ <b>𝘼𝘾𝘾𝙀𝙎𝙎 𝘾𝘼𝙉𝘾𝙀𝙇𝙇𝙀𝘿</b> ❌",
        parse_mode="HTML"
    )

async def start_access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        pass

    await send_main_welcome(update.effective_user.id, context)

def make_button(text, callback_data=None, url=None, style="primary"):
    kwargs = {"text": text}
    if callback_data is not None:
        kwargs["callback_data"] = callback_data
    if url is not None:
        kwargs["url"] = url
    return InlineKeyboardButton(**kwargs)

async def send_main_welcome(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for plan_key, plan in PLAN.items():
        btn_text = f"{plan['name']} | ₹{plan['price']}"
        keyboard.append([
            make_button(
                btn_text,
                callback_data=f"plan_detail_{plan_key}",
                style="danger"
            )
        ])

    keyboard.append([
        make_button(
            "🎬 𝗗𝗘𝗠𝗢",
            callback_data="main_demo_menu",
            style="success"
        )
    ])

    keyboard.append([
        make_button(
            "𝗣𝗥𝗢𝗢𝗙 𝗖𝗛𝗔𝗡𝗡𝗘𝗟",
            url=PROOF_URL,
            style="primary"
        )
    ])

    keyboard.append([
        make_button(
            "𝗦𝗨𝗣𝗣𝗢𝗥𝗧 📞",
            url=SUPPORT_URL,
            style="success"
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=WELCOME_IMAGE_URL,
            caption=WELCOME_CAPTION,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception:
        logger.exception("WELCOME PHOTO ERROR")
        await context.bot.send_message(
            chat_id=chat_id,
            text=WELCOME_CAPTION,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

async def main_demo_menu_callback(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = []
    for plan in PLAN.values():
        if not isinstance(plan, dict):
            continue
        plan_key = str(plan.get("id", "")).strip()
        if not plan_key.startswith("plan_"):
            continue
        # Skip special plans from demo menu list if they don't use standard demo viewer
        if plan_key in ["plan_multi_pack", "plan_vc_10", "plan_vc_20", "plan_vc_30"]:
            continue

        btn_text = f"🎬 Demo: {plan.get('name', plan_key)} | ₹{plan.get('price', 'N/A')} 🔥"
        keyboard.append([
            make_button(
                btn_text,
                callback_data=f"demo_start_{plan_key}_0",
                style="danger"
            )
        ])

    keyboard.append([
        make_button(
            "🔙 BACK TO MAIN MENU",
            callback_data="back_to_main",
            style="primary"
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = "<b>𝙅𝙄𝙎 𝙋𝙇𝘼𝙉 𝙆𝘼 𝘿𝙀𝙈𝙊 𝘿𝙀𝙆𝙃𝙉𝘼 𝙃𝘼𝙄 𝙑𝙊 𝙎𝙀𝙇𝙀𝘾𝙏 𝙆𝘼𝙍𝙊 ❤️👇:</b>"

    await query.edit_message_caption(
        caption=caption,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    await send_main_welcome(update.effective_user.id, context)

async def plan_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    plan_id = data.replace("plan_detail_", "")
    plan = PLAN.get(plan_id)
    if not plan:
        await query.answer("Plan not found.", show_alert=True)
        return

    # 1. SPECIAL PLAN: ₹20 PLAN – DIRECT DEMO
    if plan_id == "plan_direct_demo":
        demos = plan.get("demo_videos", [])
        if demos:
            media = [InputMediaVideo(media=fid, has_spoiler=True, caption="🎬 Instant Direct Demo" if i == 0 else "") for i, fid in enumerate(demos[:10])]
            try:
                await query.message.delete()
                await context.bot.send_media_group(chat_id=update.effective_user.id, media=media)
            except Exception as e:
                logger.error(f"Error sending direct demo media group: {e}")
        
        caption = (
            f"⚡ <b>{plan['name']}</b> ⚡\n\n"
            f"💰 <b>Price:</b> ₹{plan['price']}\n"
            f"⏳ <b>Validity:</b> {plan['validity']}\n\n"
            f"<b>Description:</b>\n{plan.get('description', '')}"
        )
        keyboard = [
            [InlineKeyboardButton(f"💳 BUY NOW ₹{plan['price']} 🔥", callback_data=f"buy_{plan_id}", style="success")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main", style="primary")]
        ]
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    # 2. SPECIAL PLAN: ₹23 PLAN – MULTI-PACK SELECTION
    if plan_id == "plan_multi_pack":
        context.user_data["selected_packs"] = []
        await render_multipack_menu(query, context, edit_message=True)
        return

    # 3. SPECIAL VC PLANS
    if plan_id in ["plan_vc_10", "plan_vc_20", "plan_vc_30"]:
        vc_caption = (
            f"🎙️ <b>{plan['name']}</b> 🎙️\n\n"
            f"💰 <b>Price:</b> ₹{plan['price']}\n"
            f"⏳ <b>Duration:</b> {plan['validity']}\n\n"
            f"<b>Details:</b>\n{plan['description']}\n\n"
            "👇 Click below to choose your preferred contact method to connect with us!"
        )
        keyboard = [
            [InlineKeyboardButton("📱 Send in WhatsApp", callback_data=f"vc_contact_wa_{plan_id}")],
            [InlineKeyboardButton("✈️ Send in Telegram", callback_data=f"vc_contact_tg_{plan_id}")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
        ]
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=plan["image_url"], caption=vc_caption, parse_mode="HTML"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=update.effective_user.id,
                photo=plan["image_url"],
                caption=vc_caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        return

    # Standard Plan Logic
    caption = SHARED_CAPTION_TEMPLATE.format(
        plan_name=plan["name"],
        number_of_videos=plan["number_of_videos"],
        price=plan["price"],
        validity=plan["validity"],
        description=plan.get("description", "N/A")
    )

    keyboard = [
        [InlineKeyboardButton(" 𝘿𝙀𝙈𝙊 🎬", callback_data=f"demo_start_{plan_id}_0", style="danger")],
        [InlineKeyboardButton(f" 𝘽𝙐𝙔 𝙉𝙊𝙒 💳 ₹{plan['price']} 🔥", callback_data=f"buy_{plan_id}", style="success")],
        [InlineKeyboardButton(" 𝘽𝘼𝘾𝙆", callback_data="back_to_main", style="primary")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if plan_id == "plan_10" and "gallery" in plan:
        try:
            await query.message.delete()
            media = [InputMediaPhoto(media=img) for img in plan["gallery"][:6]]
            await context.bot.send_media_group(chat_id=update.effective_user.id, media=media)
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"<b>{caption}</b>",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            return
        except Exception as e:
            logger.error(f"Error sending media group: {e}")

    try:
        await query.edit_message_media(
            media=InputMediaPhoto(media=plan["image_url"], caption=caption, parse_mode="HTML"),
            reply_markup=reply_markup
        )
    except Exception:
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=update.effective_user.id,
            photo=plan["image_url"],
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# ==========================================
# MULTI-PACK SELECTION HANDLERS (₹23 Plan)
# ==========================================
async def render_multipack_menu(query_or_update, context, edit_message=True):
    selected = context.user_data.get("selected_packs", [])
    count = len(selected)

    text = (
        f"✨ <b>CUSTOM MULTI-PACK BUNDLE</b> ✨\n\n"
        f"Select exactly <b>4 packs</b> from the list below.\n"
        f"📊 Current Selection: <b>{count}/4 Selected</b>\n\n"
        "Tap a pack to select or deselect:"
    )

    keyboard = []
    for pack in AVAILABLE_PACKS:
        is_sel = pack["id"] in selected
        emoji = "✅" if is_sel else "❌"
        btn_text = f"{emoji} {pack['name']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"mp_toggle_{pack['id']}")])

    if count == 4:
        keyboard.append([InlineKeyboardButton("🚀 CONTINUE TO PAYMENT (₹120)", callback_data="mp_continue")])
    else:
        keyboard.append([InlineKeyboardButton(f"🔒 Select {4 - count} more pack(s)", callback_data="mp_disabled")])

    keyboard.append([InlineKeyboardButton("🔙 BACK TO MAIN MENU", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if edit_message:
        try:
            await query_or_update.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            try:
                await query_or_update.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML")
            except Exception:
                pass
    else:
        await query_or_update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def multipack_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pack_id = query.data.replace("mp_toggle_", "")
    
    if "selected_packs" not in context.user_data:
        context.user_data["selected_packs"] = []
    
    selected = context.user_data["selected_packs"]
    if pack_id in selected:
        selected.remove(pack_id)
    else:
        if len(selected) < 4:
            selected.append(pack_id)
        else:
            await query.answer("You can select maximum 4 packs!", show_alert=True)
            return

    await render_multipack_menu(query, context, edit_message=True)

async def multipack_disabled_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected = context.user_data.get("selected_packs", [])
    count = len(selected)
    await query.answer(f"Please select exactly 4 packs! Currently selected: {count}/4", show_alert=True)

async def multipack_continue_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected = context.user_data.get("selected_packs", [])
    if len(selected) != 4:
        await query.answer("You must select exactly 4 packs first!", show_alert=True)
        return

    user_id = update.effective_user.id
    current_upi = get_current_upi()
    price = 120.0
    plan_id = "plan_multi_pack"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pending_purchases (user_id, plan_id, price, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
        (user_id, plan_id, price, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    upi_uri = f"upi://pay?pa={current_upi}&pn={PAYEE_NAME}&am={price}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(upi_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    bio = io.BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)

    selected_names = [p["name"] for p in AVAILABLE_PACKS if p["id"] in selected]
    packs_list_str = "\n".join([f"• {name}" for name in selected_names])

    payment_caption = (
        f"<b>𝙋𝘼𝙔𝙈𝙀𝙉𝙏 𝙋𝘼𝙂𝙀 💳: ₹{price} 🔥</b>\n\n"
        f"📦 <b>Selected Packs (4):</b>\n{packs_list_str}\n\n"
        f"🆔 <b>𝙐𝙋𝙄 𝙄𝘿:</b> <code>{current_upi}</code>\n\n"
        "1️⃣ Scan the QR.\n"
        "2️⃣ Pay the exact amount (₹120).\n"
        "3️⃣ Click <b>VERIFY MY PAYMENT ✅</b>.\n"
        "4️⃣ Send payment screenshot."
    )

    keyboard = [
        [InlineKeyboardButton(" 𝙑𝙀𝙍𝙄𝙁𝙔 𝙈𝙔 𝙋𝘼𝙔𝙈𝙀𝙉𝙏 ✅", callback_data=f"verify_pay_{plan_id}", style="success")],
        [InlineKeyboardButton(" 𝘾𝘼𝙉𝘾𝙀𝙇 𝙋𝙐𝙍𝘾𝙃𝘼𝙎𝙀", callback_data=f"cancel_buy_{plan_id}", style="danger")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_photo(
        chat_id=user_id,
        photo=bio,
        caption=payment_caption,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

# ==========================================
# VC PLANS CONTACT HANDLERS
# ==========================================
async def vc_contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    # data format: vc_contact_wa_plan_vc_10 or vc_contact_tg_plan_vc_10
    parts = data.split("_")
    method = parts[2] # wa or tg
    plan_id = f"{parts[3]}_{parts[4]}_{parts[5]}" if len(parts) > 5 else f"{parts[3]}_{parts[4]}"
    
    plan = PLAN.get(plan_id)
    if not plan:
        await query.answer("Plan info not found.", show_alert=True)
        return

    prefilled_msg = f"Hello, I want to book the {plan['name']} priced at ₹{plan['price']}. Please guide me further."

    if method == "wa":
        wa_url = f"https://wa.me/{VC_WHATSAPP_NUMBER}?text={quote_plus_custom(prefilled_msg)}"
        keyboard = [[InlineKeyboardButton("🔗 Open WhatsApp Chat", url=wa_url)], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]]
        await query.edit_message_caption(
            caption=f"📱 <b>WhatsApp Contact Link Ready</b>\n\nClick below to connect directly on WhatsApp with pre-filled message:\n\n<i>\"{prefilled_msg}\"</i>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    elif method == "tg":
        tg_url = f"https://t.me/{VC_TELEGRAM_USERNAME}?text={quote_plus_custom(prefilled_msg)}"
        # Fallback to direct username if telegram text ref fails or standard t.me link
        keyboard = [[InlineKeyboardButton("🔗 Open Telegram Chat", url=f"https://t.me/{VC_TELEGRAM_USERNAME}")], [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]]
        await query.edit_message_caption(
            caption=f"✈️ <b>Telegram Contact Link Ready</b>\n\nClick below to message our support username (@{VC_TELEGRAM_USERNAME}) with details:\n\n<i>\"{prefilled_msg}\"</i>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

def quote_plus_custom(text):
    import urllib.parse
    return urllib.parse.quote_plus(text)

async def demo_viewer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("_")
    plan_id = f"{parts[2]}_{parts[3]}"
    demo_index = int(parts[4])

    plan = PLAN.get(plan_id)
    if not plan:
        await query.answer("Plan not found.", show_alert=True)
        return

    demos = plan.get("demo_videos", [])
    if not demos:
        await query.answer("No demos available for this plan.", show_alert=True)
        return

    if demo_index >= len(demos):
        final_text = (
            "✨ <b>𝘼𝙇𝙇 𝘿𝙀𝙈𝙊𝙎 𝙊𝙑𝙀𝙍! 𝙋𝙇𝙀𝘼𝙎𝙀 𝙋𝙐𝙍𝘾𝙃𝘼𝙎𝙀 𝙏𝙃𝙀 𝙋𝙍𝙀𝙈𝙄𝙐𝙈 𝙋𝙇𝘼𝙉.</b> ✨\n\n"
            f"💰 Price: ₹{plan['price']} 🔥\n"
            f"🎬 Videos: {plan['number_of_videos']}\n"
            f"⏳ Validity: {plan['validity']}\n"
            "⚡ Access Time: Instant Delivery ✅\n\n"
        )
        keyboard = [
            [InlineKeyboardButton(f" 𝘽𝙐𝙔 𝙉𝙊𝙒 💳 ₹{plan['price']} 🔥", callback_data=f"buy_{plan_id}", style="success")],
            [InlineKeyboardButton(" 𝘽𝘼𝘾𝙆", callback_data="back_to_main", style="primary")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.delete()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=final_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return

    video_url = demos[demo_index]
    position_text = f"Demo {demo_index + 1}/{len(demos)}"

    keyboard = [
        [
            InlineKeyboardButton(" 𝙋𝙍𝙀𝙑 𝘿𝙀𝙈𝙊⬅️", callback_data=f"demo_start_{plan_id}_{demo_index - 1}" if demo_index > 0 else "noop", style="primary"),
            InlineKeyboardButton("𝙉𝙀𝙓𝙏 𝘿𝙀𝙈𝙊 ➡️", callback_data=f"demo_start_{plan_id}_{demo_index + 1}", style="primary")
        ],
        [
            InlineKeyboardButton(" 𝘽𝘼𝘾𝙆 𝙏𝙊 𝙋𝙇𝘼𝙉", callback_data=f"plan_detail_{plan_id}", style="danger")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.message.delete()
    except Exception:
        pass

    await context.bot.send_video(
        chat_id=update.effective_user.id,
        video=video_url,
        caption=f"🎥 <b>{plan['name']} - {position_text}</b>",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("⚠️ No earlier demo available.", show_alert=True)

async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_id = query.data.replace("buy_", "")
    plan = PLAN.get(plan_id)
    if not plan:
        await query.answer("Plan not found.", show_alert=True)
        return

    user_id = update.effective_user.id
    current_upi = get_current_upi()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pending_purchases (user_id, plan_id, price, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
        (user_id, plan_id, plan["price"], datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    upi_uri = f"upi://pay?pa={current_upi}&pn={PAYEE_NAME}&am={plan['price']}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(upi_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    bio = io.BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)

    payment_caption = (
        f"<b>𝙋𝘼𝙔𝙈𝙀𝙉𝙏 𝙋𝘼𝙂𝙀 💳: ₹{plan['price']} 🔥</b>\n\n"
        f"🆔 <b>𝙐𝙋𝙄 𝙄𝘿:</b> <code>{current_upi}</code>\n\n"
        "1️⃣ 𝙎𝙘𝙖𝙣 𝙩𝙝𝙚 𝙌𝙍.\n"
        "2️⃣ 𝙋𝙖𝙮 𝙩𝙝𝙚 𝙚𝙭𝙖𝙘𝙩 𝙖𝙢𝙤𝙪𝙣𝙩.\n"
        "3️⃣ 𝘾𝙡𝙞𝙘𝙠 <b>𝙄 𝙋𝘼𝙄𝘿 ✅</b>.\n"
        "4️⃣ 𝙎𝙚𝙣𝙙 𝙥𝙖𝙮𝙢𝙚𝙣𝙩 𝙨𝙘𝙧𝙚𝙚𝙣𝙨𝙝𝙤𝙩. ✅"
    )

    keyboard = [
        [InlineKeyboardButton(" 𝙑𝙀𝙍𝙄𝙁𝙔 𝙈𝙔 𝙋𝘼𝙔𝙈𝙀𝙉𝙏 ✅", callback_data=f"verify_pay_{plan_id}", style="success")],
        [InlineKeyboardButton(" 𝘾𝘼𝙉𝘾𝙀𝙇 𝙋𝙐𝙍𝘾𝙃𝘼𝙎𝙀", callback_data=f"cancel_buy_{plan_id}", style="danger")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_photo(
        chat_id=user_id,
        photo=bio,
        caption=payment_caption,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def cancel_purchase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Purchase cancelled.")
    user_id = update.effective_user.id

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE pending_purchases SET status='cancelled' WHERE user_id=? AND status='pending'", (user_id,))
    conn.commit()
    conn.close()

    await query.message.delete()
    await send_main_welcome(user_id, context)

async def verify_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT plan_id, price FROM pending_purchases WHERE user_id=? AND status='pending' ORDER BY id DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        await query.message.reply_text("⚠️ No active pending purchase found. Please start a new purchase.")
        return

    plan_id, price = row
    context.user_data["awaiting_screenshot"] = {"plan_id": plan_id, "price": price}

    await query.message.reply_text(
        "📸 <b>𝙋𝙡𝙚𝙖𝙨𝙚 𝙪𝙥𝙡𝙤𝙖𝙙 𝙮𝙤𝙪𝙧 𝙥𝙖𝙮𝙢𝙚𝙣𝙩 𝙨𝙘𝙧𝙚𝙚𝙣𝙨𝙝𝙤𝙩.</b>\n.",
        parse_mode="HTML"
    )

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if "awaiting_screenshot" not in context.user_data:
        return

    if not update.message.photo:
        await update.message.reply_text("⚠️ Please send a valid photo screenshot of your payment.")
        return

    photo_file = update.message.photo[-1]
    file_id = photo_file.file_id
    purchase_data = context.user_data.pop("awaiting_screenshot")
    plan_id = purchase_data["plan_id"]
    price = purchase_data["price"]
    plan = PLAN.get(plan_id, {"name": plan_id})

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO payment_submissions (user_id, plan_id, price, file_id, status, submitted_at) VALUES (?, ?, ?, ?, 'pending', ?)",
        (user.id, plan_id, price, file_id, datetime.utcnow().isoformat())
    )
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()

    await update.message.reply_text("✅ Your screenshot has been submitted for review. Please wait 5-10 minutes.")

    admin_caption = (
        "📥 <b>𝙋𝘼𝙔𝙈𝙀𝙉𝙏 𝙍𝙀𝘾𝙀𝙄𝙑𝙀𝘿</b>\n\n"
        f"📦 Plan: {plan['name']}\n"
        f"💰 Price: ₹{price}\n"
        f"👤 Username: @{user.username if user.username else 'N/A'}\n"
        f"🆔 User ID: {user.id}\n"
        f"⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    admin_keyboard = [
        [
            InlineKeyboardButton(" 𝘼𝙋𝙋𝙍𝙊𝙑𝙀 ✅", callback_data=f"approve_{submission_id}", style="success"),
            InlineKeyboardButton(" 𝙍𝙀𝙅𝙀𝘾𝙏 ❌", callback_data=f"reject_{submission_id}", style="danger")
        ]
    ]
    admin_markup = InlineKeyboardMarkup(admin_keyboard)

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=admin_caption,
                reply_markup=admin_markup,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

async def approve_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS:
        await query.answer("Unauthorized.", show_alert=True)
        return

    submission_id = int(query.data.replace("approve_", ""))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, plan_id, price, status FROM payment_submissions WHERE id=?", (submission_id,))
    row = cursor.fetchone()

    if not row or row[3] != 'pending':
        conn.close()
        await query.answer("Payment already processed or invalid.", show_alert=True)
        return

    user_id, plan_id, price, _ = row
    plan = PLAN.get(plan_id, {"name": plan_id})

    cursor.execute("UPDATE payment_submissions SET status='approved' WHERE id=?", (submission_id,))
    cursor.execute(
        "INSERT INTO purchases (user_id, plan_id, price, approved_at) VALUES (?, ?, ?, ?)",
        (user_id, plan_id, price, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    await query.answer("Payment Approved Successfully!")
    await query.edit_message_caption(caption=query.message.caption + "\n\n<b>STATUS: APPROVED ✅</b>", parse_mode="HTML")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 <b>Congratulations! Your payment for {plan['name']} has been approved.</b>\n\nYour access will be delivered to you shortly! 🚀",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

async def reject_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS:
        await query.answer("Unauthorized.", show_alert=True)
        return

    submission_id = int(query.data.replace("reject_", ""))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, status FROM payment_submissions WHERE id=?", (submission_id,))
    row = cursor.fetchone()

    if not row or row[1] != 'pending':
        conn.close()
        await query.answer("Payment already processed or invalid.", show_alert=True)
        return

    user_id = row[0]
    cursor.execute("UPDATE payment_submissions SET status='rejected' WHERE id=?", (submission_id,))
    conn.commit()
    conn.close()

    await query.answer("Payment Rejected.")
    await query.edit_message_caption(caption=query.message.caption + "\n\n<b>STATUS: REJECTED ❌</b>", parse_mode="HTML")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Your payment has been rejected. Please contact support if you believe this is a mistake."
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

# ==========================================
# ADMIN PANEL & COMMANDS
# ==========================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(price) FROM purchases")
    row = cursor.fetchone()
    conn.close()

    total_count = row[0] if row and row[0] else 0
    total_revenue = row[1] if row and row[1] else 0.0

    panel_text = (
        "🛠 <b>𝘼𝘿𝙈𝙄𝙉 𝘾𝙊𝙉𝙏𝙍𝙊𝙇 𝙋𝘼𝙉𝙀𝙇</b> 🛠\n\n"
        f"✅ <b>Total Approved Payments:</b> {total_count}\n"
        f"💵 <b>Total Revenue Collected:</b> ₹{total_revenue}\n\n"
        "Choose an action below:"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 𝗥𝙚𝙛𝙧𝙚𝙨𝙝 𝙎𝙩𝙖𝙩𝙨", callback_data="admin_refresh")],
        [InlineKeyboardButton("🗑 𝘾𝙡𝙚𝙖𝙧 𝘼𝙡𝙡 𝙎𝙩𝙖𝙩𝙨 & 𝙍𝙚𝙨𝙚𝙩", callback_data="admin_clear")],
        [InlineKeyboardButton("❌ 𝘾𝙡𝙤𝙨𝙚 𝙋𝙖𝙣𝙚𝙡", callback_data="admin_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(panel_text, reply_markup=reply_markup, parse_mode="HTML")

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await query.answer("Unauthorized.", show_alert=True)
        return

    data = query.data

    if data == "admin_refresh":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(price) FROM purchases")
        row = cursor.fetchone()
        conn.close()

        total_count = row[0] if row and row[0] else 0
        total_revenue = row[1] if row and row[1] else 0.0

        panel_text = (
            "🛠 <b>𝘼𝘿𝙈𝙄𝙉 𝘾𝙊𝙉𝙏𝙍𝙊𝙇 𝙋𝘼𝙉𝙀𝙇</b> 🛠\n\n"
            f"✅ <b>Total Approved Payments:</b> {total_count}\n"
            f"💵 <b>Total Revenue Collected:</b> ₹{total_revenue}\n\n"
            "Choose an action below:"
        )
        await query.answer("Stats refreshed!")
        try:
            await query.edit_message_text(panel_text, reply_markup=query.message.reply_markup, parse_mode="HTML")
        except Exception:
            pass

    elif data == "admin_clear":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM purchases")
        cursor.execute("DELETE FROM payment_submissions")
        cursor.execute("DELETE FROM pending_purchases")
        conn.commit()
        conn.close()

        await query.answer("All stats and records cleared successfully!", show_alert=True)
        panel_text = (
            "🛠 <b>𝘼𝘿𝙈𝙄𝙉 𝘾𝙊𝙉𝙏𝙍𝙊𝙇 𝙋𝘼𝙉𝙀𝙇</b> 🛠\n\n"
            "✅ <b>Total Approved Payments:</b> 0\n"
            "💵 <b>Total Revenue Collected:</b> ₹0.0\n\n"
            "<i>(Stats have been reset successfully)</i>"
        )
        try:
            await query.edit_message_text(panel_text, reply_markup=query.message.reply_markup, parse_mode="HTML")
        except Exception:
            pass

    elif data == "admin_close":
        await query.answer("Panel closed.")
        try:
            await query.message.delete()
        except Exception:
            pass

async def change_upi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /changeupi new_upi_id@handle")
        return

    new_upi = context.args[0]
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE config SET value=? WHERE key='upi_id'", (new_upi,))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ UPI ID successfully updated to: <code>{new_upi}</code>", parse_mode="HTML")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to the message you want to broadcast with /broadcast.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    msg_to_broadcast = update.message.reply_to_message
    success, failed = 0, 0

    for (uid,) in users:
        try:
            await msg_to_broadcast.copy(chat_id=uid)
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_text(f"✅ Broadcast complete!\nSuccessful: {success}\nFailed: {failed}")

# ==========================================
# MAIN APP ENTRYPOINT
# ==========================================
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing!")
        return

    init_db()
    application = Application.builder().token(BOT_TOKEN).build()

    # Core Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("changeupi", change_upi_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))

    # Callback Query Handlers
    application.add_handler(CallbackQueryHandler(start_access_callback, pattern="^start$"))
    application.add_handler(CallbackQueryHandler(exit_callback, pattern="^exit$"))
    application.add_handler(CallbackQueryHandler(main_demo_menu_callback, pattern="^main_demo_menu$"))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
    application.add_handler(CallbackQueryHandler(plan_detail_callback, pattern="^plan_detail_"))
    application.add_handler(CallbackQueryHandler(demo_viewer_callback, pattern="^demo_start_"))
    application.add_handler(CallbackQueryHandler(noop_callback, pattern="^noop$"))
    application.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(verify_payment_callback, pattern="^verify_pay_"))
    application.add_handler(CallbackQueryHandler(cancel_purchase_callback, pattern="^cancel_buy_"))
    application.add_handler(CallbackQueryHandler(approve_payment_callback, pattern="^approve_"))
    application.add_handler(CallbackQueryHandler(reject_payment_callback, pattern="^reject_"))
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^admin_"))

    # Multi-pack Select Callbacks
    application.add_handler(CallbackQueryHandler(multipack_toggle_callback, pattern="^mp_toggle_"))
    application.add_handler(CallbackQueryHandler(multipack_disabled_callback, pattern="^mp_disabled$"))
    application.add_handler(CallbackQueryHandler(multipack_continue_callback, pattern="^mp_continue$"))

    # VC Contact Callbacks
    application.add_handler(CallbackQueryHandler(vc_contact_callback, pattern="^vc_contact_"))

    # Message Handlers for Screenshots
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
