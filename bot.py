import os
import time
import logging
import random
import sqlite3
import io
import qrcode
from datetime import datetime
import pytz
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION & ENVIRONMENT VARIABLES ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS_RAW = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

if not BOT_TOKEN or not ADMIN_IDS:
    logger.warning("WARNING: BOT_TOKEN or ADMIN_IDS environment variables are not set properly!")

IST = pytz.timezone("Asia/Kolkata")
PROMO_COOLDOWN_SECONDS = 600  # 10 minutes

# --- PLACEHOLDER URLS & CONFIGURATIONS ---
START_IMAGE = "https://i.ibb.co/Fb6S1mYg/course1.jpg"
MAIN_WELCOME_IMAGE = "https://i.ibb.co/Fb6S1mYg/course1.jpg"
DEFAULT_UPI = "haaland78@ybl"
DEFAULT_PROOF_URL = "https://t.me/placeholder_proof"
DEFAULT_SUPPORT_URL = "https://t.me/placeholder_support"
DEFAULT_RATING_MSG = (
    "🌟 **Why Trust Us? / हमारी विश्वसनीयता**\n\n"
    "1. **Verified Deliveries:** Over 10,000+ successful digital product deliveries.\n\n"
    "2. **Instant Support:** Our support team is active 24/7 to resolve any issues.\n\n"
    "3. **Secure Payments:** Direct UPI verification with strict safety protocols.\n\n"
    "4. **Transparent Proofs:** Check our proof channel for real customer reviews!"
)

