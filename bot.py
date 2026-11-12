import os
import io
import sqlite3
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
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

UPI_ID = os.getenv("UPI_ID", "haaland78@ybl")
PAYEE_NAME = os.getenv("PAYEE_NAME", "Social Flux")

PROOF_URL = "https://t.me/fluxproofs"
SUPPORT_URL = "https://t.me/fluxsupport"

START_IMAGE_URL = "https://ibb.co/GhbLV5P"
START_CAPTION = (
    "✨ <b>𝘽𝙚𝙛𝙤𝙧𝙚 𝙘𝙤𝙣𝙩𝙞𝙣𝙪𝙞𝙣𝙜, 𝙥𝙡𝙚𝙖𝙨𝙚 𝙘𝙤𝙣𝙛𝙞𝙧𝙢 𝙮𝙤𝙪 𝙖𝙧𝙚 18 𝙤𝙧 𝙤𝙡𝙙𝙚𝙧</b> \n\n"
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
# PLANS CONFIGURATION (Exactly 24 Full Plan Slots)
# ==========================================
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
    "plan_multi_pack": {
        "id": "plan_multi_pack",
        "name": "✨ Multi-Pack Custom Bundle (₹23 Pack)",
        "number_of_videos": "Custom Selection (4 Packs)",
        "price": 120,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "Select exactly 4 packs from our existing plans to build your custom bundle for ₹120!"
    },
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
    "plan_vc_10": {
        "id": "plan_vc_10",
        "name": "🎙️ 10 Minutes VC Session",
        "number_of_videos": "1-on-1 Live",
        "price": 69,
        "validity": "Live Session",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "10 Minutes Live Video Call Session with personal attention and direct interaction."
    },
    "plan_vc_20": {
        "id": "plan_vc_20",
        "name": "🎙️ 20 Minutes VC Session",
        "number_of_videos": "1-on-1 Live",
        "price": 130,
        "validity": "Live Session",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "20 Minutes Live Video Call Session with extended duration and exclusive interaction."
    },
    "plan_vc_30": {
        "id": "plan_vc_30",
        "name": "🎙️ 30 Minutes VC Session",
        "number_of_videos": "1-on-1 Live",
        "price": 249,
        "validity": "Live Session",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "30 Minutes Live Video Call Session featuring complete priority access and detailed interaction."
    },
    "plan_13": {
        "id": "plan_13",
        "name": "Mega Creator Bundle 13",
        "number_of_videos": "12000+",
        "price": 299,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_14": {
        "id": "plan_14",
        "name": "Pro Creator Bundle 14",
        "number_of_videos": "1500+",
        "price": 150,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_15": {
        "id": "plan_15",
        "name": "Elite Video Pack 15",
        "number_of_videos": "1800+",
        "price": 175,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_16": {
        "id": "plan_16",
        "name": "Special Masterclass 16",
        "number_of_videos": "2200+",
        "price": 220,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_17": {
        "id": "plan_17",
        "name": "Prime Creator Pack 17",
        "number_of_videos": "2500+",
        "price": 250,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_18": {
        "id": "plan_18",
        "name": "Ultra Bundle 18",
        "number_of_videos": "3000+",
        "price": 300,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_19": {
        "id": "plan_19",
        "name": "Supreme Creator Pack 19",
        "number_of_videos": "3500+",
        "price": 350,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_20": {
        "id": "plan_20",
        "name": "Grand Video Vault 20",
        "number_of_videos": "4000+",
        "price": 400,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_21": {
        "id": "plan_21",
        "name": "Infinity Creator Pack 21",
        "number_of_videos": "4500+",
        "price": 450,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_22": {
        "id": "plan_22",
        "name": "Legendary Collection 22",
        "number_of_videos": "5000+",
        "price": 500,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_23": {
        "id": "plan_23",
        "name": "Titanium Creator Pack 23",
        "number_of_videos": "5500+",
        "price": 550,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌",
        "demo_videos": ["https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"]
    },
    "plan_10": {
        "id": "plan_10",
        "name": "𝗔𝗟𝗟 𝗩𝗜𝗣  𝗠𝗘𝗚𝗔 𝗣𝗔𝗖𝗞 🔥",
        "number_of_videos": "10000+",
        "price": 200,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/logo.png",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demos": ["https://i.ibb.co/5X0hc5dd/logo.png"],
        "gallery": ["https://i.ibb.co/5X0hc5dd/logo.png"]
    }
}

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

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# BOT HANDLERS & LOGIC
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
            InlineKeyboardButton("𝙔ES 𝙄 𝘼𝙈 18+ ✅", callback_data="start"),
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
                parse_mode="HTML"
            )
        except Exception:
            logger.exception("START PHOTO ERROR")
            await update.message.reply_text(START_CAPTION, reply_markup=reply_markup, parse_mode="HTML")