# --- PLANS CONFIGURATION (EDIT TITLE, PRICE, DEMOS, LINKS HERE) ---
PLANS_DATA = {
    "plan_1": {
        "id": 1,
        "name": "Ultimate Masterclass Pack 1",
        "number_of_videos": "50000+",
        "price": 49,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4",
            "https://videotourl.com/videos/1791607674607-203922d8-e261-4085-90fc-4be2fd62a6fb.mp4",
            "https://videotourl.com/videos/1791607662133-116f8c11-861a-4d4c-94a4-411fbd79a4f4.mp4",
            "https://videotourl.com/videos/1791607553470-a87b7709-29e5-449b-89d2-49ce97c8e367.mp4",
            "https://videotourl.com/videos/1791607607288-b1cc3341-7d49-473e-8544-840992806dab.mp4",
            "https://videotourl.com/videos/1791607585444-8a7d8e39-2917-4d23-949e-c048fcbacb2f.mp4",
            "https://videotourl.com/videos/1791607617748-9c8da0dd-313e-4a4d-862b-7ccf034383b7.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_1"
    },
    "plan_2": {
        "id": 2,
        "name": "Exclusive Video Bundle 2",
        "number_of_videos": "45000+",
        "price": 49,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/ZRqKVvRQ/course2.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791609530271-d1845e11-78bd-4465-a0e3-3e0dd57fb424.mp4",
            "https://videotourl.com/videos/1791610410648-c50ab2d2-b1b2-4998-8f5f-43a5f719b603.mp4",
            "https://videotourl.com/videos/1791609652325-1646ca32-e73f-4a5a-9874-a0f4e401c6bb.mp4",
            "https://videotourl.com/videos/1791609624603-358124e2-dbc4-43b2-9772-e18c1df57397.mp4",
            "https://videotourl.com/videos/1791609569957-a7ce2e8a-e185-4dc6-893c-298a2d9c1b4c.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_2"
    },
    "plan_3": {
        "id": 3,
        "name": "Premium Creator Pack 3",
        "number_of_videos": "70000+",
        "price": 49,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/21H7BGM2/course3.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791598226633-9d219b40-bf0b-4774-b493-6449c47d5ef1.mp4",
            "https://videotourl.com/videos/1791598035486-79178a34-a631-49d2-870e-ff3425f1c058.mp4",
            "https://videotourl.com/videos/1791611314862-1e0e5b81-0a04-436a-9749-4f5e9115404f.mp4",
            "https://videotourl.com/videos/1791598059935-f6722923-e315-4b97-aaeb-e7b0af379f2b.mp4",
            "https://videotourl.com/videos/1791598126801-a117ace0-e399-46e6-b697-0d3da6efeedd.mp4",
            "https://videotourl.com/videos/1791598104865-7bca6c3f-db24-465d-9688-d153131af1e5.mp4",
            "https://videotourl.com/videos/1791598207010-15f8101c-d87e-4e83-bd6a-43a333204662.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_3"
    },
    "plan_4": {
        "id": 4,
        "name": "Pro Video Collection 4",
        "number_of_videos": "40000+",
        "price": 69,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/QF2v05qK/course4.jpg",
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
        ],
        "delivery_link": "https://t.me/+delivery_link_4"
    },
    "plan_5": {
        "id": 5,
        "name": "Advanced Media Pack 5",
        "number_of_videos": "30000+",
        "price": 58,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/5X0hc5dd/course5.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791609855846-9b6bac98-1fcf-4d60-b612-3e5abaf6be7e.mp4",
            "https://videotourl.com/videos/1791614058029-1220e2df-44c4-467d-bbd7-755af32ada0c.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_5"
    },
    "plan_6": {
        "id": 6,
        "name": "Starter Creators Pack 6",
        "number_of_videos": "56000+",
        "price": 39,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/HLw36KQ4/course6.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791611037316-4db456f2-f82c-4468-9f48-381341ed6e55.mp4",
            "https://videotourl.com/videos/1791611085614-c863517b-d989-4d6f-b6ef-d23db0b73f5a.mp4",
            "https://videotourl.com/videos/1791611220352-ba6538bc-4db1-401e-81f7-88c53824e27f.mp4",
            "https://videotourl.com/videos/1791609479203-02acf86c-6132-4bc2-8041-9f43ab529748.mp4",
            "https://videotourl.com/videos/1791611168222-86d679dd-8a24-46fb-8b06-d59cc97e84c2.mp4",
            "https://videotourl.com/videos/1791611005214-c25159ac-d514-4eff-8061-a25465ff6eba.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_6"
    },
    "plan_7": {
        "id": 7,
        "name": "Mega Creator Bundle 7",
        "number_of_videos": "67000+",
        "price": 49,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/9kKCd6ZF/course7.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "demo_videos": [
            "https://videotourl.com/videos/1791611423923-36dbbbf3-84c1-4754-a7e4-dc05798eaa03.mp4",
            "https://videotourl.com/videos/1791611350514-052fe889-5ac7-4446-91ef-2f928070e131.mp4",
            "https://videotourl.com/videos/1791609591492-b5b0f616-27c5-436f-9aa9-e70720337677.mp4",
            "https://videotourl.com/videos/1791609952353-7ee9382f-6db6-4c43-86ed-c8f418a3282c.mp4",
            "https://videotourl.com/videos/1791609450717-98fd3d4d-533c-46fc-a290-9f9f937b6721.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_7"
    },
    "plan_8": {
        "id": 8,
        "name": "Elite Video Library 8",
        "number_of_videos": "18000+",
        "price": 49,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/C5KZBm7f/course8.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍",
        "demo_videos": [
            "https://videotourl.com/videos/1791611713436-2f106a4b-9ee1-4d9b-8e06-c30a0fe309e7.mp4",
            "https://videotourl.com/videos/1791611779829-f05b75a9-65c7-441d-ad89-5d5f15301b01.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_8"
    },
    "plan_9": {
        "id": 9,
        "name": "Super Viral Pack 9",
        "number_of_videos": "70000+",
        "price": 69,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/qFhKnzcH/course9.jpg",
        "description": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙁𝙍𝙄𝘿𝘼𝙔 ✅.",
        "demo_videos": [
            "https://videotourl.com/videos/1791611593469-187437c5-8f84-41c6-afa1-3d61feb9ff72.mp4",
            "https://videotourl.com/videos/1791611552865-c2cf6f7d-1544-4c34-9bdb-5e5fb2092584.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_9"
    },
    "plan_10": {
        "id": 10,
        "name": "INSTAGRAM Pack 10",
        "number_of_videos": "50000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_10"
    },
    "plan_11": {
        "id": 11,
        "name": "INSTAGRAM Pack 11",
        "number_of_videos": "50000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_11"
    },
    "plan_12": {
        "id": 12,
        "name": "INSTAGRAM Pack 12",
        "number_of_videos": "50000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_12"
    },
    "plan_13": {
        "id": 13,
        "name": "INSTAGRAM Pack 13",
        "number_of_videos": "50000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_13"
    },
    "plan_14": {
        "id": 14,
        "name": "INSTAGRAM Pack 14",
        "number_of_videos": "50000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_14"
    },
    "plan_15": {
        "id": 15,
        "name": "INSTAGRAM Pack 15",
        "number_of_videos": "50000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_15"
    },
    "plan_16": {
        "id": 16,
        "name": "art",
        "number_of_videos": "58000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_16"
    },
    "plan_17": {
        "id": 17,
        "name": "INSTAGRAM Pack 17",
        "number_of_videos": "50000+",
        "price": 40,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [
            "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"
        ],
        "delivery_link": "https://t.me/+delivery_link_17"
    },
    "plan_18": {
        "id": 18,
        "name": "Multiple Plan Bundle (Any 4)",
        "number_of_videos": "60",
        "price": 120,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "Choose any 4 plans priced at ₹50 or less! Select 4 items to continue.",
        "demo_videos": [],
        "delivery_link": "https://t.me/+delivery_link_18"
    },
    "plan_19": {
        "id": 19,
        "name": "Direct Access Link",
        "number_of_videos": "1",
        "price": 50,
        "validity": "180 days",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "Direct link delivery package.",
        "demo_videos": [],
        "delivery_link": "https://t.me/+delivery_link_19"
    },
    "plan_20": {
        "id": 20,
        "name": "All VIP Lifetime Pack",
        "number_of_videos": "500000+",
        "price": 499,
        "validity": "Lifetime",
        "image_url": "https://i.ibb.co/Fb6S1mYg/course1.jpg",
        "description": "1. YOU CAN SAVE IN GALLERY ✅\n2. NO ANY ADS ❌\n3. HIGH QUALITY VIDEOS 😍\n4. NEW VIDEOS UPLOADED EVERY SUNDAY ✅\n5. High quality and new videos best in telegram",
        "demo_videos": [],
        "delivery_link": "https://t.me/+delivery_link_20"
    }
}


# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            platform TEXT,
            registered_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan_id TEXT PRIMARY KEY,
            name TEXT,
            price REAL,
            videos TEXT,
            validity TEXT,
            image_url TEXT,
            caption TEXT,
            demo_urls TEXT,
            delivery_link TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_id TEXT,
            amount REAL,
            screenshot_file_id TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()

    defaults = {
        "upi_id": DEFAULT_UPI,
        "proof_url": DEFAULT_PROOF_URL,
        "support_url": DEFAULT_SUPPORT_URL,
        "rating_msg": DEFAULT_RATING_MSG,
        "last_promo_ts": "0"
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    for pid, pdata in PLANS_DATA.items():
        demos_str = ",".join(pdata.get("demo_videos", []))
        cursor.execute("""
            INSERT OR REPLACE INTO plans (plan_id, name, price, videos, validity, image_url, caption, demo_urls, delivery_link, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            pid,
            pdata["name"],
            pdata["price"],
            pdata["number_of_videos"],
            pdata["validity"],
            pdata["image_url"],
            pdata["description"],
            demos_str,
            pdata["delivery_link"]
        ))

    conn.commit()
    conn.close()


init_db()


def get_plan_info(plan_num_or_id):
    pid = str(plan_num_or_id)
    if not pid.startswith("plan_"):
        pid = f"plan_{pid}"

    if pid in PLANS_DATA:
        return PLANS_DATA[pid]

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT plan_id, name, price, videos, validity, image_url, caption, demo_urls, delivery_link FROM plans WHERE plan_id=?",
        (pid,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    demos = [u.strip() for u in (row[7] or "").split(",") if u.strip()]
    return {
        "id": row[0],
        "name": row[1],
        "price": row[2],
        "number_of_videos": row[3],
        "validity": row[4],
        "image_url": row[5],
        "description": row[6],
        "demo_videos": demos,
        "delivery_link": row[8],
    }


def format_price(price):
    try:
        val = float(price)
        return str(int(val)) if val.is_integer() else f"{val:g}"
    except Exception:
        return str(price)


def format_plan_button_text(pdata):
    return f"{pdata['name']} • ₹{format_price(pdata['price'])}"


def format_buy_button_text(pdata):
    return f"Buy {pdata['name']} • ₹{format_price(pdata['price'])}"


def get_setting(key):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""


def update_setting(key, value):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


def generate_upi_qr(upi_id, payee_name, amount, transaction_note="Digital Purchase"):
    upi_url = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount}&cu=INR&tn={transaction_note}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    bio.name = "upi_qr.png"
    img.save(bio, "PNG")
    bio.seek(0)
    return bio


# --- BUTTON FACTORY (SAFE COLOR STYLING VIA api_kwargs) ---
def make_button(text, callback_data=None, url=None, style=None):
    kwargs = {}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if style:
        kwargs["api_kwargs"] = {"style": style}
    return InlineKeyboardButton(text, **kwargs)


# --- CLEAN BOT MESSAGE HELPER (NEVER DELETES USER MESSAGES) ---
async def safe_delete_bot_message(message):
    if not message:
        return
    try:
        await message.delete()
    except Exception:
        pass


async def send_age_gate_screen(context: ContextTypes.DEFAULT_TYPE, chat_id: int, first_name: str):
    caption = (
        f"👋 **Welcome, {first_name}!**\n\n"
        f"Please confirm your age to continue:"
    )
    keyboard = [
        [
            make_button("𝙔𝙀𝙎 𝙄 𝘼𝙈 18+ ✅", callback_data="start", style="success"),
            make_button("𝙄 𝘼𝙈 𝙉𝙊𝙏 18+ ❌", callback_data="exit", style="danger")
        ]
    ]
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


async def send_platform_screen(context: ContextTypes.DEFAULT_TYPE, chat_id: int, first_name: str):
    caption = (
        f"👋 **Welcome, {first_name}!**\n\n"
        f"Which platform are you joining us from?"
    )
    keyboard = [
        [
            make_button("Instagram", callback_data="platform_instagram", style="primary"),
            make_button("Facebook", callback_data="platform_facebook", style="danger")
        ]
    ]
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


# --- START & AGE GATE COMMAND ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO users (user_id, username, first_name, platform, registered_at)
        VALUES (
            ?, ?, ?,
            COALESCE((SELECT platform FROM users WHERE user_id=?), 'PENDING'),
            COALESCE((SELECT registered_at FROM users WHERE user_id=?), ?)
        )
        """,
        (user.id, user.username, user.first_name, user.id, user.id, datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    await send_age_gate_screen(context, update.effective_chat.id, user.first_name or "User")


async def handle_age_gate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    if data == "exit":
        await safe_delete_bot_message(query.message)
        text = (
            "🚫 **ACCESS DENIED**\n\n"
            "This bot is only for users **18+**.\n\n"
            "Tap below if you are 18+ or go back."
        )
        keyboard = [
            [make_button("𝙔𝙀𝙎 𝙄 𝘼𝙈 18+ ✅", callback_data="start", style="success")],
            [make_button("« Back", callback_data="back_to_start", style="primary")]
        ]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
    elif data == "start":
        await safe_delete_bot_message(query.message)
        await send_platform_screen(context, query.message.chat_id, user.first_name or "User")


async def handle_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    if data == "platform_facebook":
        await safe_delete_bot_message(query.message)
        text = (
            "🚫 **ACCESS DENIED**\n\n"
            "Sorry, this platform is currently not supported.\n\n"
            "Please select **Instagram** to continue."
        )
        keyboard = [[make_button("« Back", callback_data="start", style="primary")]]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
    elif data == "platform_instagram":
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET platform=?, username=?, first_name=? WHERE user_id=?",
            ("Instagram", user.username, user.first_name, user.id)
        )
        conn.commit()
        conn.close()
        await show_main_menu(query.message, delete_old=True)


def build_plans_only_keyboard():
    keyboard = []
    for i in range(1, 21):
        pdata = get_plan_info(i)
        if pdata:
            keyboard.append([make_button(format_plan_button_text(pdata), callback_data=f"plan_view_{i}", style="danger")])
    keyboard.append([make_button("« Back to Menu", callback_data="menu_main", style="primary")])
    return InlineKeyboardMarkup(keyboard)


async def send_plans_only(context: ContextTypes.DEFAULT_TYPE, chat_id: int, old_message=None):
    await safe_delete_bot_message(old_message)
    text = (
        "💎 **Available Plans**\n\n"
        "Select a plan below to view details and get instant access:"
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=build_plans_only_keyboard(),
        parse_mode="Markdown",
        protect_content=True
    )


async def show_main_menu(message, delete_old=False):
    chat_id = message.chat_id
    if delete_old:
        await safe_delete_bot_message(message)

    caption = (
        "🚀 **Welcome to the Ultimate Digital Products Hub**\n\n"
        "Explore premium video collections, custom bundles, and VIP access packs.\n\n"
        "✨ **Why Choose Us:**\n"
        "• 100% Secure & Verified Deliveries\n"
        "• Direct High-Speed Access & Gallery Save\n"
        "• Regular Weekly Updates\n\n"
        "👇 **Select a Plan or Watch a Demo Below:**"
    )

    keyboard = []
    for i in range(1, 21):
        pdata = get_plan_info(i)
        if pdata:
            keyboard.append([make_button(format_plan_button_text(pdata), callback_data=f"plan_view_{i}", style="danger")])

    keyboard.append([make_button("🎬 Demo", callback_data="menu_demo", style="primary")])

    keyboard.append([
        make_button("Proof", callback_data="menu_proof", style="success"),
        make_button("Support", callback_data="menu_support", style="danger")
    ])
    keyboard.append([
        make_button("Is This Bot Trusted?", callback_data="menu_trusted", style="danger"),
        make_button("How To Buy", callback_data="menu_howtobuy", style="primary")
    ])

    await message._bot.send_photo(
        chat_id=chat_id,
        photo=MAIN_WELCOME_IMAGE,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


# --- CASE INSENSITIVE DEMO TEXT HANDLER ---
async def handle_demo_text_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS and user_id in ADMIN_SESSIONS:
        return
    await show_main_demo_menu(context, update.effective_chat.id)


async def show_main_demo_menu(context: ContextTypes.DEFAULT_TYPE, chat_id: int, old_message=None):
    await safe_delete_bot_message(old_message)
    text = (
        "🎬 **Choose a Plan Demo to Explore**\n"
        "उस प्लान को चुनें जिसका आप डेमो देखना चाहते हैं:\n\n"
        "👇 Tap any plan below to preview:"
    )
    keyboard = []
    for i in range(1, 21):
        if i in [18, 19, 20]:
            continue
        pdata = get_plan_info(i)
        if pdata:
            keyboard.append([make_button(f"🎬 {pdata['name']} Demo", callback_data=f"demo_run_{i}", style="primary")])
    keyboard.append([make_button("« Back to Menu", callback_data="menu_main", style="primary")])

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


async def handle_plan_routing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data == "bcast_see_plans":
        await send_plans_only(context, chat_id, old_message=query.message)
        return

    if data == "bcast_free_demo":
        await show_main_demo_menu(context, chat_id, old_message=query.message)
        return

    if data == "back_to_start":
        await safe_delete_bot_message(query.message)
        await send_age_gate_screen(context, chat_id, query.from_user.first_name or "User")
        return

    if data == "menu_main":
        await show_main_menu(query.message, delete_old=True)
        return

    if data == "menu_proof":
        await safe_delete_bot_message(query.message)
        proof_url = get_setting("proof_url")
        keyboard = [[make_button("« Back to Menu", callback_data="menu_main", style="primary")]]
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📢 **Check Proofs Here / प्रूफ यहाँ देखें**\n\n{proof_url}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
        return

    if data == "menu_support":
        await safe_delete_bot_message(query.message)
        support_url = get_setting("support_url")
        keyboard = [[make_button("« Back to Menu", callback_data="menu_main", style="primary")]]
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"💬 **Customer Support / सहायता**\n\n{support_url}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
        return

    if data == "menu_trusted":
        await safe_delete_bot_message(query.message)
        rating_msg = get_setting("rating_msg")
        keyboard = [[make_button("« Back to Menu", callback_data="menu_main", style="primary")]]
        await context.bot.send_message(
            chat_id=chat_id,
            text=rating_msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
        return

    if data == "menu_howtobuy":
        await safe_delete_bot_message(query.message)
        guide = (
            "📖 **HOW TO PURCHASE / खरीदने का तरीका**\n\n"
            "**English:**\n"
            "1. Select your favourite plan.\n"
            "2. Watch its demo videos.\n"
            "3. If you like it, click Buy Now.\n"
            "4. Scan the QR code and pay.\n"
            "5. Click Submit Payment.\n"
            "6. Send your payment screenshot.\n"
            "7. Receive your access link within 5 minutes.\n\n"
            "**हिंदी:**\n"
            "1. सबसे पहले अपनी पसंद का प्लान चुनें।\n"
            "2. उस प्लान के डेमो देखें।\n"
            "3. पसंद आने पर Buy Now पर क्लिक करें।\n"
            "4. दिए गए QR Code को स्कैन करके पेमेंट करें।\n"
            "5. Submit Payment पर क्लिक करें।\n"
            "6. पेमेंट का स्क्रीनशॉट भेजें।\n"
            "7. 5 मिनट के भीतर बॉट के जरिए लिंक मिल जाएगा।"
        )
        keyboard = [[make_button("« Back to Menu", callback_data="menu_main", style="primary")]]
        await context.bot.send_message(
            chat_id=chat_id,
            text=guide,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
        return

    if data == "menu_demo":
        await show_main_demo_menu(context, chat_id, old_message=query.message)
        return

    if data.startswith("demo_run_"):
        plan_num = data.split("_")[2]
        await start_demo_sequence(query, plan_num, 0, context)
        return

    if data.startswith("demo_nav_"):
        parts = data.split("_")
        plan_num = parts[2]
        index = int(parts[3])
        await start_demo_sequence(query, plan_num, index, context)
        return

    if data.startswith("plan_view_"):
        plan_num = data.split("_")[2]
        if plan_num == "18":
            await show_plan_18(query, context)
        elif plan_num == "19":
            await show_plan_19(query, context)
        elif plan_num == "20":
            await show_plan_20(query, context)
        else:
            await show_standard_plan(query, plan_num, context)
        return

    if data.startswith("buy_plan_"):
        plan_id = data.split("_")[2]
        await initiate_payment(query, plan_id, context)
        return
    elif data.startswith("buy_"):
        plan_id = data.split("_")[1]
        await initiate_payment(query, plan_id, context)
        return

    if data.startswith("submit_pay_"):
        plan_id = data.split("_")[2]
        context.user_data["pending_plan_id"] = plan_id
        await safe_delete_bot_message(query.message)
        keyboard = [[make_button("« Back to Menu", callback_data="menu_main", style="primary")]]
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "📸 **Upload Payment Screenshot**\n\n"
                "Please send your payment screenshot now.\n"
                "कृपया अपने पेमेंट का स्क्रीनशॉट भेजें।"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
        return

    if data.startswith("p18_toggle_"):
        p_num = data.split("_")[2]
        await handle_bundle_toggle(query, p_num, context)
        return

    if data == "p18_checkout":
        await process_bundle_checkout(query, context)
        return

    if data == "demo_plan_20":
        await show_plan_20_demo(query, context)
        return


async def show_standard_plan(query, plan_num, context: ContextTypes.DEFAULT_TYPE):
    pdata = get_plan_info(plan_num)
    if not pdata:
        return
    await safe_delete_bot_message(query.message)
    delivery_time = random.randint(1, 4)

    caption = (
        f"📦 **Plan Details**\n\n"
        f"• **Name:** {pdata['name']}\n"
        f"• **Price:** ₹{format_price(pdata['price'])}\n"
        f"• **Videos:** {pdata['number_of_videos']}\n"
        f"• **Validity:** {pdata['validity']}\n"
        f"• **Delivery Time:** {delivery_time} minutes\n\n"
        f"✨ **Special Features:**\n{pdata['description']}"
    )

    keyboard = [
        [make_button(format_buy_button_text(pdata), callback_data=f"buy_plan_{plan_num}", style="success")],
        [make_button(f"🎬 {pdata['name']} Demo", callback_data=f"demo_run_{plan_num}", style="primary")],
        [make_button("« Back to Menu", callback_data="menu_main", style="primary")]
    ]
    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=pdata["image_url"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


async def start_demo_sequence(query, plan_num, index, context: ContextTypes.DEFAULT_TYPE):
    pdata = get_plan_info(plan_num)
    if not pdata:
        return
    await safe_delete_bot_message(query.message)
    demo_urls = pdata.get("demo_videos", [])

    if not demo_urls or index >= len(demo_urls):
        end_text = (
            f"🎬 **Demo Info**\n\n"
            f"Demo preview for **{pdata['name']}** has ended or has no extra clips.\n\n"
            f"Unlock **{pdata['name']}** ({pdata['number_of_videos']} videos) for just **₹{format_price(pdata['price'])}**."
        )
        keyboard = [
            [make_button(format_buy_button_text(pdata), callback_data=f"buy_plan_{plan_num}", style="success")],
            [make_button(f"« Back to {pdata['name']}", callback_data=f"plan_view_{plan_num}", style="primary")]
        ]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=end_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
            protect_content=True
        )
        return

    current_video_url = demo_urls[index]
    nav_buttons = []
    if index > 0:
        nav_buttons.append(make_button("Previous Demo", callback_data=f"demo_nav_{plan_num}_{index-1}", style="primary"))
    nav_buttons.append(make_button("Next Demo", callback_data=f"demo_nav_{plan_num}_{index+1}", style="primary"))

    keyboard = [
        nav_buttons,
        [make_button(f"« Back to {pdata['name']}", callback_data=f"plan_view_{plan_num}", style="primary")]
    ]

    await context.bot.send_video(
        chat_id=query.message.chat_id,
        video=current_video_url,
        caption=f"🎬 **{pdata['name']} Demo ({index+1}/{len(demo_urls)})**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


# --- PLAN 18 (BUNDLE SELECTOR STRICTLY ≤ ₹50 ONLY) ---
BUNDLE_STATE = {}


async def show_plan_18(query, context: ContextTypes.DEFAULT_TYPE):
    pdata18 = get_plan_info(18)
    user_id = query.from_user.id
    BUNDLE_STATE[user_id] = set()
    await safe_delete_bot_message(query.message)
    caption = (
        f"🎁 **{pdata18['name']} • ₹{format_price(pdata18['price'])}**\n\n"
        f"Select 4 plans priced at ₹50 or less below.\n\n"
        f"**Selected:** 0/4"
    )
    keyboard = build_bundle_keyboard(user_id)
    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=pdata18["image_url"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


def build_bundle_keyboard(user_id):
    pdata18 = get_plan_info(18)
    bundle_price = format_price(pdata18["price"]) if pdata18 else "120"
    selected = BUNDLE_STATE.get(user_id, set())
    keyboard = []
    for i in range(1, 18):
        pdata = get_plan_info(i)
        if pdata and float(pdata["price"]) <= 50:
            status = "✅" if str(i) in selected else "➕"
            keyboard.append([
                make_button(
                    f"{format_plan_button_text(pdata)}  {status}",
                    callback_data=f"p18_toggle_{i}",
                    style="primary" if str(i) in selected else "danger"
                )
            ])

    if len(selected) == 4:
        keyboard.append([make_button(f"Continue to Payment (₹{bundle_price})", callback_data="p18_checkout", style="success")])
    else:
        keyboard.append([make_button(f"Selected: {len(selected)}/4 (Select 4)", callback_data="ignore", style="danger")])

    keyboard.append([make_button("« Back to Menu", callback_data="menu_main", style="primary")])
    return keyboard


async def handle_bundle_toggle(query, p_num, context: ContextTypes.DEFAULT_TYPE):
    pdata18 = get_plan_info(18)
    bundle_price = format_price(pdata18["price"]) if pdata18 else "120"
    user_id = query.from_user.id
    if user_id not in BUNDLE_STATE:
        BUNDLE_STATE[user_id] = set()

    if p_num in BUNDLE_STATE[user_id]:
        BUNDLE_STATE[user_id].remove(p_num)
    else:
        if len(BUNDLE_STATE[user_id]) >= 4:
            await query.answer("You can only select 4 plans!", show_alert=True)
            return
        BUNDLE_STATE[user_id].add(p_num)

    keyboard = build_bundle_keyboard(user_id)
    caption = (
        f"🎁 **{pdata18['name']} • ₹{bundle_price}**\n\n"
        f"Select 4 plans priced at ₹50 or less below.\n\n"
        f"**Selected:** {len(BUNDLE_STATE[user_id])}/4"
    )
    await query.message.edit_caption(caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def process_bundle_checkout(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    selected = BUNDLE_STATE.get(user_id, set())
    if len(selected) != 4:
        await query.answer("Please select 4 plans first!", show_alert=True)
        return
    fake_query = type("obj", (object,), {"from_user": query.from_user, "message": query.message})
    await initiate_payment(fake_query, "18", context)


# --- PLAN 19 (DIRECT URL SENDER) ---
async def show_plan_19(query, context: ContextTypes.DEFAULT_TYPE):
    pdata = get_plan_info(19)
    if not pdata:
        return
    await safe_delete_bot_message(query.message)
    delivery_url = pdata.get("delivery_link", "https://t.me/+default_link")
    caption = (
        f"📌 **{pdata['name']}**\n\n"
        f"• **Price:** ₹{format_price(pdata['price'])}\n"
        f"• **Direct Link:** {delivery_url}\n\n"
        f"Tap the button below to open your access link."
    )
    keyboard = [
        [make_button("Access Channel / Link", url=delivery_url, style="success")],
        [make_button("« Back to Menu", callback_data="menu_main", style="primary")]
    ]
    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=pdata.get("image_url", MAIN_WELCOME_IMAGE),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


# --- PLAN 20 (ALL VIP LIFETIME PACK & IMGBB ALBUM DEMO) ---
async def show_plan_20(query, context: ContextTypes.DEFAULT_TYPE):
    pdata = get_plan_info(20)
    if not pdata:
        return
    await safe_delete_bot_message(query.message)
    caption = (
        f"👑 **{pdata['name']}**\n\n"
        f"• **Price:** ₹{format_price(pdata['price'])}\n"
        f"• **Videos:** {pdata['number_of_videos']}\n"
        f"• **Validity:** {pdata['validity']}\n\n"
        f"✨ **Benefits:**\n{pdata['description']}"
    )
    keyboard = [
        [make_button(format_buy_button_text(pdata), callback_data="buy_plan_20", style="success")],
        [make_button(f"🎬 {pdata['name']} Demo", callback_data="demo_plan_20", style="primary")],
        [make_button("« Back to Menu", callback_data="menu_main", style="primary")]
    ]
    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=pdata["image_url"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


async def show_plan_20_demo(query, context: ContextTypes.DEFAULT_TYPE):
    pdata = get_plan_info(20)
    await safe_delete_bot_message(query.message)
    album = [
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample1.jpg", caption=f"👑 {pdata['name']} Preview (10 Photos Album)"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample2.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample3.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample4.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample5.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample6.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample7.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample8.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample9.jpg"),
        InputMediaPhoto(media="https://i.ibb.co/6y19mX1/sample10.jpg")
    ]
    await context.bot.send_media_group(chat_id=query.message.chat_id, media=album, protect_content=True)
    keyboard = [
        [make_button(format_buy_button_text(pdata), callback_data="buy_plan_20", style="success")],
        [make_button(f"« Back to {pdata['name']}", callback_data="plan_view_20", style="primary")]
    ]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"👆 Preview complete! Ready to unlock {pdata['name']}?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        protect_content=True
    )


# --- PAYMENT SYSTEM & SCREENSHOT VERIFICATION ---
async def initiate_payment(query, plan_id, context: ContextTypes.DEFAULT_TYPE):
    pdata = get_plan_info(plan_id)
    name = pdata["name"] if pdata else f"Plan {plan_id}"
    price = pdata["price"] if pdata else 100
    price_str = format_price(price)
    upi_id = get_setting("upi_id")
    await safe_delete_bot_message(query.message)

    qr_bio = generate_upi_qr(upi_id=upi_id, payee_name="Social Flux", amount=price_str, transaction_note=name)

    caption = (
        f"💳 **Payment Details / पेमेंट विवरण**\n\n"
        f"• **Plan:** {name}\n"
        f"• **Amount:** ₹{price_str}\n"
        f"• **UPI ID:** `{upi_id}`\n\n"
        f"📌 **How to Complete:**\n"
        f"1. Scan the QR code or pay to the UPI ID above.\n"
        f"2. Tap **Submit Payment** and send your screenshot."
    )

    keyboard = [
        [make_button("Submit Payment", callback_data=f"submit_pay_{plan_id}", style="success")],
        [make_button("« Back", callback_data=f"plan_view_{plan_id}", style="primary")]
    ]

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=qr_bio,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )


async def handle_screenshot_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    plan_id = context.user_data.get("pending_plan_id")
    if not plan_id:
        return

    context.user_data.pop("pending_plan_id", None)
    photo_file_id = update.message.photo[-1].file_id

    pdata = get_plan_info(plan_id)
    name = pdata["name"] if pdata else f"Plan {plan_id}"
    price = pdata["price"] if pdata else 100.0
    price_str = format_price(price)

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payments (user_id, plan_id, amount, screenshot_file_id, status, created_at)
        VALUES (?, ?, ?, ?, 'PENDING', ?)
    """, (user_id, str(plan_id), price, photo_file_id, datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")))
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()

    keyboard = [[make_button("« Back to Menu", callback_data="menu_main", style="primary")]]
    await update.message.reply_text(
        "✅ **Payment Submitted**\n\n"
        "Please wait 5–10 minutes while we verify your payment.\n"
        "कृपया 5–10 मिनट इंतज़ार करें, पेमेंट वेरीफाई किया जा रहा है।",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        protect_content=True
    )

    user = update.effective_user
    username_str = f"@{user.username}" if user.username else "@NA"
    admin_caption = (
        f"🚨 **NEW PAYMENT REQUEST**\n\n"
        f"• **Plan Name:** {name}\n"
        f"• **User Name:** {username_str}\n"
        f"• **User ID:** `{user.id}`\n"
        f"• **Price:** ₹{price_str}"
    )
    admin_keyboard = [
        [
            make_button("Approve", callback_data=f"adm_approve_{payment_id}", style="success"),
            make_button("Reject", callback_data=f"adm_reject_{payment_id}", style="danger")
        ]
    ]

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo_file_id,
                caption=admin_caption,
                reply_markup=InlineKeyboardMarkup(admin_keyboard),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


# --- ADMIN PAYMENT APPROVAL & PUBLIC BROADCAST ---
async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    action = parts[1]
    payment_id = parts[2]

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, plan_id, status, amount, screenshot_file_id, created_at FROM payments WHERE payment_id=?",
        (payment_id,)
    )
    pay_row = cursor.fetchone()

    if not pay_row:
        conn.close()
        await query.edit_message_caption(caption="Payment record not found.")
        return

    user_id, plan_id, status, amount, screenshot_file_id, created_at = pay_row
    if status != "PENDING":
        conn.close()
        await query.edit_message_caption(caption=f"Payment already processed ({status}).")
        return

    pdata = get_plan_info(plan_id)
    plan_name = pdata["name"] if pdata else "Premium Plan"
    delivery_link = pdata["delivery_link"] if pdata else "https://t.me/+default_link"
    price_str = format_price(pdata["price"] if pdata else amount)

    if action == "approve":
        cursor.execute("UPDATE payments SET status='APPROVED' WHERE payment_id=?", (payment_id,))
        cursor.execute("SELECT user_id FROM users")
        all_users = cursor.fetchall()
        conn.commit()
        conn.close()

        await query.edit_message_caption(caption=f"✅ Approved for {plan_name} (User ID: {user_id})")

        user_keyboard = [[make_button("JOIN YOUR CHANNEL", url=delivery_link, style="success")]]
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🎉 **Congratulations!**\n\n"
                    "Your payment has been approved and your access is ready.\n\n"
                    "Tap the button below to join your channel:"
                ),
                reply_markup=InlineKeyboardMarkup(user_keyboard),
                parse_mode="Markdown",
                protect_content=True
            )
        except Exception as e:
            logger.error(f"Failed to send delivery link to user {user_id}: {e}")

        public_caption = (
            f"🎉 **OUR NEW USER PURCHASED A PLAN**\n\n"
            f"• **Plan Name:** {plan_name}\n"
            f"• **Price:** ₹{price_str}\n"
            f"• **Date & Time:** {created_at} IST\n"
            f"• **Status:** Purchased ✅"
        )
        broadcast_buttons = InlineKeyboardMarkup([
            [
                make_button("See Plans", callback_data="bcast_see_plans", style="success"),
                make_button("Free Demo", callback_data="bcast_free_demo", style="primary")
            ]
        ])

        for (uid,) in all_users:
            try:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=screenshot_file_id,
                    caption=public_caption,
                    reply_markup=broadcast_buttons,
                    parse_mode="Markdown",
                    protect_content=True
                )
            except Exception:
                pass

    elif action == "reject":
        cursor.execute("UPDATE payments SET status='REJECTED' WHERE payment_id=?", (payment_id,))
        conn.commit()
        conn.close()

        await query.edit_message_caption(caption=f"❌ Rejected for {plan_name} (User ID: {user_id})")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "❌ **Payment Not Verified**\n\n"
                    "Your payment could not be verified. Please contact support for assistance."
                ),
                parse_mode="Markdown",
                protect_content=True
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")


# --- ADMIN PANEL, DEPLOY PROMO & BROADCAST ---
ADMIN_SESSIONS = {}


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized access.")
        return

    keyboard = [
        [
            make_button("Change UPI", callback_data="adm_set_upi", style="primary"),
            make_button("Set Rating Message", callback_data="adm_set_rating", style="primary")
        ],
        [
            make_button("Today's Revenue", callback_data="adm_revenue", style="success"),
            make_button("Broadcast", callback_data="adm_broadcast", style="danger")
        ],
        [make_button("🚀 Deploy Promo", callback_data="adm_deploy_promo", style="success")],
        [make_button("« Back to Main Menu", callback_data="menu_main", style="primary")]
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⚙️ **Admin Dashboard**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def handle_admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        return

    data = query.data
    if data == "adm_revenue":
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        today_date = datetime.now(IST).strftime("%Y-%m-%d")

        cursor.execute("SELECT SUM(amount) FROM payments WHERE status='APPROVED' AND created_at LIKE ?", (f"{today_date}%",))
        rev = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT COUNT(*) FROM payments WHERE status='APPROVED'")
        app_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM payments WHERE status='PENDING'")
        pend_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM payments WHERE status='REJECTED'")
        rej_count = cursor.fetchone()[0]
        conn.close()

        report = (
            f"📊 **Today's Revenue Report**\n"
            f"Date: {today_date} (Asia/Kolkata)\n\n"
            f"• **Today's Revenue:** ₹{format_price(rev)}\n"
            f"• **Total Approved Payments:** {app_count}\n"
            f"• **Pending Payments:** {pend_count}\n"
            f"• **Rejected Payments:** {rej_count}"
        )
        await query.answer()
        await query.message.reply_text(report, parse_mode="Markdown")

    elif data == "adm_deploy_promo":
        now_ts = int(time.time())
        last_ts = int(float(get_setting("last_promo_ts") or "0"))
        elapsed = now_ts - last_ts

        if elapsed < PROMO_COOLDOWN_SECONDS:
            await query.answer("Function on cooldown, try after 10 min", show_alert=True)
            await query.message.reply_text("⏳ Function on cooldown, try after 10 min")
            return

        update_setting("last_promo_ts", str(now_ts))
        await query.answer("Deploying promo to all users...")

        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name FROM users")
        all_users = cursor.fetchall()
        conn.close()

        sent_count = 0
        skipped_count = 0
        promo_keyboard = InlineKeyboardMarkup([
            [make_button("See Plans", callback_data="bcast_see_plans", style="success")]
        ])

        for uid, fname in all_users:
            safe_name = fname if fname else "Dost"
            promo_text = (
                f"suno {safe_name} abhi tak tumne premium ka maja nai liya hai aur abhi offer chal rha hai to price kam hai bad me bardh sakte hai to abhi lo aur maje kro 💗😁\n\n"
                f"hamare bot ke fayde 👇\n"
                f"1. 100 percent trusted bot ✅\n"
                f"2. 24/7 support milega 📞\n"
                f"3. high quality and fresh videos ✅\n"
                f"4. you can save in gallery ✅\n"
                f"5. no any chanel ban issue ✅\n\n"
                f"niche diye gaye plans se apna plan chuno aur pao turant access 🔥😘"
            )
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=promo_text,
                    reply_markup=promo_keyboard,
                    protect_content=True
                )
                sent_count += 1
            except Exception:
                skipped_count += 1

        await query.message.reply_text(
            f"🚀 **Promo Broadcast Finished**\n\n"
            f"• **Total Users:** {len(all_users)}\n"
            f"• **Delivered:** {sent_count}\n"
            f"• **Unavailable / Blocked:** {skipped_count}",
            parse_mode="Markdown"
        )

    elif data == "adm_set_upi":
        ADMIN_SESSIONS[user_id] = "waiting_upi"
        await query.answer()
        await query.message.reply_text("Please reply with the new UPI ID:")

    elif data == "adm_set_rating":
        ADMIN_SESSIONS[user_id] = "waiting_rating"
        await query.answer()
        await query.message.reply_text("Please reply with the new Trust / Rating message:")

    elif data == "adm_broadcast":
        ADMIN_SESSIONS[user_id] = "waiting_broadcast"
        await query.answer()
        await query.message.reply_text("Please send the message, photo, or media you want to broadcast to all users:")


async def handle_admin_text_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS or user_id not in ADMIN_SESSIONS:
        return

    state = ADMIN_SESSIONS.pop(user_id)

    if state == "waiting_upi":
        text = update.message.text.strip()
        update_setting("upi_id", text)
        await update.message.reply_text(f"✅ UPI ID successfully updated to: `{text}`", parse_mode="Markdown")

    elif state == "waiting_rating":
        text = update.message.text
        update_setting("rating_msg", text)
        await update.message.reply_text("✅ Trust / Rating message updated successfully!")

    elif state == "waiting_broadcast":
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        all_users = cursor.fetchall()
        conn.close()

        success = 0
        blocked = 0
        failed = 0
        total = len(all_users)

        status_msg = await update.message.reply_text(f"📢 Broadcast started to {total} users...")

        for (uid,) in all_users:
            try:
                await update.message.copy(chat_id=uid, protect_content=True)
                success += 1
            except Exception as e:
                err_str = str(e).lower()
                if "blocked" in err_str or "deactivated" in err_str:
                    blocked += 1
                else:
                    failed += 1

        await status_msg.edit_text(
            f"📢 **Broadcast Completed Report**\n\n"
            f"• **Total Users:** {total}\n"
            f"• **Successful Deliveries:** {success}\n"
            f"• **Blocked Bots:** {blocked}\n"
            f"• **Failed Deliveries:** {failed}",
            parse_mode="Markdown"
        )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_panel))

    application.add_handler(CallbackQueryHandler(handle_age_gate, pattern="^(start|exit)$"))
    application.add_handler(CallbackQueryHandler(handle_platform, pattern="^platform_"))
    application.add_handler(CallbackQueryHandler(handle_plan_routing, pattern="^(back_to_start|menu_|plan_view_|demo_|buy_|p18_|submit_pay_|bcast_)"))
    application.add_handler(CallbackQueryHandler(handle_admin_action, pattern="^adm_(approve|reject)_"))
    application.add_handler(CallbackQueryHandler(handle_admin_callbacks, pattern="^adm_"))

    # Case-insensitive DEMO / demo / Demo keyword handler
    application.add_handler(
        MessageHandler(
            filters.PHOTO & ~filters.COMMAND,
            handle_screenshot_upload
        )
    )

    application.add_handler(
        MessageHandler(
            (
                filters.TEXT
                | filters.PHOTO
                | filters.VIDEO
                | filters.ATTACHMENT
            )
            & ~filters.COMMAND
            & filters.User(user_id=ADMIN_IDS),
            handle_admin_text_inputs
        )
    )

    logger.info("Bot started successfully...")
    application.run_polling()


if __name__ == "__main__":
    main()