async def exit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Access Cancelled ❌", show_alert=True)
    await query.edit_message_caption(caption="⚠️ <b>𝘼𝘾𝘾𝙀𝙎𝙎 𝘾𝘼𝙉𝘾𝙀𝙇𝙇𝙀𝘿</b> ❌", parse_mode="HTML")

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
        if plan_key.startswith("plan_vc_"):
            continue
        btn_text = f"{plan['name']} | ₹{plan['price']}"
        keyboard.append([make_button(btn_text, callback_data=f"plan_detail_{plan_key}", style="danger")])

    keyboard.append([make_button("🎙️ VC PLANS", callback_data="vc_main_menu", style="success")])
    keyboard.append([make_button("🎬 𝗗𝗘𝗠𝗢", callback_data="main_demo_menu", style="success")])
    keyboard.append([make_button("𝗣𝗥𝗢𝗢𝗙 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url=PROOF_URL, style="primary")])
    keyboard.append([make_button("𝗦𝗨𝗣𝗣𝗢𝗥𝗧 📞", url=SUPPORT_URL, style="success")])

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
        await context.bot.send_message(chat_id=chat_id, text=WELCOME_CAPTION, reply_markup=reply_markup, parse_mode="HTML")

async def vc_main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    vc_caption = "🎙️ <b>𝙑𝙄𝘿𝙀𝙊 𝘾𝘼𝙇𝙇 (𝙑𝘾) 𝙋𝙇𝘼𝙉𝙎 𝙈𝙀𝙉𝙐</b> 🎙️\n\nSelect a session duration below for 1-on-1 private calls:"
    keyboard = [
        [InlineKeyboardButton("🎙️ 10 Minutes VC – ₹69", callback_data="plan_detail_plan_vc_10")],
        [InlineKeyboardButton("🎙️ 20 Minutes VC – ₹130", callback_data="plan_detail_plan_vc_20")],
        [InlineKeyboardButton("🎙️ 30 Minutes VC – ₹249", callback_data="plan_detail_plan_vc_30")],
        [InlineKeyboardButton("🔙 BACK TO MAIN MENU", callback_data="back_to_main")]
    ]
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(media=WELCOME_IMAGE_URL, caption=vc_caption, parse_mode="HTML"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception:
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=update.effective_user.id,
            photo=WELCOME_IMAGE_URL,
            caption=vc_caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
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
        if not plan_key.startswith("plan_") or plan_key.startswith("plan_vc_"):
            continue
        if plan_key in ["plan_multi_pack"]:
            continue

        btn_text = f"🎬 Demo: {plan.get('name', plan_key)} | ₹{plan.get('price', 'N/A')} 🔥"
        keyboard.append([make_button(btn_text, callback_data=f"demo_start_{plan_key}_0", style="danger")])

    keyboard.append([make_button("🔙 BACK TO MAIN MENU", callback_data="back_to_main", style="primary")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = "<b>𝙅𝙄𝙎 𝙋𝙇𝘼𝙉 𝙆𝘼 𝘿𝙀𝙈𝙊 𝘿𝙀𝙆𝙃𝙉𝘼 𝙃𝘼𝙄 𝙑𝙊 𝙎𝙀𝙇𝙀𝘾𝙏 𝙆𝘼𝙍𝙊 ❤️👇:</b>"

    await query.edit_message_caption(caption=caption, reply_markup=reply_markup, parse_mode="HTML")

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    await send_main_welcome(update.effective_user.id, context)

async def render_multipack_menu(query, context, edit_message=True):
    selected = context.user_data.get("selected_packs", [])
    count = len(selected)

    keyboard = []
    # Automatically extract existing plans from PLAN dict to use for selection (excluding special multi-pack, direct demo, and VC plans)
    for p_id, p_data in PLAN.items():
        if p_id in ["plan_multi_pack", "plan_direct_demo"] or p_id.startswith("plan_vc_"):
            continue
        is_sel = p_id in selected
        prefix = "✅ " if is_sel else "🔲 "
        btn_text = f"{prefix}{p_data['name']} (₹{p_data['price']})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"multipack_toggle_{p_id}")])

    continue_text = f"Continue ({count}/4 Selected) {'🚀' if count == 4 else '🔒 (Select exactly 4)'}"
    if count == 4:
        keyboard.append([InlineKeyboardButton(continue_text, callback_data="multipack_continue")])
    else:
        keyboard.append([InlineKeyboardButton(continue_text, callback_data="multipack_invalid")])

    keyboard.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")])

    caption = (
        "✨ <b>₹23 MULTI-PACK SELECTION INTERFACE</b> ✨\n\n"
        f"📊 <b>Selection Status:</b> <code>{count}/4 Selected</code>\n"
        "👉 Please choose exactly <b>4 packs</b> from your existing plans below:"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    if edit_message:
        try:
            await query.edit_message_caption(caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.from_user.id,
                photo="https://i.ibb.co/5X0hc5dd/logo.png",
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
    else:
        await query.message.reply_text(caption, reply_markup=reply_markup, parse_mode="HTML")

async def multipack_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("multipack_toggle_"):
        plan_id = data.replace("multipack_toggle_", "")
        selected = context.user_data.setdefault("selected_packs", [])
        if plan_id in selected:
            selected.remove(plan_id)
            await query.answer("Plan deselected ❌")
        else:
            if len(selected) >= 4:
                await query.answer("You can select maximum 4 packs! Deselect one to change.", show_alert=True)
            else:
                selected.append(plan_id)
                await query.answer("Plan selected ✅")
        await render_multipack_menu(query, context, edit_message=True)

    elif data == "multipack_invalid":
        selected = context.user_data.get("selected_packs", [])
        await query.answer(f"Current selection: {len(selected)}/4. You must select exactly 4 packs to continue!", show_alert=True)

    elif data == "multipack_continue":
        selected = context.user_data.get("selected_packs", [])
        if len(selected) != 4:
            await query.answer("Please select exactly 4 packs first!", show_alert=True)
            return
        await query.answer("Generating payment QR for ₹120...")
        await trigger_upi_payment(query, context, "plan_multi_pack", 120.0)

async def trigger_upi_payment(query, context, plan_id, price):
    current_upi = get_current_upi()
    upi_url = f"upi://pay?pa={current_upi}&pn={PAYEE_NAME}&am={price:.2f}&cu=INR"
    img = qrcode.make(upi_url)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)

    caption = (
        f"💳 <b>𝙋𝘼𝙔𝙈𝙀𝙉𝙏 𝙂𝘼𝙏𝙀𝙒𝘼𝙔</b> 💳\n\n"
        f"📌 <b>Amount to Pay:</b> ₹{price:.2f}\n"
        f"🎯 <b>UPI ID:</b> <code>{current_upi}</code>\n"
        f"👤 <b>Payee:</b> {PAYEE_NAME}\n\n"
        f"1️⃣ Scan the QR code using any UPI app (GPay, PhonePe, Paytm).\n"
        f"2️⃣ Complete the payment of <b>₹{price:.2f}</b>.\n"
        f"3️⃣ Send screenshot below for instant admin verification."
    )
    keyboard = [
        [InlineKeyboardButton("📤 SUBMIT PAYMENT SCREENSHOT", callback_data=f"submit_proof_{plan_id}_{price}")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
    ]
    try:
        await query.message.delete()
    except Exception:
        pass

    await context.bot.send_photo(
        chat_id=query.from_user.id,
        photo=bio,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def plan_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    plan_id = data.replace("plan_detail_", "")
    plan = PLAN.get(plan_id)
    if not plan:
        await query.answer("Plan not found.", show_alert=True)
        return

    # SPECIAL PLAN: ₹20 PLAN – DIRECT DEMO
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
            [InlineKeyboardButton(f"💳 BUY NOW ₹{plan['price']} 🔥", callback_data=f"buy_{plan_id}")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
        ]
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    # SPECIAL PLAN: ₹23 MULTI-PACK SELECTION
    if plan_id == "plan_multi_pack":
        context.user_data["selected_packs"] = []
        await render_multipack_menu(query, context, edit_message=True)
        return

    # SPECIAL VC PLANS
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
            [InlineKeyboardButton("🔙 BACK", callback_data="vc_main_menu")]
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
        [InlineKeyboardButton("𝘿𝙀𝙈𝙊 🎬", callback_data=f"demo_start_{plan_id}_0")],
        [InlineKeyboardButton(f"𝘽𝙐𝙔 𝙉𝙊𝙒 💳 ₹{plan['price']} 🔥", callback_data=f"buy_{plan_id}")],
        [InlineKeyboardButton("𝘽𝘼𝘾𝙆", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

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

async def vc_contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith("vc_contact_wa_"):
        plan_id = data.replace("vc_contact_wa_", "")
        plan = PLAN.get(plan_id, {})
        msg = f"Hello, I want to book the {plan.get('name', 'VC Session')} for ₹{plan.get('price')}."
        wa_url = f"https://wa.me/{VC_WHATSAPP_NUMBER}?text={msg.replace(' ', '%20')}"
        keyboard = [[InlineKeyboardButton("💬 Click to Open WhatsApp", url=wa_url)], [InlineKeyboardButton("🔙 BACK", callback_data="vc_main_menu")]]
        await query.edit_message_caption(caption=f"📱 <b>WhatsApp Contact Ready</b>\n\nClick below to open chat with pre-filled message:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    elif data.startswith("vc_contact_tg_"):
        plan_id = data.replace("vc_contact_tg_", "")
        plan = PLAN.get(plan_id, {})
        msg = f"Hello, I want to book the {plan.get('name', 'VC Session')} for ₹{plan.get('price')}."
        tg_url = f"https://t.me/{VC_TELEGRAM_USERNAME}?text={msg.replace(' ', '%20')}"
        keyboard = [[InlineKeyboardButton("✈️ Click to Open Telegram Chat", url=tg_url)], [InlineKeyboardButton("🔙 BACK", callback_data="vc_main_menu")]]
        await query.edit_message_caption(caption=f"✈️ <b>Telegram Contact Ready</b>\n\nClick below to message support directly:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_id = query.data.replace("buy_", "")
    plan = PLAN.get(plan_id)
    if not plan:
        await query.answer("Plan not found.", show_alert=True)
        return
    await trigger_upi_payment(query, context, plan_id, float(plan["price"]))

async def submit_proof_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_parts = query.data.replace("submit_proof_", "").split("_")
    plan_id = data_parts[0]
    context.user_data["awaiting_proof_for"] = plan_id
    await query.message.reply_text("📤 Please send the screenshot of your payment now. Our system will forward it to admin for verification.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if "awaiting_proof_for" in context.user_data and update.message.photo:
        plan_id = context.user_data.pop("awaiting_proof_for")
        plan = PLAN.get(plan_id, {})
        file_id = update.message.photo[-1].file_id

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO payment_submissions (user_id, plan_id, price, file_id, status, submitted_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user.id, plan_id, plan.get("price", 0), file_id, "pending", datetime.utcnow().isoformat())
        )
        sub_id = cursor.lastrowid
        conn.commit()
        conn.close()

        await update.message.reply_text("✅ Payment screenshot submitted successfully! Admin will verify and approve shortly.")

        # Notify Admins
        admin_keyboard = [
            [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{sub_id}"), InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{sub_id}")]
        ]
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=f"🔔 <b>New Payment Submission!</b>\n\n👤 User: @{user.username} ({user.id})\n📦 Plan: {plan.get('name')}\n💰 Price: ₹{plan.get('price')}",
                    reply_markup=InlineKeyboardMarkup(admin_keyboard),
                    parse_mode="HTML"
                )
            except Exception:
                pass

async def admin_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await query.answer("Unauthorized!", show_alert=True)
        return

    data = query.data
    if data.startswith("admin_approve_"):
        sub_id = int(data.replace("admin_approve_", ""))
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, plan_id, price FROM payment_submissions WHERE id=?", (sub_id,))
        row = cursor.fetchone()
        if row:
            u_id, p_id, price = row
            cursor.execute("UPDATE payment_submissions SET status='approved' WHERE id=?", (sub_id,))
            cursor.execute("INSERT INTO purchases (user_id, plan_id, price, approved_at) VALUES (?, ?, ?, ?)", (u_id, p_id, price, datetime.utcnow().isoformat()))
            conn.commit()
            conn.close()
            await query.answer("Approved successfully ✅")
            await query.edit_message_caption(caption=query.message.caption + "\n\n<b>STATUS: APPROVED ✅</b>", parse_mode="HTML")
            try:
                await context.bot.send_message(chat_id=u_id, text="🎉 Your payment has been approved by admin! Enjoy your premium access.")
            except Exception:
                pass
    elif data.startswith("admin_reject_"):
        sub_id = int(data.replace("admin_reject_", ""))
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE payment_submissions SET status='rejected' WHERE id=?", (sub_id,))
        conn.commit()
        conn.close()
        await query.answer("Rejected ❌")
        await query.edit_message_caption(caption=query.message.caption + "\n\n<b>STATUS: REJECTED ❌</b>", parse_mode="HTML")

# ==========================================
# MAIN INITIALIZATION
# ==========================================
def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start_access_callback, pattern="^start$"))
    application.add_handler(CallbackQueryHandler(exit_callback, pattern="^exit$"))
    application.add_handler(CallbackQueryHandler(vc_main_menu_callback, pattern="^vc_main_menu$"))
    application.add_handler(CallbackQueryHandler(main_demo_menu_callback, pattern="^main_demo_menu$"))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
    application.add_handler(CallbackQueryHandler(plan_detail_callback, pattern="^plan_detail_"))
    application.add_handler(CallbackQueryHandler(vc_contact_handler, pattern="^vc_contact_"))
    application.add_handler(CallbackQueryHandler(multipack_callback_handler, pattern="^multipack_"))
    application.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(submit_proof_callback, pattern="^submit_proof_"))
    application.add_handler(CallbackQueryHandler(admin_action_callback, pattern="^admin_"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
