# ============================================================
#   🔶 NUMBER PANEL PRO BOT — ULTRA EDITION 🔶
#   Telegram OTP Number, 2FA, Profile, Refer, Withdraw, Admin
#   Modified & Enhanced Build
# ============================================================

import asyncio
import io
import re
import json
import html
import os
import time
import secrets
import string
import logging
from datetime import datetime, timedelta
from collections import defaultdict

import httpx
import pyotp

from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)
from telegram.constants import ParseMode, ChatAction

# ============================================================
#                  ⚙️ CONFIG SECTION ⚙️
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8969155153:AAH0QdU5YFo7_UYoJfEjBHK-6pORFi7Onz4")
ADMIN_ID  = int(os.environ.get("ADMIN_ID", 8361587941))                                     # আপনার আসল টেলিগ্রাম numeric ID
ADMINS    = [ADMIN_ID]                                     # একাধিক অ্যাডমিন দিতে চাইলে এখানে যোগ করুন
BOT_USERNAME = "@OTP_Code_Penel_Bot"                         # এই বটের username
SOURCE_BOT_USERNAME = "@OTP_Code_Penel_Bot"                  # যে বট থেকে নম্বর/OTP আসবে
API_KEY   = os.environ.get("API_KEY", "MURAD_7431E56C7564E91505723DA4")               # আগের ফাইলের API key রাখা হয়েছে
BASE_URL  = os.environ.get("BASE_URL", "https://fastxotp.com/@Access/@Bot/3oo9/@public")

# Data files
USER_DATA_FILE       = "users.json"
PAID_SMS_FILE        = "paid_sms.json"
STATS_FILE           = "user_stats.json"
REFERRAL_DATA_FILE   = "referral_data.json"
BANNED_USERS_FILE    = "banned_users.json"
WITHDRAW_DATA_FILE   = "withdraw_requests.json"
ACTIVITY_LOGS_FILE   = "activity_logs.json"
DATA_RANGE_FILE      = "datarange.json"
WITHDRAW_HISTORY_FILE = "withdraw_history.json"

# Pricing & limits
OTP_RATE          = 0.20          # <-- প্রতি OTP-তে কত টাকা রিওয়ার্ড
REFERRAL_PRICE    = 0.00          # <-- রেফার করলে কত টাকা
MIN_WITHDRAW      = 50           # <-- সর্বনিম্ন উইথড্র (BDT)
MAX_WITHDRAW      = 10000        # <-- সর্বোচ্চ উইথড্র (BDT)
DAILY_EARNING_CAP = 0            # <-- 0 মানে আনলিমিটেড

# Channel / Support / Force Join
SUPPORT_LINK    = "https://t.me/otp_groupe"
DEVELOPER_LINK  = "https://t.me/Shakil_X9"

# Force-join চ্যানেলগুলো (@otp_groupe এবং @Shakil_X9X)
REQUIRED_CHANNELS = [
    {"username": "@otp_groupe", "name": "OTP GROUP",            "url": "https://t.me/otp_groupe"},
    {"username": "@Shakil_X9X", "name": "🌐🚀𝗦𝗵𝗮𝗸𝗶𝗹® 𝗗𝗲𝘃𝗛𝘂𝗯💻",  "url": "https://t.me/Shakil_X9X"},
]

# OTP ফরওয়ার্ডিং গ্রুপ আইডি — @otp_groupe (এখানে number/OTP forward হবে)
OTP_GROUP_ID    = -1004390552014

# ডিফল্ট চ্যানেল লিংক (ব্রডকাস্ট বাটন ইত্যাদিতে)
CHANNEL_LINK    = "https://t.me/otp_groupe"

# ============================================================
#                  🎨 COLOR THEME 🎨
# ============================================================
ACCENT   = "🟡"   # Gold accent — বটের মূল রঙ
SUCCESS  = "🟢"
DANGER   = "🔴"
WARNING  = "🟠"
INFO     = "🔵"
NEUTRAL  = "⚪"

# ============================================================
#                  🌍 LANGUAGE TEXTS 🌍
# ============================================================
LANG_TEXTS = {
    "en": {
        # Main
        "welcome": (
            "💎 <b>[ ACCESS GRANTED ]</b> 💎\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 Connection Status: <code>SECURE</code>\n"
            f"🛰️ Telemetry Engine: <code>v21.0-PRO</code>\n"
            f"⚙️ Decryption Protocol: <code>ACTIVE</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 Choose a service to begin:"
        ),
        # Buttons
        "btn_get_num": "📲 GET NUMBER",
        "btn_search_otp": "🔎 SEARCH OTP",
        "btn_2fa": "🔑 GET 2FA",
        "btn_balance": "🪙 BALANCE",
        "btn_refer": "👥 REFER & EARN",
        "btn_profile": "👑 PROFILE",
        "btn_history": "📜 HISTORY",
        "btn_leaderboard": "🏆 LEADERBOARD",
        "btn_support": "💬 SUPPORT",
        "btn_lang": "🌐 LANGUAGE",
        "btn_admin": "⚙️ ADMIN PANEL ⚙️",
        "banned": f"{DANGER} <b>YOU ARE BANNED!</b>",
        # Prompts
        "join_prompt": (
            f"🔔 <b>Official Channel Subscription</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Please join our official channel to use bot services safely."
        ),
        "btn_join": "🔔 Join Channel",
        "btn_continue": "❇️ Continue",
        # Profile
        "profile_title": "👑 <b>USER PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━",
        # Balance / Withdraw
        "balance_title": (
            f"{ACCENT} <b>BALANCE WALLET</b> {ACCENT}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💵 Available Funds: <code>{{bal}} BDT</code>"
        ),
        "btn_withdraw": "💳 WITHDRAW",
        "withdraw_min_err": (
            f"<blockquote>{ACCENT} Current Balance: <code>{{bal}} BDT</code>\n"
            f"📉 Minimum withdrawal: <code>{{min_val}} BDT</code></blockquote>"
        ),
        "withdraw_method_prompt": "💳 Select your payment gateway:",
        "withdraw_amount_prompt": f"{ACCENT} Enter withdrawal amount (Min: {{min_val}} BDT):",
        "withdraw_number_prompt": "📲 Send your receiving number (Format: 017XXXXXXXX):",
        "withdraw_proposed": (
            f"✨ <b>WITHDRAWAL DETAILS</b> ✨\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>💳 Gateway: <code>{method}</code>\n"
            "📲 Number: <code>{num}</code>\n"
            f"{ACCENT} Amount: <code>{{amount}} BDT</code></blockquote>\n\n"
            "Confirm to proceed."
        ),
        # OTP search
        "search_otp_prompt": "🔎 <b>Enter the number to search OTP:</b>",
        "search_otp_searching": "🔎 Searching database, please wait...",
        "search_otp_not_found": (
            f"{DANGER} <b>NO OTP FOUND</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📟 Number: <code>+{num}</code>\n"
            "⏳ No active session detected."
        ),
        # 2FA
        "get_2fa_prompt": "🔑 <b>Send your 2FA Secret Key:</b>",
        "2fa_invalid": f"{DANGER} <b>INVALID SECRET KEY</b>\n\nPlease check and try again.",
        # Get Number
        "node_alloc_fail": f"{DANGER} <b>NO NUMBERS AVAILABLE</b>\n\nTry a different range/service.",
        "get_active_node": (
            f"📲 <b>[ GET NUMBER ]</b>\n\n"
            "🎯 Select a service:"
        ),
        "pick_country": (
            f"📲 <b>[ GET NUMBER ]</b>\n\n"
            "🎯 Service: <b>{sid}</b>\n"
            "🌍 Select country / range:"
        ),
        "custom_range_prompt": (
            f"{ACCENT} <b>[ CUSTOM RANGE ]</b>\n\n"
            "Enter custom range (e.g.: 237XXX):"
        ),
        "invalid_range": (
            f"{DANGER} <b>INVALID RANGE!</b>\n"
            "Example: <code>237XXX</code>"
        ),
        # Generic
        "cancel": f"{DANGER} OPERATION CANCELLED",
        "error_generic": f"{DANGER} Something went wrong. Try again later.",
    },
    "bn": {
        "welcome": (
            "💎 <b>[ অ্যাক্সেস সফল ]</b> 💎\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 সংযোগ: <code>সক্রিয়</code>\n"
            "🛰️ ইঞ্জিন: <code>v21.0-PRO</code>\n"
            "⚙️ প্রোটোকল: <code>চলমান</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 নিচ থেকে সার্ভিস বাছাই করুন:"
        ),
        "btn_get_num": "📲 নম্বর নিন",
        "btn_search_otp": "🔎 ওটিপি খুঁজুন",
        "btn_2fa": "🔑 2FA কোড",
        "btn_balance": "🪙 ব্যালেন্স",
        "btn_refer": "👥 রেফার",
        "btn_profile": "👑 প্রোফাইল",
        "btn_history": "📜 ইতিহাস",
        "btn_leaderboard": "🏆 লিডারবোর্ড",
        "btn_support": "💬 সাপোর্ট",
        "btn_lang": "🌐 ভাষা",
        "btn_admin": "⚙️ অ্যাডমিন প্যানেল ⚙️",
        "banned": f"{DANGER} <b>আপনি ব্যান হয়েছেন!</b>",
        "join_prompt": (
            "🔔 <b>আপডেট চ্যানেলে যোগ দিন</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "বটের সার্ভিস ব্যবহার করতে অফিশিয়াল চ্যানেলে যোগ দিন।"
        ),
        "btn_join": "🔔 চ্যানেলে যোগ দিন",
        "btn_continue": "❇️ প্রবেশ করুন",
        "profile_title": "👑 <b>ইউজার প্রোফাইল</b>\n━━━━━━━━━━━━━━━━━━━━━━━━",
        "balance_title": (
            f"{ACCENT} <b>ওয়ালেট ব্যালেন্স</b> {ACCENT}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💵 মোট ব্যালেন্স: <code>{{bal}} BDT</code>"
        ),
        "btn_withdraw": "💸 উইথড্র",
        "withdraw_min_err": (
            f"<blockquote>{ACCENT} বর্তমান ব্যালেন্স: <code>{{bal}} BDT</code>\n"
            f"📉 সর্বনিম্ন উইথড্র: <code>{{min_val}} BDT</code></blockquote>"
        ),
        "withdraw_method_prompt": "💳 পেমেন্ট গেটওয়ে বাছাই করুন:",
        "withdraw_amount_prompt": f"{ACCENT} উইথড্র পরিমাণ লিখুন (সর্বনিম্ন: {{min_val}} BDT):",
        "withdraw_number_prompt": "📲 প্রাপক নম্বর দিন (যেমন: 017XXXXXXXX):",
        "withdraw_proposed": (
            "✨ <b>উইথড্র ডিটেইলস</b> ✨\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>💳 গেটওয়ে: <code>{method}</code>\n"
            "📲 নম্বর: <code>{num}</code>\n"
            f"{ACCENT} পরিমাণ: <code>{{amount}} BDT</code></blockquote>\n\n"
            "নিশ্চিত করতে কনফার্ম বাটন চাপুন।"
        ),
        "search_otp_prompt": "🔎 <b>ওটিপি খুঁজতে নম্বর দিন:</b>",
        "search_otp_searching": "🔎 ডেটাবেজ চেক হচ্ছে, অপেক্ষা করুন...",
        "search_otp_not_found": (
            f"{DANGER} <b>কোনো ওটিপি নেই</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📟 নম্বর: <code>+{num}</code>\n"
            "⏳ কোনো সক্রিয় ওটিপি পাওয়া যায়নি।"
        ),
        "get_2fa_prompt": "🔑 <b>আপনার 2FA সিক্রেট কী দিন:</b>",
        "2fa_invalid": f"{DANGER} <b>ভুল সিক্রেট কী!</b>\n\nআবার চেষ্টা করুন।",
        "node_alloc_fail": f"{DANGER} <b>নম্বর নেই</b>\n\nঅন্য রেঞ্জ বা সার্ভিস ব্যবহার করুন।",
        "get_active_node": "📲 <b>[ নম্বর নিন ]</b>\n\n🎯 সার্ভিস বাছাই করুন:",
        "pick_country": "📲 <b>[ নম্বর নিন ]</b>\n\n🎯 সার্ভিস: <b>{sid}</b>\n🌍 দেশ/রেঞ্জ বাছাই করুন:",
        "custom_range_prompt": f"{ACCENT} <b>[ কাস্টম রেঞ্জ ]</b>\n\nরেঞ্জ লিখুন (যেমন: 237XXX):",
        "invalid_range": f"{DANGER} <b>ভুল রেঞ্জ!</b>\nউদাহরণ: <code>237XXX</code>",
        "cancel": f"{DANGER} অপারেশন বাতিল",
        "error_generic": f"{DANGER} কিছু সমস্যা হয়েছে। পরে আবার চেষ্টা করুন।",
    }
}

# Button matchers (English + Bangla)
T_GET_NUM     = ["📲 GET NUMBER", "📲 নম্বর নিন"]
T_SEARCH_OTP  = ["🔎 SEARCH OTP", "🔎 ওটিপি খুঁজুন"]
T_2FA         = ["🔑 GET 2FA", "🔑 2FA কোড"]
T_BALANCE     = ["🪙 BALANCE", "🪙 ব্যালেন্স"]
T_REFER       = ["👥 REFER & EARN", "👥 রেফার"]
T_PROFILE     = ["👑 PROFILE", "👑 প্রোফাইল"]
T_HISTORY     = ["📜 HISTORY", "📜 ইতিহাস"]
T_LEADERBOARD = ["🏆 LEADERBOARD", "🏆 লিডারবোর্ড"]
T_SUPPORT     = ["💬 SUPPORT", "💬 সাপোর্ট"]
T_LANG        = ["🌐 LANGUAGE", "🌐 ভাষা"]
T_ADMIN       = ["⚙️ ADMIN PANEL ⚙️"]
T_CANCEL      = ["🛑 CANCEL", "🛑 বাতিল"]
T_BACK_MAIN   = ["⬅️ MAIN MENU"]

# ============================================================
#                  🌐 HTTP CLIENT & QUEUE 🌐
# ============================================================
request_queue = asyncio.Queue()
MAX_WORKERS = 200

client_async = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=3.0, read=10.0, write=5.0, pool=3.0),
    headers={"X-API-Key": API_KEY},
    limits=httpx.Limits(max_connections=500, max_keepalive_connections=200),
)

active_numbers = {}      # number -> {uid, range, ts, lang}
last_range = {}          # uid -> range_text
CHECK_INTERVAL = 1.5

# Live services cache
_liveaccess_cache = {"services": [], "ts": 0}
LIVEACCESS_REFRESH_INTERVAL = 25

# ============================================================
#                  📁 HELPERS / PERSISTENCE 📁
# ============================================================
def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        save_data({}, filename)
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

def is_admin(uid):
    return int(uid) in ADMINS

# === User DB ===
def get_user(uid):
    uid = str(uid)
    data = load_data(USER_DATA_FILE)
    if uid not in data:
        data[uid] = {
            "user_id": uid, "balance": 0.0,
            "total_numbers": 0, "referral_count": 0,
            "lang": None, "joined_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
        save_data(data, USER_DATA_FILE)
    elif "lang" not in data[uid]:
        data[uid]["lang"] = None
        save_data(data, USER_DATA_FILE)
    return data[uid]

def set_user_lang(uid, lang):
    uid = str(uid)
    data = load_data(USER_DATA_FILE)
    if uid in data:
        data[uid]["lang"] = lang
        save_data(data, USER_DATA_FILE)

def get_user_lang(uid):
    user = get_user(uid)
    return user.get("lang") or "en"

async def update_db_balance(uid, amount):
    uid = str(uid)
    data = load_data(USER_DATA_FILE)
    if uid in data:
        data[uid]["balance"] = round(float(data[uid].get("balance", 0)) + float(amount), 2)
        data[uid]["last_active"] = datetime.now().isoformat()
        save_data(data, USER_DATA_FILE)
        return data[uid]["balance"]
    return 0.0

def get_all_users():
    return list(load_data(USER_DATA_FILE).keys())

def user_exists(uid):
    return str(uid) in load_data(USER_DATA_FILE)

# === Ban DB ===
def load_banned():
    if not os.path.exists(BANNED_USERS_FILE):
        save_data([], BANNED_USERS_FILE)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned(lst): save_data(lst, BANNED_USERS_FILE)
def is_user_banned(uid): return str(uid) in load_banned()
def ban_user(uid):
    lst = load_banned()
    if str(uid) not in lst:
        lst.append(str(uid)); save_banned(lst); return True
    return False
def unban_user(uid):
    lst = load_banned()
    if str(uid) in lst:
        lst.remove(str(uid)); save_banned(lst); return True
    return False

# === Referral DB ===
def get_referral_count(uid):
    rd = load_data(REFERRAL_DATA_FILE)
    return rd.get(str(uid), {}).get("referral_count", 0)

def update_referral_count(uid, count):
    rd = load_data(REFERRAL_DATA_FILE)
    rd[str(uid)] = {"referral_count": count}
    save_data(rd, REFERRAL_DATA_FILE)

# === Range DB ===
def save_number_range_info(uid, number, range_text):
    db = load_data(DATA_RANGE_FILE)
    flag, name = get_country_info(number)
    db[normalize_number(number)] = {
        "user_id": str(uid),
        "number": f"+{normalize_number(number)}",
        "range": range_text,
        "country": f"{flag} {name}",
        "ts": datetime.now().isoformat()
    }
    save_data(db, DATA_RANGE_FILE)

# === Stats ===
def load_stats(): return load_data(STATS_FILE)
def save_stats(s): save_data(s, STATS_FILE)

def add_number_taken(uid, count=1):
    uid = str(uid); stats = load_stats()
    stats.setdefault(uid, {"numbers_taken": [], "otps_received": []})
    for _ in range(count):
        stats[uid]["numbers_taken"].append(datetime.now().isoformat())
    log_activity(uid, "NUMBER_TAKEN", {"count": count})
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid); stats = load_stats()
    stats.setdefault(uid, {"numbers_taken": [], "otps_received": []})
    stats[uid]["otps_received"].append(datetime.now().isoformat())
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid); s = load_stats().get(uid, {"numbers_taken":[], "otps_received":[]})
    today_mid = get_date_reset_time()
    last24 = datetime.now() - timedelta(hours=24)
    last7  = datetime.now() - timedelta(days=7)
    nt = s.get("numbers_taken", []); ot = s.get("otps_received", [])
    return {
        "total_numbers": len(nt), "total_otps": len(ot),
        "today_numbers": sum(1 for t in nt if datetime.fromisoformat(t) >= today_mid),
        "today_otps":   sum(1 for t in ot if datetime.fromisoformat(t) >= today_mid),
        "24h_numbers":   sum(1 for t in nt if datetime.fromisoformat(t) >  last24),
        "24h_otps":      sum(1 for t in ot if datetime.fromisoformat(t) >  last24),
        "7d_numbers":    sum(1 for t in nt if datetime.fromisoformat(t) >  last7),
        "7d_otps":       sum(1 for t in ot if datetime.fromisoformat(t) >  last7),
    }

def get_global_stats():
    stats = load_stats()
    now = datetime.now()
    today_mid = get_date_reset_time()
    last7 = now - timedelta(days=7)
    tn, to, sn, so, tot_n, tot_o = 0, 0, 0, 0, 0, 0
    for u in stats.values():
        nt = u.get("numbers_taken", []); ot = u.get("otps_received", [])
        tot_n += len(nt); tot_o += len(ot)
        for t in nt:
            d = datetime.fromisoformat(t)
            if d >= today_mid: tn += 1
            if d >= last7: sn += 1
        for t in ot:
            d = datetime.fromisoformat(t)
            if d >= today_mid: to += 1
            if d >= last7: so += 1
    return tn, to, sn, so, tot_n, tot_o

# === Activity log ===
def log_activity(uid, action, details):
    if not os.path.exists(ACTIVITY_LOGS_FILE):
        save_data([], ACTIVITY_LOGS_FILE)
    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    now = datetime.now()
    logs.append({
        "uid": str(uid), "action": action,
        "details": details, "timestamp": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"), "time": now.strftime("%H:%M:%S")
    })
    if len(logs) > 10000: logs = logs[-10000:]
    save_data(logs, ACTIVITY_LOGS_FILE)

# ============================================================
#                  🌍 COUNTRY / SERVICE MAPS 🌍
# ============================================================
COUNTRY_MAP = {
    "2376": ("🇨🇲","Cameroon"),"2250":("🇨🇮","Ivory Coast"),"2613":("🇲🇬","Madagascar"),
    "4077":("🇷🇴","Romania"),"237":("🇨🇲","Cameroon"),"225":("🇨🇮","Ivory Coast"),
    "261":("🇲🇬","Madagascar"),"20":("🇪🇬","Egypt"),"27":("🇿🇦","South Africa"),
    "234":("🇳🇬","Nigeria"),"254":("🇰🇪","Kenya"),"233":("🇬🇭","Ghana"),
    "212":("🇲🇦","Morocco"),"213":("🇩🇿","Algeria"),"216":("🇹🇳","Tunisia"),
    "218":("🇱🇾","Libya"),"249":("🇸🇩","Sudan"),"251":("🇪🇹","Ethiopia"),
    "252":("🇸🇴","Somalia"),"253":("🇩🇯","Djibouti"),"255":("🇹🇿","Tanzania"),
    "256":("🇺🇬","Uganda"),"257":("🇧🇮","Burundi"),"258":("🇲🇿","Mozambique"),
    "260":("🇿🇲","Zambia"),"263":("🇿🇼","Zimbabwe"),"264":("🇳🇦","Namibia"),
    "265":("🇲🇼","Malawi"),"266":("🇱🇸","Lesotho"),"267":("🇧🇼","Botswana"),
    "268":("🇸🇿","Eswatini"),"269":("🇰🇲","Comoros"),"220":("🇬🇲","Gambia"),
    "221":("🇸🇳","Senegal"),"222":("🇲🇷","Mauritania"),"223":("🇲🇱","Mali"),
    "224":("🇬🇳","Guinea"),"226":("🇧🇫","Burkina Faso"),"227":("🇳🇪","Niger"),
    "228":("🇹🇬","Togo"),"229":("🇧🇯","Benin"),"230":("🇲🇺","Mauritius"),
    "231":("🇱🇷","Liberia"),"232":("🇸🇱","Sierra Leone"),"235":("🇹🇩","Chad"),
    "236":("🇨🇫","Central African Republic"),"238":("🇨🇻","Cape Verde"),
    "239":("🇸🇹","Sao Tome"),"240":("🇬🇶","Equatorial Guinea"),"241":("🇬🇦","Gabon"),
    "242":("🇨🇬","Congo"),"243":("🇨🇩","DR Congo"),"244":("🇦🇴","Angola"),
    "245":("🇬🇼","Guinea-Bissau"),"247":("🇸🇭","Saint Helena"),"248":("🇸🇨","Seychelles"),
    "250":("🇷🇼","Rwanda"),"290":("🇸🇭","Saint Helena"),"291":("🇪🇷","Eritrea"),
    "40":("🇷🇴","Romania"),"44":("🇬🇧","United Kingdom"),"33":("🇫🇷","France"),
    "49":("🇩🇪","Germany"),"39":("🇮🇹","Italy"),"34":("🇪🇸","Spain"),
    "31":("🇳🇱","Netherlands"),"32":("🇧🇪","Belgium"),"41":("🇨🇭","Switzerland"),
    "43":("🇦🇹","Austria"),"46":("🇸🇪","Sweden"),"47":("🇳🇴","Norway"),
    "45":("🇩🇰","Denmark"),"358":("🇫🇮","Finland"),"351":("🇵🇹","Portugal"),
    "353":("🇮🇪","Ireland"),"36":("🇭🇺","Hungary"),"48":("🇵🇱","Poland"),
    "380":("🇺🇦","Ukraine"),"370":("🇱🇹","Lithuania"),"371":("🇱🇻","Latvia"),
    "372":("🇪🇪","Estonia"),"373":("🇲🇩","Moldova"),"374":("🇦🇲","Armenia"),
    "375":("🇧🇾","Belarus"),"376":("🇦🇩","Andorra"),"377":("🇲🇨","Monaco"),
    "381":("🇷🇸","Serbia"),"382":("🇲🇪","Montenegro"),"385":("🇭🇷","Croatia"),
    "386":("🇸🇮","Slovenia"),"387":("🇧🇦","Bosnia"),"389":("🇲🇰","North Macedonia"),
    "350":("🇬🇮","Gibraltar"),"352":("🇱🇺","Luxembourg"),"354":("🇮🇸","Iceland"),
    "355":("🇦🇱","Albania"),"356":("🇲🇹","Malta"),"357":("🇨🇾","Cyprus"),
    "359":("🇧🇬","Bulgaria"),"421":("🇸🇰","Slovakia"),"420":("🇨🇿","Czech Republic"),
    "298":("🇫🇴","Faroe Islands"),"299":("🇬🇱","Greenland"),"1":("🇺🇸","USA"),
    "7":("🇷🇺","Russia"),"91":("🇮🇳","India"),"92":("🇵🇰","Pakistan"),
    "880":("🇧🇩","Bangladesh"),"86":("🇨🇳","China"),"81":("🇯🇵","Japan"),
    "82":("🇰🇷","South Korea"),"84":("🇻🇳","Vietnam"),"66":("🇹🇭","Thailand"),
    "62":("🇮🇩","Indonesia"),"60":("🇲🇾","Malaysia"),"65":("🇸🇬","Singapore"),
    "63":("🇵🇭","Philippines"),"95":("🇲🇲","Myanmar"),"94":("🇱🇰","Sri Lanka"),
    "977":("🇳🇵","Nepal"),"93":("🇦🇫","Afghanistan"),"98":("🇮🇷","Iran"),
    "90":("🇹🇷","Turkey"),"964":("🇮🇶","Iraq"),"963":("🇸🇾","Syria"),
    "961":("🇱🇧","Lebanon"),"962":("🇯🇴","Jordan"),"965":("🇰🇼","Kuwait"),
    "966":("🇸🇦","Saudi Arabia"),"967":("🇾🇪","Yemen"),"968":("🇴🇲","Oman"),
    "971":("🇦🇪","UAE"),"972":("🇮🇱","Israel"),"973":("🇧🇭","Bahrain"),
    "974":("🇶🇦","Qatar"),"994":("🇦🇿","Azerbaijan"),"995":("🇬🇪","Georgia"),
    "996":("🇰🇬","Kyrgyzstan"),"992":("🇹🇯","Tajikistan"),"993":("🇹🇲","Turkmenistan"),
    "998":("🇺🇿","Uzbekistan"),"855":("🇰🇭","Cambodia"),"856":("🇱🇦","Laos"),
    "976":("🇲🇳","Mongolia"),"850":("🇰🇵","North Korea"),"55":("🇧🇷","Brazil"),
    "52":("🇲🇽","Mexico"),"54":("🇦🇷","Argentina"),"57":("🇨🇴","Colombia"),
    "51":("🇵🇪","Peru"),"58":("🇻🇪","Venezuela"),"56":("🇨🇱","Chile"),
    "593":("🇪🇨","Ecuador"),"591":("🇧🇴","Bolivia"),"595":("🇵🇾","Paraguay"),
    "598":("🇺🇾","Uruguay"),"502":("🇬🇹","Guatemala"),"503":("🇸🇻","El Salvador"),
    "504":("🇭🇳","Honduras"),"506":("🇨🇷","Costa Rica"),"507":("🇵🇦","Panama"),
    "509":("🇭🇹","Haiti"),"501":("🇧🇿","Belize"),"61":("🇦🇺","Australia"),
    "64":("🇳🇿","New Zealand"),"675":("🇵🇬","Papua New Guinea"),"679":("🇫🇯","Fiji"),
    "1246":("🇧🇧","Barbados"),"1876":("🇯🇲","Jamaica"),"53":("🇨🇺","Cuba"),
    "592":("🇬🇾","Guyana"),
}

def get_country_info(number):
    n = str(number).replace("+","").replace(" ","").replace("-","").strip()
    for p in sorted(COUNTRY_MAP.keys(), key=len, reverse=True):
        if n.startswith(p):
            return COUNTRY_MAP[p]
    return ("🌍","Unknown")

SERVICE_KEYWORDS = {
    "facebook":"FACEBOOK","fb":"FACEBOOK","instagram":"INSTAGRAM","insta":"INSTAGRAM",
    "tiktok":"TIKTOK","twitter":"TWITTER","x.com":"TWITTER","snapchat":"SNAPCHAT",
    "whatsapp":"WHATSAPP","telegram":"TELEGRAM","discord":"DISCORD","messenger":"MESSENGER",
    "linkedin":"LINKEDIN","google":"GOOGLE","gmail":"GOOGLE","amazon":"AMAZON",
    "microsoft":"MICROSOFT","outlook":"MICROSOFT","yahoo":"YAHOO","paypal":"PAYPAL",
    "binance":"BINANCE","coinbase":"COINBASE","spotify":"SPOTIFY","netflix":"NETFLIX",
    "uber":"UBER","apple":"APPLE","icloud":"APPLE","bkash":"BKASH","nagad":"NAGAD",
    "stripe":"STRIPE","line":"LINE","wechat":"WECHAT","viber":"VIBER","signal":"SIGNAL",
    "pubg":"PUBG","free fire":"FREE FIRE",
}
SERVICE_LOGOS = {
    "FACEBOOK":"🔵 FACEBOOK","INSTAGRAM":"📸 INSTAGRAM","TIKTOK":"🎵 TIKTOK",
    "TWITTER":"🐦 TWITTER","SNAPCHAT":"👻 SNAPCHAT","WHATSAPP":"🟢 WHATSAPP",
    "TELEGRAM":"✈️ TELEGRAM","DISCORD":"👾 DISCORD","MESSENGER":"💬 MESSENGER",
    "LINKEDIN":"💼 LINKEDIN","GOOGLE":"📨 GOOGLE","AMAZON":"🛒 AMAZON",
    "MICROSOFT":"💻 MICROSOFT","YAHOO":"🟣 YAHOO","PAYPAL":"💳 PAYPAL",
    "BINANCE":"🔶 BINANCE","COINBASE":"🔵 COINBASE","SPOTIFY":"🎧 SPOTIFY",
    "NETFLIX":"🎬 NETFLIX","UBER":"🚗 UBER","APPLE":"🍎 APPLE",
    "BKASH":"🌸 BKASH","NAGAD":"🍊 NAGAD","STRIPE":"💳 STRIPE",
    "LINE":"🟢 LINE","WECHAT":"💬 WECHAT","VIBER":"🟣 VIBER","SIGNAL":"💬 SIGNAL",
    "PUBG":"🎮 PUBG","FREE FIRE":"🔥 FREE FIRE",
}

def detect_service(text):
    if not text: return "SMS SERVICE"
    t = text.lower()
    for k, v in sorted(SERVICE_KEYWORDS.items(), key=lambda x: len(x[0]), reverse=True):
        if k in t: return v
    return "SMS SERVICE"

def get_service_logo(svc): return SERVICE_LOGOS.get(str(svc).upper(), "📩 SMS")

# ============================================================
#                  🔘 BUTTON BUILDERS 🔘
# ============================================================
def kb(text, style=None):
    try: return KeyboardButton(text=text, style=style)
    except TypeError: return KeyboardButton(text=text)

def ikb(text, callback_data=None, url=None, style=None):
    try:
        if url: return InlineKeyboardButton(text=text, url=url, style=style)
        return InlineKeyboardButton(text=text, callback_data=callback_data, style=style)
    except TypeError:
        if url: return InlineKeyboardButton(text=text, url=url)
        return InlineKeyboardButton(text=text, callback_data=callback_data)

# ============================================================
#                  🎛️ KEYBOARD LAYOUTS 🎛️
# ============================================================
def main_keyboard(uid):
    lang = get_user_lang(uid)
    t = LANG_TEXTS[lang]
    primary   = "primary" if lang == "en" else None
    success   = "success" if lang == "en" else None
    rows = [
        [kb(t["btn_get_num"], style=success)],
        [kb(t["btn_search_otp"], style=primary), kb(t["btn_2fa"], style=primary)],
        [kb(t["btn_balance"], style=primary),     kb(t["btn_history"], style=primary)],
        [kb(t["btn_refer"], style=primary),       kb(t["btn_profile"], style=primary)],
        [kb(t["btn_leaderboard"], style=success), kb(t["btn_support"], style=success)],
        [kb(t["btn_lang"], style=primary),        kb(t["btn_admin"] if is_admin(uid) else "📊 STATS", style="danger" if is_admin(uid) else None)],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def cancel_keyboard(uid):
    lang = get_user_lang(uid)
    btn = "🛑 CANCEL" if lang == "en" else "🛑 বাতিল"
    style = "danger" if lang == "en" else None
    return ReplyKeyboardMarkup([[kb(btn, style=style)]], resize_keyboard=True)

def admin_main_kb():
    return ReplyKeyboardMarkup([
        [kb("👥 USER MANAGEMENT", style="primary")],
        [kb("⚙️ SYSTEM CONFIGURATION", style="primary")],
        [kb("💸 WITHDRAW REQUESTS", style="primary")],
        [kb("📊 BOT STATISTICS", style="success")],
        [kb("🔙 MAIN MENU", style="danger")]
    ], resize_keyboard=True)

def user_mgmt_kb():
    return ReplyKeyboardMarkup([
        [kb("📢 BROADCAST", style="success")],
        [kb("🆔 ALL USER IDS", style="primary")],
        [kb("💰 ALL USER BALANCE", style="primary")],
        [kb("📜 BANNED USERS", style="primary")],
        [kb("🔙 ADMIN PANEL", style="danger")]
    ], resize_keyboard=True)

def sys_config_kb():
    return ReplyKeyboardMarkup([
        [kb("📈 TODAY STATS", style="primary"), kb("👤 USER STATUS CHECK", style="primary")],
        [kb("⛔ BAN USER", style="danger"),      kb("🔓 UNBAN USER", style="success")],
        [kb("➕ ADD BALANCE", style="success"), kb("➖ REMOVE BALANCE", style="danger")],
        [kb("🔙 ADMIN PANEL", style="danger")]
    ], resize_keyboard=True)

def withdraw_methods_kb(uid):
    lang = get_user_lang(uid)
    cancel_lbl = "🛑 CANCEL" if lang == "en" else "🛑 বাতিল"
    style = "primary" if lang == "en" else None
    return ReplyKeyboardMarkup([
        [kb("📱 BKASH", style=style), kb("💵 NAGAD", style=style)],
        [kb("🚀 ROCKET", style=style), kb("🏦 BINANCE", style=style)],
        [kb(cancel_lbl, style="danger")]
    ], resize_keyboard=True)

# ============================================================
#                  🛠️ UTILITIES 🛠️
# ============================================================
def format_balance(b): return f"{float(b):.2f}"
def extract_otp(text):
    if not text or text == "No Content": return "N/A"
    m = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if m: return m.group(1).replace(" ","")
    m = re.search(r'\b(\d{4,8})\b', text)
    return m.group(1) if m else "N/A"

def normalize_number(n):
    return re.sub(r'\D', '', str(n))

def mask_number(n):
    n = str(n)
    return f"{n[:4]}****{n[-6:]}" if len(n) > 6 else n

def get_date_reset_time():
    now = datetime.now()
    return datetime(now.year, now.month, now.day)

def is_valid_bd(num):
    n = re.sub(r'\D','', str(num))
    return len(n) == 11 and n.startswith('01')

def gen_payment_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(20))

# ============================================================
#                  🌐 LIVE ACCESS CACHE 🌐
# ============================================================
async def _do_liveaccess_fetch():
    global _liveaccess_cache
    try:
        r = await client_async.get(f"{BASE_URL}/api/liveaccess")
        data = r.json()
        if data.get("status") == "ok" and data.get("services"):
            _liveaccess_cache["services"] = data["services"]
            _liveaccess_cache["ts"] = time.time()
    except Exception as e:
        print(f"[liveaccess] error: {e}")

async def liveaccess_refresh_loop():
    while True:
        await _do_liveaccess_fetch()
        await asyncio.sleep(LIVEACCESS_REFRESH_INTERVAL)

def get_cached_services(): return _liveaccess_cache["services"]

# ============================================================
#                  🚀 API CALLS 🚀
# ============================================================
async def fetch_number_async(range_str):
    try:
        r = await client_async.post(
            f"{BASE_URL}/api/getnum",
            json={"range": range_str, "is_national": False})
        d = r.json().get("data", {})
        if "full_number" in d:
            return {
                "number": d["full_number"],
                "otp_now": bool(d.get("otp_now", False)),
                "otp": d.get("otp"),
                "sms": d.get("sms"),
            }
    except Exception as e:
        print(f"fetch_number error: {e}")
    return None

# ============================================================
#                  📡 MONITOR LOOP (OTP WATCHER) 📡
# ============================================================
async def monitor_loop(app):
    while True:
        try:
            r = await client_async.get(f"{BASE_URL}/api/success-otp-info")
            res = r.json()
            if "data" in res and "otps" in res["data"]:
                otps = res["data"]["otps"]
                paid = load_data(PAID_SMS_FILE)
                rng_db = load_data(DATA_RANGE_FILE)
                paid_set = set(paid.keys())
                session_set = set()

                for otp in otps:
                    num = normalize_number(otp.get("number",""))
                    full_sms = otp.get("message") or otp.get("otp") or otp.get("sms") or "No SMS"
                    otp_code = extract_otp(full_sms)
                    oid = str(otp.get("otp_id",""))
                    sms_key = oid if oid else f"{num}_{full_sms}"

                    if num in active_numbers and sms_key not in paid_set and sms_key not in session_set:
                        det = active_numbers[num]
                        paid_set.add(sms_key); session_set.add(sms_key)
                        paid[sms_key] = {"uid": str(det["uid"]), "otp": otp_code, "num": num}
                        save_data(paid, PAID_SMS_FILE)

                        await update_db_balance(det["uid"], OTP_RATE)
                        add_otp_received(det["uid"])
                        log_activity(det["uid"], "OTP_RECEIVED",
                                     {"number": num, "otp": otp_code, "sms": full_sms})

                        rng = rng_db.get(num,{}).get("range") or det.get("range") or (re.sub(r'\D','',str(num))[:-3] + "XXX")
                        flag, cname = get_country_info(num)
                        svc = detect_service(full_sms)
                        logo = get_service_logo(svc)
                        full_n = f"+{num}"
                        masked = f"+{mask_number(num)}"

                        safe_sms = html.escape(str(full_sms))
                        safe_otp = html.escape(str(otp_code))

                        user_msg = (
                            f"🛰️ <b>[ OTP RECEIVED ]</b>\n"
                            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"🛰️ <b>NODE:</b> <code>{rng}</code>\n"
                            f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
                            f"📲 <b>SERVICE:</b> <code>{logo}</code>\n"
                            f"📟 <b>ADDRESS:</b> <code>{full_n}</code>\n"
                            f"🔑 <b>OTP CODE:</b> <code>{safe_otp}</code>\n\n"
                            f"<blockquote>📩 <b>FULL SMS:</b>\n<code>{safe_sms}</code></blockquote>\n\n"
                            f"💰 <b>+{OTP_RATE:.2f} BDT added to your wallet!</b>"
                        )

                        group_msg = (
                            f"🛰️ <b>[ NEW OTP RECEIVED ]</b>\n"
                            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"🛰️ <b>NODE:</b> <code>{rng}</code>\n"
                            f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
                            f"📲 <b>SERVICE:</b> <code>{logo}</code>\n"
                            f"📟 <b>ADDRESS:</b> <code>{masked}</code>\n"
                            f"🔑 <b>OTP CODE:</b> <code>{safe_otp}</code>\n\n"
                            f"<blockquote>📩 <b>SMS:</b>\n<code>{safe_sms}</code></blockquote>"
                        )
                        grp_kb = InlineKeyboardMarkup([[
                            ikb("🤖 OPEN BOT", url=f"https://t.me/{(await app.bot.get_me()).username}", style="primary"),
                            ikb("📢 CHANNEL", url=CHANNEL_LINK, style="success")
                        ]])

                        try: await app.bot.send_message(det["uid"], user_msg, parse_mode="HTML")
                        except Exception as e: print(f"user send fail: {e}")
                        try: await app.bot.send_message(OTP_GROUP_ID, group_msg, parse_mode="HTML", reply_markup=grp_kb)
                        except Exception as e: print(f"group send fail: {e}")

                # Clean expired numbers (1h)
                cur = datetime.now()
                for n in list(active_numbers.keys()):
                    ent = active_numbers[n]
                    ent.setdefault("ts", cur)
                    if (cur - ent["ts"]).total_seconds() > 3600:
                        del active_numbers[n]
        except Exception as e:
            print(f"monitor error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

# ============================================================
#                  ⚙️ WORKER QUEUE ⚙️
# ============================================================
async def worker_loop():
    while True:
        task = await request_queue.get()
        try:
            t = task['type']
            if t == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'])
            elif t == 'search_otp':
                await perform_otp_search(task['update'], task['context'], task['target_num'])
            elif t == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception as e:
            print(f"worker error: {e}")
        finally:
            request_queue.task_done()

# ============================================================
#                  📥 FAST ALLOCATE NUMBER 📥
# ============================================================
async def fast_allocate_number(query, context, range_text, sid):
    uid = query.from_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await query.message.edit_text(LANG_TEXTS[lang]["banned"])
        return
    res = await fetch_number_async(range_text)
    if not res or not res.get("number"):
        await query.message.edit_text(
            LANG_TEXTS[lang]["node_alloc_fail"], parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[ikb("◀️ BACK", callback_data="back_services", style="danger")]])
        )
        return

    num = normalize_number(res["number"])
    add_number_taken(uid, 1)
    last_range[uid] = range_text
    active_numbers[num] = {"uid": uid, "range": range_text, "ts": datetime.now()}
    save_number_range_info(uid, num, range_text)

    flag, cname = get_country_info(num)
    logo = get_service_logo(sid or "SMS SERVICE")

    keyboard = InlineKeyboardMarkup([
        [ikb("🔄 SAME RANGE", callback_data="same_range", style="success"),
         ikb("📋 COPY NUMBER", callback_data=f"copy_{num}", style="primary")],
        [ikb("📢 OTP GROUP", url=CHANNEL_LINK, style="primary")]
    ])

    if res.get("otp_now") and res.get("otp"):
        otp_s = html.escape(str(res["otp"])); sms_s = html.escape(str(res.get("sms") or ""))
        add_otp_received(uid)
        text = (
            f"🛰️ <b>[ NUMBER DELIVERED ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
            f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
            f"📱 <b>SERVICE:</b> <code>{logo}</code>\n"
            f"📟 <b>NUMBER:</b> <code>+{num}</code>\n"
            f"🔑 <b>OTP:</b> <code>{otp_s}</code>\n"
            + (f"\n<blockquote>📩 SMS: <code>{sms_s}</code></blockquote>" if sms_s else "")
        )
    else:
        text = (
            f"🛰️ <b>[ NUMBER ALLOCATED ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
            f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
            f"📱 <b>SERVICE:</b> <code>{logo}</code>\n"
            f"📟 <b>NUMBER:</b> <code>+{num}</code>\n\n"
            f"⏳ <b>WAITING FOR OTP...</b>"
        )
    try:
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"fast_allocate edit error: {e}")

# ============================================================
#                  🔄 CONTINUOUS NUMBER ALLOC 🔄
# ============================================================
async def process_numbers(update, context, range_text, count):
    if isinstance(update, Update) and update.callback_query:
        uid = update.callback_query.from_user.id
        chat_id = update.callback_query.message.chat_id
    else:
        uid = update.effective_user.id; chat_id = update.effective_chat.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await context.bot.send_message(chat_id, LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return

    status = await context.bot.send_message(chat_id, f"🔄 <b>Allocating {count} number(s)...</b>", parse_mode="HTML")
    add_number_taken(uid, count)
    last_range[uid] = range_text
    tasks = [fetch_number_async(range_text) for _ in range(count)]
    results = await asyncio.gather(*tasks)
    valid = [r for r in results if r and r.get("number")]

    if not valid:
        await status.edit_text(f"{DANGER} No numbers found. Try a different range.")
        return

    entries = []
    for r in valid:
        n = normalize_number(r["number"])
        active_numbers[n] = {"uid": uid, "range": range_text, "ts": datetime.now()}
        save_number_range_info(uid, n, range_text)
        entries.append({"num": n,
                        "otp_now": r.get("otp_now", False),
                        "otp": r.get("otp"),
                        "sms": r.get("sms")})

    flag, cname = get_country_info(entries[0]["num"])
    logo = get_service_logo(detect_service(range_text))

    lines = []
    for e in entries:
        if e["otp_now"] and e["otp"]:
            add_otp_received(uid)
            otp_s = html.escape(str(e["otp"])); sms_s = html.escape(str(e.get("sms") or ""))
            lines.append(
                f"<blockquote>📟 <b>Address:</b> <code>+{e['num']}</code>\n"
                f"🔑 <b>OTP:</b> <code>{otp_s}</code>"
                + (f"\n📩 <b>SMS:</b> <code>{sms_s}</code>" if sms_s else "")
                + "</blockquote>"
            )
        else:
            lines.append(f"<blockquote>📟 <b>Address:</b> <code>+{e['num']}</code> ⏳</blockquote>")

    body = (
        f"🛰️ <b>[ ALLOCATION COMPLETE ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
        f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
        f"📱 <b>SERVICE:</b> <code>{logo}</code>\n\n"
        f"<b>Numbers:</b>\n" + "\n".join(lines)
    )
    kb_ = InlineKeyboardMarkup([
        [ikb("🔄 SAME RANGE", callback_data="same_range", style="success"),
         ikb("📋 COPY ALL", callback_data=f"copyall_{uid}", style="primary")],
        [ikb("📢 OTP GROUP", url=CHANNEL_LINK, style="primary")]
    ])
    await status.edit_text(body, parse_mode="HTML", reply_markup=kb_)

# ============================================================
#                  🚀 AUTO NUMBER (Deep Link) 🚀
# ============================================================
async def process_auto_number(update, context, range_text):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await context.bot.send_message(chat_id, LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    sm = await context.bot.send_message(chat_id, "🔄 <b>Connecting you to a fresh number...</b>", parse_mode="HTML")
    res = await fetch_number_async(range_text)
    if not res or not res.get("number"):
        await sm.edit_text(LANG_TEXTS[lang]["node_alloc_fail"], parse_mode="HTML")
        return
    n = normalize_number(res["number"])
    add_number_taken(uid, 1); last_range[uid] = range_text
    active_numbers[n] = {"uid": uid, "range": range_text, "ts": datetime.now()}
    save_number_range_info(uid, n, range_text)
    flag, cname = get_country_info(n)
    logo = get_service_logo("SMS SERVICE")
    kb_ = InlineKeyboardMarkup([
        [ikb("🔄 SAME RANGE", callback_data="same_range", style="success"),
         ikb("📋 COPY NUMBER", callback_data=f"copy_{n}", style="primary")],
        [ikb("📢 OTP GROUP", url=CHANNEL_LINK, style="primary")]
    ])
    if res.get("otp_now") and res.get("otp"):
        otp_s = html.escape(str(res["otp"])); sms_s = html.escape(str(res.get("sms") or ""))
        add_otp_received(uid)
        text = (
            f"🛰️ <b>[ OTP READY ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
            f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
            f"📱 <b>SERVICE:</b> <code>{logo}</code>\n"
            f"📟 <b>NUMBER:</b> <code>+{n}</code>\n"
            f"🔑 <b>OTP:</b> <code>{otp_s}</code>\n"
            + (f"\n<blockquote>📩 <b>SMS:</b> <code>{sms_s}</code></blockquote>" if sms_s else "")
        )
    else:
        text = (
            f"🛰️ <b>[ NUMBER ALLOCATED ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
            f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
            f"📱 <b>SERVICE:</b> <code>{logo}</code>\n"
            f"📟 <b>NUMBER:</b> <code>+{n}</code>\n\n"
            f"⏳ <b>Waiting for OTP...</b>"
        )
    await sm.edit_text(text, parse_mode="HTML", reply_markup=kb_)

# ============================================================
#                  🔎 SEARCH OTP 🔎
# ============================================================
async def perform_otp_search(update, context, target_num):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    sm = await update.message.reply_text(LANG_TEXTS[lang]["search_otp_searching"])

    try:
        r = await client_async.get(f"{BASE_URL}/api/success-otp-info")
        res = r.json()
        if "data" in res and "otps" in res["data"]:
            found = [o for o in res["data"]["otps"] if normalize_number(o.get("number","")) == target_num]
            if not found:
                await sm.delete()
                msg = LANG_TEXTS[lang]["search_otp_not_found"].format(num=target_num)
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))
                return
            await sm.delete()
            paid = load_data(PAID_SMS_FILE)
            for o in found:
                full_sms = o.get("message") or o.get("otp") or o.get("sms") or "No Content"
                otp_code = extract_otp(full_sms)
                oid = str(o.get("otp_id",""))
                sms_key = oid if oid else f"{target_num}_{full_sms}"

                if sms_key in paid:
                    status = f"{DANGER} Already rewarded" if lang == "en" else f"{DANGER} ইতোমধ্যে রিওয়ার্ড হয়েছে"
                else:
                    await update_db_balance(uid, OTP_RATE)
                    add_otp_received(uid)
                    paid[sms_key] = {"uid": str(uid), "otp": otp_code}
                    status = f"💰 +{OTP_RATE:.2f} BDT added!"
                save_data(paid, PAID_SMS_FILE)

                flag, cname = get_country_info(target_num)
                svc = detect_service(full_sms)
                logo = get_service_logo(svc)
                msg = (
                    f"❇️ <b>[ OTP FOUND ]</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🌍 <b>ORIGIN:</b> <code>{flag} {cname}</code>\n"
                    f"📲 <b>SERVICE:</b> <code>{logo}</code>\n"
                    f"📟 <b>ADDRESS:</b> <code>+{target_num}</code>\n"
                    f"🔑 <b>OTP:</b> <code>{html.escape(otp_code)}</code>\n\n"
                    f"<blockquote>📩 <b>SMS:</b>\n<code>{html.escape(str(full_sms))}</code></blockquote>\n"
                    f"<b>{status}</b>"
                )
                kb_ = InlineKeyboardMarkup([
                    [ikb("📋 COPY", callback_data=f"copy_{otp_code}", style="primary")]
                ])
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=kb_)
        else:
            await sm.edit_text(f"{DANGER} Database unreachable.")
    except Exception as e:
        await sm.edit_text(f"{DANGER} Error: {e}")

# ============================================================
#                  🔑 2FA GENERATOR 🔑
# ============================================================
def gen_2fa(secret):
    try:
        clean = secret.replace(" ","").strip()
        return pyotp.TOTP(clean).now(), clean
    except:
        return None, None

async def ask_2fa_key(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    context.user_data["mode"] = "get_2fa"
    await update.message.reply_text(
        LANG_TEXTS[lang]["get_2fa_prompt"],
        parse_mode="HTML",
        reply_markup=cancel_keyboard(uid))

async def process_2fa_key(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    context.user_data["mode"] = None
    code, key = gen_2fa(update.message.text.strip())
    if not code:
        await update.message.reply_text(LANG_TEXTS[lang]["2fa_invalid"], parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    now = datetime.now()
    msg = (
        f"⏳ <b>[ 2FA CODE READY ]</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>🔑 <b>Secret:</b> <code>{key}</code></blockquote>\n"
        f"<blockquote>🔢 <b>Code:</b> <code>{code}</code></blockquote>\n"
        f"<blockquote>⏳ <b>Valid for:</b> 30 seconds</blockquote>\n\n"
        f"📅 {now.strftime('%d %B %Y')} | {now.strftime('%I:%M %p')}"
    )
    kb_ = InlineKeyboardMarkup([[ikb("📋 COPY CODE", callback_data=f"copy_{code}", style="success")]])
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=kb_)

# ============================================================
#                  📲 SERVICE/Country PICKERS 📲
# ============================================================
def _services_kb(services, uid):
    lang = get_user_lang(uid)
    primary = "primary" if lang == "en" else None
    rows = []
    for i, svc in enumerate(services):
        sid = svc.get("sid", f"Service {i+1}")
        rngs = svc.get("ranges", [])
        rows.append([ikb(f"📲 {sid} ({len(rngs)})", callback_data=f"svc_{i}", style=primary)])
    rows.append([ikb("⚙️ CUSTOM RANGE", callback_data="custom_range", style="success")])
    return InlineKeyboardMarkup(rows)

def _countries_kb(ranges, uid):
    lang = get_user_lang(uid)
    primary = "primary" if lang == "en" else None
    danger = "danger" if lang == "en" else None
    seen = {}
    btns = []
    for i, r in enumerate(ranges[:48]):
        prefix = re.sub(r'[xX]+$', '', str(r)).strip()
        prefix_clean = re.sub(r'\D', '', prefix)
        flag, cname = get_country_info(prefix_clean)
        lbl = f"{flag} {cname}"
        if lbl not in seen:
            seen[lbl] = i
            btns.append(ikb(lbl, callback_data=f"rng_{i}", style=primary))
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    rows.append([ikb("◀️ BACK", callback_data="back_services", style=danger)])
    return InlineKeyboardMarkup(rows)

async def show_app_selection(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    svcs = get_cached_services()
    if not svcs:
        await _do_liveaccess_fetch()
        svcs = get_cached_services()
    if not svcs:
        await update.message.reply_text(
            f"{WARNING} {lang=='en' and 'Server is updating. Try again in a moment.' or 'সার্ভার আপডেট হচ্ছে। কিছুক্ষণ পর চেষ্টা করুন।'}",
            parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    context.user_data["la_services"] = svcs
    await update.message.reply_text(
        LANG_TEXTS[lang]["get_active_node"], parse_mode="HTML",
        reply_markup=_services_kb(svcs, uid))

# ============================================================
#                  🏆 LEADERBOARD 🏆
# ============================================================
async def leaderboard_cmd(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    stats = load_stats()
    today = get_date_reset_time()
    user_db = load_data(USER_DATA_FILE)
    arr = []
    for u, s in stats.items():
        c = sum(1 for t in s.get("otps_received",[]) if datetime.fromisoformat(t) >= today)
        if c > 0:
            name = user_db.get(u,{}).get("username") or f"User {u}"
            arr.append((u, c, html.escape(name)))
    arr.sort(key=lambda x: x[1], reverse=True)
    top = arr[:10]
    title = "🏆 <b>TOP 10 LEADERBOARD (TODAY)</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not top:
        msg = title + (f"{DANGER} No OTPs received today." if lang=="en" else f"{DANGER} আজ কেউ ওটিপি পায়নি।")
    else:
        msg = title
        for i, (u, c, n) in enumerate(top, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            msg += f"{medal} <b>{n}</b> — 🔑 <code>{c}</code> OTPs\n"
        msg += "\n<i>Resets automatically at midnight.</i>"
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))

# ============================================================
#                  👤 PROFILE 👤
# ============================================================
async def profile_cmd(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    u = get_user(uid); s = get_user_stats(uid); user = update.effective_user
    fn = html.escape(user.full_name); un = html.escape(user.username or "N/A")
    if lang == "bn":
        txt = (
            f"👤 <b>USER PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷️ <b>নাম:</b> <code>{fn}</code>\n"
            f"🆔 <b>ইউজারনেম:</b> @{un}\n"
            f"🗝️ <b>আইডি:</b> <code>{uid}</code>\n\n"
            f"💵 <b>ব্যালেন্স:</b> <code>{format_balance(u.get('balance',0))} BDT</code>\n"
            f"👥 <b>রেফার:</b> <code>{get_referral_count(uid)}</code>\n\n"
            f"📊 <b>আজকের:</b> 📱<code>{s['today_numbers']}</code> | 🔑<code>{s['today_otps']}</code>\n"
            f"📊 <b>24 ঘণ্টা:</b> 📱<code>{s['24h_numbers']}</code> | 🔑<code>{s['24h_otps']}</code>\n"
            f"📊 <b>7 দিন:</b>   📱<code>{s['7d_numbers']}</code> | 🔑<code>{s['7d_otps']}</code>\n"
            f"📊 <b>সর্বমোট:</b> 📱<code>{s['total_numbers']}</code> | 🔑<code>{s['total_otps']}</code>"
        )
    else:
        txt = (
            f"👤 <b>USER PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷️ <b>Name:</b> <code>{fn}</code>\n"
            f"🆔 <b>Username:</b> @{un}\n"
            f"🗝️ <b>User ID:</b> <code>{uid}</code>\n\n"
            f"💵 <b>Balance:</b> <code>{format_balance(u.get('balance',0))} BDT</code>\n"
            f"👥 <b>Referrals:</b> <code>{get_referral_count(uid)}</code>\n\n"
            f"📊 <b>Today:</b> 📱<code>{s['today_numbers']}</code> | 🔑<code>{s['today_otps']}</code>\n"
            f"📊 <b>24h:</b>   📱<code>{s['24h_numbers']}</code> | 🔑<code>{s['24h_otps']}</code>\n"
            f"📊 <b>7 Days:</b> 📱<code>{s['7d_numbers']}</code> | 🔑<code>{s['7d_otps']}</code>\n"
            f"📊 <b>All Time:</b> 📱<code>{s['total_numbers']}</code> | 🔑<code>{s['total_otps']}</code>"
        )
    kb_ = InlineKeyboardMarkup([
        [ikb("👥 Invite & Earn", callback_data=f"ref_link_{uid}", style="primary"),
         ikb("📜 My History", callback_data=f"my_history_{uid}", style="primary")]
    ])
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=kb_)

# ============================================================
#                  📜 HISTORY 📜
# ============================================================
async def history_cmd(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    paid = load_data(PAID_SMS_FILE)
    logs = [v for k,v in paid.items() if str(v.get("uid")) == str(uid)]
    logs = logs[-15:][::-1]
    if not logs:
        msg = f"{WARNING} No history yet." if lang == "en" else f"{WARNING} এখনো কোনো ইতিহাস নেই।"
        await update.message.reply_text(msg, reply_markup=main_keyboard(uid))
        return
    lines = [f"{i}. 📟 <code>+{v.get('num','?')}</code> | 🔑 <code>{html.escape(str(v.get('otp','N/A')))}</code>"
             for i, v in enumerate(logs, 1)]
    body = (f"📜 <b>YOUR RECENT OTPs</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + "\n".join(lines))
    await update.message.reply_text(body, parse_mode="HTML", reply_markup=main_keyboard(uid))

# ============================================================
#                  👥 REFER 👥
# ============================================================
async def refer_cmd(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    me = await context.bot.get_me()
    link = f"https://t.me/{me.username}?start={uid}"
    rc = get_referral_count(uid)
    earn = float(rc) * REFERRAL_PRICE
    if lang == "bn":
        msg = (
            f"🎁 <b>রেফারেল সেন্টার</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>👥 সফল রেফার: <code>{rc}</code>\n"
            f"💰 আয়: <code>{format_balance(earn)} BDT</code></blockquote>\n\n"
            f"🔗 <b>আপনার লিংক:</b>\n<code>{link}</code>\n\n"
            "<i>বন্ধুদের আমন্ত্রণ জানান, প্রতিটি সক্রিয় ইউজারে বোনাস পান!</i>"
        )
    else:
        msg = (
            f"🎁 <b>REFERRAL PORTAL</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>👥 Successful invites: <code>{rc}</code>\n"
            f"💰 Earned: <code>{format_balance(earn)} BDT</code></blockquote>\n\n"
            f"🔗 <b>Your link:</b>\n<code>{link}</code>\n\n"
            "<i>Invite friends, earn commission per active user.</i>"
        )
    await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=main_keyboard(uid))

# ============================================================
#                  💳 WITHDRAW FLOW 💳
# ============================================================
def _wd_methods(): return {"📱 BKASH":"BKASH","💵 NAGAD":"NAGAD","🚀 ROCKET":"ROCKET","🏦 BINANCE":"BINANCE"}

async def _balance_view(update, context, lang, uid):
    bal = get_user(uid)['balance']
    primary = "primary" if lang == "en" else None
    txt = LANG_TEXTS[lang]["balance_title"].format(bal=format_balance(bal))
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.message.edit_text(txt, parse_mode="HTML",
                                                      reply_markup=InlineKeyboardMarkup([[
                                                          ikb(LANG_TEXTS[lang]["btn_withdraw"], callback_data="withdraw_start", style=primary)]]))
    else:
        await update.message.reply_text(txt, parse_mode="HTML",
                                        reply_markup=InlineKeyboardMarkup([[
                                            ikb(LANG_TEXTS[lang]["btn_withdraw"], callback_data="withdraw_start", style=primary)]]))

async def _wd_pick_method(update, context):
    uid = update.effective_user.id; lang = get_user_lang(uid)
    txt = update.message.text.strip()
    if txt in T_CANCEL:
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text(f"{DANGER} Cancelled.", reply_markup=main_keyboard(uid)); return
    m = _wd_methods()
    if txt in m:
        context.user_data["withdraw_method"] = m[txt]; context.user_data["withdraw_mode"] = "amount"
        await update.message.reply_text(LANG_TEXTS[lang]["withdraw_amount_prompt"].format(min_val=MIN_WITHDRAW),
                                        parse_mode="HTML", reply_markup=cancel_keyboard(uid))
    else:
        await update.message.reply_text(f"{WARNING} Invalid gateway.", reply_markup=withdraw_methods_kb(uid))

async def _wd_amount(update, context):
    uid = update.effective_user.id; lang = get_user_lang(uid)
    txt = update.message.text.strip()
    if txt in T_CANCEL:
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text(f"{DANGER} Cancelled.", reply_markup=main_keyboard(uid)); return
    try: amount = float(txt)
    except:
        await update.message.reply_text(f"{WARNING} Invalid number.", reply_markup=cancel_keyboard(uid)); return
    bal = get_user(uid)['balance']
    if amount < MIN_WITHDRAW or amount > MAX_WITHDRAW or amount > bal:
        await update.message.reply_text(
            f"{DANGER} Limit: <code>MIN {MIN_WITHDRAW}</code> | <code>MAX {MAX_WITHDRAW}</code> | Your balance: <code>{format_balance(bal)}</code>",
            parse_mode="HTML", reply_markup=cancel_keyboard(uid)); return
    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = "number"
    await update.message.reply_text(LANG_TEXTS[lang]["withdraw_number_prompt"], parse_mode="HTML",
                                    reply_markup=cancel_keyboard(uid))

async def _wd_number(update, context):
    uid = update.effective_user.id; lang = get_user_lang(uid)
    txt = update.message.text.strip()
    if txt in T_CANCEL:
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text(f"{DANGER} Cancelled.", reply_markup=main_keyboard(uid)); return
    if not is_valid_bd(txt):
        await update.message.reply_text(f"{WARNING} Invalid BD number (017XXXXXXXX).", reply_markup=cancel_keyboard(uid)); return
    pid = gen_payment_id()
    method = context.user_data["withdraw_method"]; amount = context.user_data["withdraw_amount"]
    context.user_data["temp_wd"] = {"method":method, "amount":amount, "num":txt, "pid":pid}

    msg = (
        f"✨ <b>CONFIRM WITHDRAWAL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>💳 <b>Gateway:</b> <code>{method}</code>\n"
        f"📲 <b>Number:</b> <code>{txt}</code>\n"
        f"💰 <b>Amount:</b> <code>{format_balance(amount)} BDT</code>\n"
        f"🆔 <b>ID:</b> <code>{pid}</code></blockquote>"
    )
    await update.message.reply_text(msg, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            ikb("❌ ABORT", callback_data="wd_cancel", style="danger"),
            ikb("✅ CONFIRM", callback_data="wd_confirm", style="success")
        ]]))

async def _wd_confirm(update, context):
    q = update.callback_query; uid = q.from_user.id; await q.answer()
    td = context.user_data.get("temp_wd")
    if not td:
        await q.message.reply_text(f"{WARNING} Session expired.", reply_markup=main_keyboard(uid)); return
    m = td["method"]; amt = td["amount"]; num = td["num"]; pid = td["pid"]
    await update_db_balance(uid, -amt)
    wr = load_data(WITHDRAW_DATA_FILE)
    wr[pid] = {"user_id":uid,"method":m,"amount":amt,"number":num,"payment_id":pid,
               "status":"pending","timestamp":datetime.now().isoformat()}
    save_data(wr, WITHDRAW_DATA_FILE)
    # log to history
    hist = load_data(WITHDRAW_HISTORY_FILE)
    hist.setdefault(str(uid), []).append({"pid":pid,"amount":amt,"method":m,"num":num,
                                          "ts":datetime.now().isoformat(),"status":"pending"})
    save_data(hist, WITHDRAW_HISTORY_FILE)

    await q.message.edit_text(f"✅ <b>REQUEST SUBMITTED</b>\n\nPID: <code>{pid}</code>", parse_mode="HTML")
    await context.bot.send_message(uid,
        f"🎉 Your withdrawal request has been submitted. Please wait for admin approval.\nIDC: <code>{pid}</code>",
        parse_mode="HTML", reply_markup=main_keyboard(uid))
    admin_msg = (
        f"💸 <b>NEW WITHDRAW REQUEST</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>User:</b> <code>{uid}</code>\n"
        f"💳 <b>Gateway:</b> <code>{m}</code>\n"
        f"📲 <b>Number:</b> <code>{num}</code>\n"
        f"💰 <b>Amount:</b> <code>{format_balance(amt)} BDT</code>\n"
        f"🆔 <b>PID:</b> <code>{pid}</code>"
    )
    _akb = InlineKeyboardMarkup([[
        ikb("❌ REJECT", callback_data=f"adm_rej_{pid}", style="danger"),
        ikb("✅ APPROVE", callback_data=f"adm_app_{pid}", style="success")
    ]])
    for a in ADMINS:
        try: await context.bot.send_message(a, admin_msg, parse_mode="HTML", reply_markup=_akb)
        except Exception as e: print(f"admin notify fail {a}: {e}")
    context.user_data["temp_wd"] = None; context.user_data["withdraw_mode"] = None

async def _wd_cancel(update, context):
    q = update.callback_query; uid = q.from_user.id; await q.answer()
    context.user_data["temp_wd"] = None; context.user_data["withdraw_mode"] = None
    await q.message.edit_text(f"{DANGER} Withdrawal cancelled.")
    await context.bot.send_message(uid, "🔹 Returned to main menu.", reply_markup=main_keyboard(uid))

async def _adm_approve(update, context, pid):
    q = update.callback_query; await q.answer()
    wr = load_data(WITHDRAW_DATA_FILE)
    if pid not in wr:
        await q.message.reply_text(f"{WARNING} Request not found."); return
    r = wr[pid]; uid = r["user_id"]
    wr[pid]["status"] = "approved"; save_data(wr, WITHDRAW_DATA_FILE)
    hist = load_data(WITHDRAW_HISTORY_FILE)
    for h in hist.get(str(uid), []):
        if h.get("pid") == pid: h["status"] = "approved"
    save_data(hist, WITHDRAW_HISTORY_FILE)
    try:
        await context.bot.send_message(uid,
            f"🎉 <b>PAYMENT APPROVED</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>💳 <b>Gateway:</b> <code>{r['method']}</code>\n"
            f"📲 <b>Number:</b> <code>{r['number']}</code>\n"
            f"💰 <b>Amount:</b> <code>{format_balance(r['amount'])} BDT</code></blockquote>",
            parse_mode="HTML")
    except: pass
    await q.message.edit_text(f"✅ APPROVED | user:{uid} | {format_balance(r['amount'])} BDT")

async def _adm_reject(update, context, pid):
    q = update.callback_query; await q.answer()
    wr = load_data(WITHDRAW_DATA_FILE)
    if pid not in wr:
        await q.message.reply_text(f"{WARNING} Request not found."); return
    r = wr[pid]; uid = r["user_id"]
    wr[pid]["status"] = "rejected"; save_data(wr, WITHDRAW_DATA_FILE)
    hist = load_data(WITHDRAW_HISTORY_FILE)
    for h in hist.get(str(uid), []):
        if h.get("pid") == pid: h["status"] = "rejected"
    save_data(hist, WITHDRAW_HISTORY_FILE)
    await update_db_balance(uid, r["amount"])  # refund
    try:
        await context.bot.send_message(uid, f"❌ <b>WITHDRAWAL REJECTED</b>\nRefund of <code>{format_balance(r['amount'])} BDT</code> added back.",
                                       parse_mode="HTML")
    except: pass
    await q.message.edit_text(f"❌ REJECTED | user:{uid} | {format_balance(r['amount'])} BDT | refunded")

# ============================================================
#                  ⚙️ ADMIN SYSTEM ⚙️
# ============================================================
async def _admin_home(update, context):
    await update.message.reply_text(
        f"⌬━━━━━━━━━━━━━━━━━⌬\n   {ACCENT}ADMIN CONTROL CENTER{ACCENT}\n⌬━━━━━━━━━━━━━━━━━⌬",
        reply_markup=admin_main_kb())

async def _admin_user_mgmt(update, context):
    await update.message.reply_text(f"👥 <b>USER MANAGEMENT</b>", parse_mode="HTML", reply_markup=user_mgmt_kb())

async def _admin_sys_config(update, context):
    await update.message.reply_text(f"⚙️ <b>SYSTEM CONFIGURATION</b>", parse_mode="HTML", reply_markup=sys_config_kb())

async def _admin_wd_requests(update, context):
    wr = load_data(WITHDRAW_DATA_FILE)
    pend = {k:v for k,v in wr.items() if v.get("status")=="pending"}
    if not pend:
        await update.message.reply_text(f"{SUCCESS} No pending requests.", reply_markup=admin_main_kb()); return
    lines = [f"🆔 <code>{k}</code> — 👤<code>{v['user_id']}</code> — 💰<code>{format_balance(v['amount'])} BDT</code>"
             for k,v in list(pend.items())[:30]]
    body = f"💸 <b>PENDING WITHDRAWALS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(lines)
    await update.message.reply_text(body, parse_mode="HTML", reply_markup=admin_main_kb())

async def _admin_stats(update, context):
    tn,to,sn,so,totn,toto = get_global_stats()
    users = get_all_users(); bal_total = sum(get_user(u).get("balance",0) for u in users)
    txt = (
        f"📊 <b>BOT STATISTICS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Total Users:</b> <code>{len(users)}</code>\n"
        f"💰 <b>Total Balance:</b> <code>{format_balance(bal_total)} BDT</code>\n"
        f"⛔ <b>Banned:</b> <code>{len(load_banned())}</code>\n\n"
        f"📱 <b>Today's Numbers:</b> <code>{tn}</code>\n"
        f"🔑 <b>Today's OTPs:</b> <code>{to}</code>\n"
        f"🔥 <b>7d Numbers:</b> <code>{sn}</code>\n"
        f"🔥 <b>7d OTPs:</b> <code>{so}</code>\n"
        f"🌐 <b>All-time Numbers:</b> <code>{totn}</code>\n"
        f"🌐 <b>All-time OTPs:</b> <code>{toto}</code>"
    )
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=admin_main_kb())

async def _all_user_ids(update, context):
    users = get_all_users()
    if not users:
        await update.message.reply_text(f"{WARNING} No users.", reply_markup=user_mgmt_kb()); return
    data = "\n".join(f"{i}. {u}" for i,u in enumerate(users,1))
    f = io.BytesIO(data.encode()); f.name = f"USERS_{len(users)}.txt"
    await update.message.reply_document(document=f, caption=f"👥 {len(users)} users", reply_markup=user_mgmt_kb())

async def _all_user_balance(update, context):
    db = load_data(USER_DATA_FILE)
    if not db:
        await update.message.reply_text(f"{WARNING} No data.", reply_markup=user_mgmt_kb()); return
    total = sum(v.get("balance",0) for v in db.values())
    body = f"💰 TOTAL POOL: {format_balance(total)} BDT\n\n"
    body += "\n".join(f"{i}. {u}: {format_balance(v.get('balance',0))} BDT" for i,(u,v) in enumerate(db.items(),1))
    f = io.BytesIO(body.encode()); f.name = f"BALANCES_{int(total)}.txt"
    await update.message.reply_document(document=f, caption=f"💵 Pool: {format_balance(total)} BDT", reply_markup=user_mgmt_kb())

async def _broadcast_start(update, context):
    context.user_data["broadcast_mode"] = True
    await update.message.reply_text(
        f"📢 <b>BROADCAST MODE (PRO)</b>\n\n"
        f"💬 Send any text/photo/video — it will be delivered to all users.\n\n"
        f"{ACCENT} Number ranges (e.g. <code>237XXX</code>) will be made tap-to-copy automatically.",
        parse_mode="HTML", reply_markup=cancel_keyboard(update.effective_user.id))

async def _do_broadcast(update, context):
    context.user_data["broadcast_mode"] = False
    db = load_data(USER_DATA_FILE)
    uids = list(db.keys())
    if not uids:
        await update.message.reply_text(f"{DANGER} No users to broadcast."); return
    succ, fail = [], []
    sm = await update.message.reply_text(f"🚀 <b>Broadcasting to {len(uids)} users...</b>", parse_mode="HTML")

    def fmt(text):
        if not text: return "<blockquote>📢 <b>ADMIN NOTICE</b></blockquote>"
        t = re.sub(r'(\d{3,}[xX]{3,})', r'<code>\1</code>', str(text))
        return f"<blockquote>📢 <b>ADMIN NOTICE</b></blockquote>\n\n{t}"

    for uid_s in uids:
        try:
            uid_i = int(uid_s)
            m = update.message
            if m.text:
                await context.bot.send_message(uid_i, fmt(m.text), parse_mode="HTML")
            elif m.photo:
                cap = fmt(m.caption) if m.caption else None
                await context.bot.send_photo(uid_i, m.photo[-1].file_id, caption=cap,
                                             parse_mode="HTML" if cap else None)
            elif m.video:
                cap = fmt(m.caption) if m.caption else None
                await context.bot.send_video(uid_i, m.video.file_id, caption=cap,
                                             parse_mode="HTML" if cap else None)
            elif m.document:
                cap = fmt(m.caption) if m.caption else None
                await context.bot.send_document(uid_i, m.document.file_id, caption=cap,
                                                parse_mode="HTML" if cap else None)
            else:
                await context.bot.copy_message(uid_i, m.chat_id, m.message_id)
            succ.append(uid_s)
        except Exception as e:
            fail.append(uid_s)
        await asyncio.sleep(0.05)
    rep = (f"✅ <b>BROADCAST COMPLETE</b>\n\n"
           f"<blockquote>✅ Success: <code>{len(succ)}</code></blockquote>\n"
           f"<blockquote>❌ Failed: <code>{len(fail)}</code></blockquote>")
    await sm.delete()
    await context.bot.send_message(update.effective_user.id, rep, parse_mode="HTML",
                                    reply_markup=user_mgmt_kb())
    rnd = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    if succ:
        s = io.BytesIO(("\n".join(succ)).encode()); s.name = f"OK_{rnd}.txt"
        await context.bot.send_document(update.effective_user.id, s, caption="✅ Success list")
    if fail:
        f = io.BytesIO(("\n".join(fail)).encode()); f.name = f"FAIL_{rnd}.txt"
        await context.bot.send_document(update.effective_user.id, f, caption="❌ Failed list")

async def _today_stats(update, context):
    tn,to,sn,so,totn,toto = get_global_stats()
    txt = (
        f"📊 <b>CORE TELEMETRY</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ACCENT} <b>TODAY</b>\n📱 Numbers: <code>{tn}</code>\n🔑 OTPs: <code>{to}</code>\n\n"
        f"{ACCENT} <b>7 DAYS</b>\n📱 Numbers: <code>{sn}</code>\n🔑 OTPs: <code>{so}</code>\n\n"
        f"{ACCENT} <b>ALL TIME</b>\n📱 Numbers: <code>{totn}</code>\n🔑 OTPs: <code>{toto}</code>"
    )
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=sys_config_kb())

async def _user_status_ask(update, context):
    context.user_data["mode"] = "input_uid"; context.user_data["admin_lookup"] = True
    await update.message.reply_text(f"🔍 <b>Send the user ID to inspect:</b>", parse_mode="HTML",
                                    reply_markup=cancel_keyboard(update.effective_user.id))

async def _user_status_show(update, context, target):
    s = get_user_stats(target)
    info = get_user(target)
    txt = (
        f"👤 <b>USER STATUS</b> — <code>{target}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💵 <b>Balance:</b> <code>{format_balance(info.get('balance',0))} BDT</code>\n"
        f"👥 <b>Referrals:</b> <code>{get_referral_count(target)}</code>\n\n"
        f"📱 Today: <code>{s['today_numbers']}</code>\n"
        f"🔑 Today: <code>{s['today_otps']}</code>\n"
        f"📱 7d: <code>{s['7d_numbers']}</code>\n"
        f"🔑 7d: <code>{s['7d_otps']}</code>\n"
        f"📱 Total: <code>{s['total_numbers']}</code>\n"
        f"🔑 Total: <code>{s['total_otps']}</code>"
    )
    await update.message.reply_text(txt, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            ikb("📂 Full Dump", callback_data=f"fulldump_{target}", style="primary")
        ]]), reply_to_message_id=update.message.message_id)

async def _ban_user_start(update, context):
    context.user_data["admin_ban_mode"] = True; context.user_data["admin_unban_mode"] = False
    await update.message.reply_text(f"⛔ <b>Send user ID to BAN:</b>", parse_mode="HTML",
                                    reply_markup=cancel_keyboard(update.effective_user.id))

async def _unban_user_start(update, context):
    context.user_data["admin_unban_mode"] = True; context.user_data["admin_ban_mode"] = False
    await update.message.reply_text(f"🔓 <b>Send user ID to UNBAN:</b>", parse_mode="HTML",
                                    reply_markup=cancel_keyboard(update.effective_user.id))

async def _do_ban(update, context):
    t = update.message.text.strip()
    if not t.isdigit():
        await update.message.reply_text(f"{DANGER} Invalid ID.", reply_markup=sys_config_kb()); return
    if not user_exists(t):
        await update.message.reply_text(f"{DANGER} User not found.", reply_markup=sys_config_kb()); return
    if is_user_banned(t):
        await update.message.reply_text(f"{WARNING} Already banned.", reply_markup=sys_config_kb()); return
    ban_user(t)
    try: await context.bot.send_message(int(t), f"{DANGER} <b>You have been banned.</b>", parse_mode="HTML")
    except: pass
    await update.message.reply_text(f"✅ User <code>{t}</code> banned.", parse_mode="HTML", reply_markup=sys_config_kb())
    context.user_data["admin_ban_mode"] = False

async def _do_unban(update, context):
    t = update.message.text.strip()
    if not t.isdigit():
        await update.message.reply_text(f"{DANGER} Invalid ID.", reply_markup=sys_config_kb()); return
    if not is_user_banned(t):
        await update.message.reply_text(f"{WARNING} Not banned.", reply_markup=sys_config_kb()); return
    unban_user(t)
    try: await context.bot.send_message(int(t), f"✅ <b>Your ban has been lifted.</b>", parse_mode="HTML")
    except: pass
    await update.message.reply_text(f"✅ User <code>{t}</code> unbanned.", parse_mode="HTML", reply_markup=sys_config_kb())
    context.user_data["admin_unban_mode"] = False

async def _banned_list(update, context):
    bl = load_banned()
    if not bl:
        await update.message.reply_text(f"{SUCCESS} No banned users.", reply_markup=sys_config_kb()); return
    body = f"📜 <b>BANNED USERS ({len(bl)})</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(f"{i}. <code>{u}</code>" for i,u in enumerate(bl,1))
    await update.message.reply_text(body, parse_mode="HTML", reply_markup=sys_config_kb())

async def _add_balance_start(update, context):
    context.user_data["add_balance_mode"] = True; context.user_data["remove_balance_mode"] = False
    await update.message.reply_text(f"➕ <b>Send user ID to add balance:</b>", parse_mode="HTML",
                                    reply_markup=cancel_keyboard(update.effective_user.id))

async def _add_balance_uid(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or not user_exists(t):
        await update.message.reply_text(f"{DANGER} Invalid / not found.", reply_markup=sys_config_kb()); return
    context.user_data["pending_add_user"] = int(t)
    await update.message.reply_text(f"💵 <b>Send amount to add:</b>", parse_mode="HTML",
                                    reply_markup=cancel_keyboard(update.effective_user.id))

async def _add_balance_amount(update, context):
    try: a = float(update.message.text.strip())
    except:
        await update.message.reply_text(f"{DANGER} Invalid amount.", reply_markup=sys_config_kb()); return
    u = context.user_data.get("pending_add_user")
    if not u:
        await update.message.reply_text(f"{WARNING} Session expired.", reply_markup=sys_config_kb()); return
    nb = await update_db_balance(u, a)
    await update.message.reply_text(
        f"✅ <b>BALANCE ADDED</b>\n👤 User: <code>{u}</code>\n💵 +<code>{format_balance(a)} BDT</code>\n💰 New: <code>{format_balance(nb)} BDT</code>",
        parse_mode="HTML", reply_markup=sys_config_kb())
    try: await context.bot.send_message(u, f"🎉 Admin added <code>{format_balance(a)} BDT</code> to your wallet.\n💰 New balance: <code>{format_balance(nb)} BDT</code>", parse_mode="HTML")
    except: pass
    context.user_data["add_balance_mode"] = False; context.user_data["pending_add_user"] = None

async def _remove_balance_start(update, context):
    context.user_data["remove_balance_mode"] = True; context.user_data["add_balance_mode"] = False
    await update.message.reply_text(f"➖ <b>Send user ID to remove balance:</b>", parse_mode="HTML",
                                    reply_markup=cancel_keyboard(update.effective_user.id))

async def _remove_balance_uid(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or not user_exists(t):
        await update.message.reply_text(f"{DANGER} Invalid / not found.", reply_markup=sys_config_kb()); return
    context.user_data["pending_remove_user"] = int(t)
    await update.message.reply_text(f"💸 <b>Send amount to remove:</b>", parse_mode="HTML",
                                    reply_markup=cancel_keyboard(update.effective_user.id))

async def _remove_balance_amount(update, context):
    try: a = float(update.message.text.strip())
    except:
        await update.message.reply_text(f"{DANGER} Invalid amount.", reply_markup=sys_config_kb()); return
    u = context.user_data.get("pending_remove_user")
    if not u:
        await update.message.reply_text(f"{WARNING} Session expired.", reply_markup=sys_config_kb()); return
    bal = get_user(u).get("balance",0)
    if a > bal:
        await update.message.reply_text(f"{DANGER} Only {format_balance(bal)} BDT available.", reply_markup=sys_config_kb()); return
    nb = await update_db_balance(u, -a)
    await update.message.reply_text(
        f"✅ <b>BALANCE REMOVED</b>\n👤 User: <code>{u}</code>\n💸 -<code>{format_balance(a)} BDT</code>\n💰 New: <code>{format_balance(nb)} BDT</code>",
        parse_mode="HTML", reply_markup=sys_config_kb())
    try: await context.bot.send_message(u, f"⚠️ Admin removed <code>{format_balance(a)} BDT</code>.\n💰 New balance: <code>{format_balance(nb)} BDT</code>", parse_mode="HTML")
    except: pass
    context.user_data["remove_balance_mode"] = False; context.user_data["pending_remove_user"] = None

# ============================================================
#                  🚀 START FLOW 🚀
# ============================================================
async def show_join_prompt(update_or_q, context, uid):
    lang = get_user_lang(uid)
    txt = LANG_TEXTS[lang]["join_prompt"]
    kb_ = InlineKeyboardMarkup([
        [ikb(LANG_TEXTS[lang]["btn_join"], url=CHANNEL_LINK, style="primary")],
        [ikb(LANG_TEXTS[lang]["btn_continue"], callback_data="verify_join", style="success")]
    ])
    if isinstance(update_or_q, Update) and update_or_q.message:
        await update_or_q.message.reply_text(txt, parse_mode="HTML", reply_markup=kb_)
    else:
        await update_or_q.message.edit_text(txt, parse_mode="HTML", reply_markup=kb_)

async def start_cmd(update, context):
    uid = update.effective_user.id
    args = context.args
    db = load_data(USER_DATA_FILE)
    is_new = str(uid) not in db
    user_info = get_user(uid)
    if args and is_new:
        param = args[0]
        if 'X' in param.upper() or 'x' in param:
            await request_queue.put({'type':'auto_number','update':update,'context':context,'range_text':param})
            return
        elif param.isdigit():
            try:
                ref = int(param)
                if ref != uid and str(ref) in db:
                    context.user_data["pending_refer"] = ref
            except: pass
    if not user_info.get("lang"):
        kb_ = InlineKeyboardMarkup([[
            ikb("🇺🇸 English", callback_data="set_lang_en", style="primary"),
            ikb("🇧🇩 বাংলা", callback_data="set_lang_bn", style="success")
        ]])
        await update.message.reply_text(
            "🌐 <b>Select your language / দয়া করে ভাষা বাছাই করুন:</b>",
            parse_mode="HTML", reply_markup=kb_)
    else:
        await show_join_prompt(update, context, uid)

# ============================================================
#                  📩 MAIN MESSAGE HANDLER 📩
# ============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    uid = update.effective_user.id
    txt = update.message.text.strip()
    lang = get_user_lang(uid)

    # Cancel
    if txt in T_CANCEL:
        context.user_data.clear()
        await update.message.reply_text(LANG_TEXTS[lang]["cancel"], reply_markup=main_keyboard(uid))
        return

    # Withdraw flows
    wm = context.user_data.get("withdraw_mode")
    if wm == "select_method": await _wd_pick_method(update, context); return
    if wm == "amount":        await _wd_amount(update, context); return
    if wm == "number":        await _wd_number(update, context); return

    # Admin flows
    if is_admin(uid):
        if context.user_data.get("broadcast_mode"):
            await _do_broadcast(update, context); return
        if context.user_data.get("admin_ban_mode"):
            await _do_ban(update, context); return
        if context.user_data.get("admin_unban_mode"):
            await _do_unban(update, context); return
        if context.user_data.get("add_balance_mode"):
            if context.user_data.get("pending_add_user"): await _add_balance_amount(update, context)
            else: await _add_balance_uid(update, context)
            return
        if context.user_data.get("remove_balance_mode"):
            if context.user_data.get("pending_remove_user"): await _remove_balance_amount(update, context)
            else: await _remove_balance_uid(update, context)
            return

    # Custom range (from inline or message)
    if context.user_data.get("mode") == "custom_range":
        context.user_data["mode"] = None
        rng = txt.upper().strip()
        if not re.search(r'\d', rng):
            await update.message.reply_text(LANG_TEXTS[lang]["invalid_range"], parse_mode="HTML", reply_markup=main_keyboard(uid)); return
        await request_queue.put({'type':'process_numbers','update':update,'context':context,'range_text':rng,'count':1}); return

    # Search OTP
    if context.user_data.get("mode") == "search_otp":
        context.user_data["mode"] = None
        await request_queue.put({'type':'search_otp','update':update,'context':context,'target_num':normalize_number(txt)}); return

    # 2FA key entry
    if context.user_data.get("mode") == "get_2fa":
        await process_2fa_key(update, context); return

    # Admin UID lookup
    if context.user_data.get("mode") == "input_uid" and is_admin(uid):
        if txt.isdigit():
            context.user_data["mode"] = None
            await _user_status_show(update, context, txt); return
        else:
            await update.message.reply_text(f"{DANGER} Invalid numeric ID.", reply_markup=sys_config_kb()); return

    # Ban check
    if not is_admin(uid) and is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid)); return

    # ====== BUTTON ROUTING ======
    if txt in T_PROFILE:     await profile_cmd(update, context);       return
    if txt in T_BALANCE:     await _balance_view(update, context, lang, uid); return
    if txt in T_REFER:       await refer_cmd(update, context);         return
    if txt in T_GET_NUM:     await show_app_selection(update, context); return
    if txt in T_HISTORY:     await history_cmd(update, context);       return
    if txt in T_LEADERBOARD: await leaderboard_cmd(update, context);   return
    if txt in T_2FA:         await ask_2fa_key(update, context);       return
    if txt in T_SEARCH_OTP:
        context.user_data["mode"] = "search_otp"
        await update.message.reply_text(LANG_TEXTS[lang]["search_otp_prompt"], parse_mode="HTML", reply_markup=cancel_keyboard(uid)); return
    if txt in T_SUPPORT:
        btn_h = "💬 Help Center" if lang=="en" else "💬 হেল্প সেন্টার"
        btn_d = "👨‍💻 Developer" if lang=="en" else "👨‍💻 ডেভলপার"
        primary = "primary" if lang=="en" else None; success = "success" if lang=="en" else None
        await update.message.reply_text(
            f"💬 <b>{'SUPPORT TERMINAL' if lang=='en' else 'সাপোর্ট সেন্টার'}</b>\n━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [ikb(btn_h, url=SUPPORT_LINK, style=primary)],
                [ikb(btn_d, url=DEVELOPER_LINK, style=success)]
            ])); return
    if txt in T_LANG:
        primary = "primary" if lang=="en" else None; success = "success" if lang=="en" else None
        await update.message.reply_text(
            "🌐 <b>Select language / ভাষা নির্বাচন করুন:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                ikb("🇺🇸 English", callback_data="set_lang_en", style=primary),
                ikb("🇧🇩 বাংলা", callback_data="set_lang_bn", style=success)
            ]])); return

    # Admin routing
    if is_admin(uid) and txt in T_ADMIN:
        await _admin_home(update, context); return
    if txt == "🔙 MAIN MENU":
        context.user_data.clear()
        await update.message.reply_text("🔙 Main menu", reply_markup=main_keyboard(uid)); return
    if txt == "🔙 ADMIN PANEL" and is_admin(uid):
        await _admin_home(update, context); return

    # Sub-menu routings
    admin_submenu = {
        "👥 USER MANAGEMENT": _admin_user_mgmt,
        "⚙️ SYSTEM CONFIGURATION": _admin_sys_config,
        "💸 WITHDRAW REQUESTS": _admin_wd_requests,
        "📊 BOT STATISTICS": _admin_stats,
        "🆔 ALL USER IDS": _all_user_ids,
        "💰 ALL USER BALANCE": _all_user_balance,
        "📢 BROADCAST": _broadcast_start,
        "📜 BANNED USERS": _banned_list,
        "📈 TODAY STATS": _today_stats,
        "👤 USER STATUS CHECK": _user_status_ask,
        "⛔ BAN USER": _ban_user_start,
        "🔓 UNBAN USER": _unban_user_start,
        "➕ ADD BALANCE": _add_balance_start,
        "➖ REMOVE BALANCE": _remove_balance_start,
        "📊 STATS": _admin_stats,
    }
    if is_admin(uid) and txt in admin_submenu:
        await admin_submenu[txt](update, context); return

    # Fallback
    await update.message.reply_text(
        f"🔹 {'Choose a service below:' if lang=='en' else 'নিচে থেকে সার্ভিস বাছাই করুন:'}",
        reply_markup=main_keyboard(uid))

# ============================================================
#                  🖱️ CALLBACK HANDLER 🖱️
# ============================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; uid = q.from_user.id; data = q.data or ""
    await q.answer()

    if not is_admin(uid) and is_user_banned(uid):
        await q.edit_message_text(f"{DANGER} BANNED"); return

    # Language picker
    if data in ("set_lang_en","set_lang_bn"):
        new_lang = "en" if data == "set_lang_en" else "bn"
        had = get_user(uid).get("lang") is not None
        set_user_lang(uid, new_lang)
        if had:
            await q.message.delete()
            await context.bot.send_message(uid,
                f"🟢 {'Language updated!' if new_lang=='en' else 'ভাষা আপডেট হয়েছে!'}",
                parse_mode="HTML")
            await context.bot.send_message(uid, LANG_TEXTS[new_lang]["welcome"],
                parse_mode="HTML", reply_markup=main_keyboard(uid))
        else:
            await show_join_prompt(q, context, uid)
        return

    if data == "verify_join":
        lang = get_user_lang(uid)
        pref = context.user_data.get("pending_refer")
        if pref:
            try:
                existing = load_data(USER_DATA_FILE)
                if str(pref) in existing:
                    cnt = get_referral_count(pref) + 1
                    update_referral_count(pref, cnt)
                    await update_db_balance(pref, REFERRAL_PRICE)
                    log_activity(pref, "REFERRAL_JOINED", {"referred_user": uid})
                    try:
                        await context.bot.send_message(pref,
                            f"🎉 <b>NEW REFERRAL</b>\nUser: <code>{uid}</code>\nTotal: <code>{cnt}</code>",
                            parse_mode="HTML")
                    except: pass
            except: pass
            context.user_data["pending_refer"] = None
        await q.message.delete()
        await context.bot.send_message(uid, LANG_TEXTS[lang]["welcome"],
            parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    # Service picker
    if data.startswith("svc_"):
        idx = int(data.split("_",1)[1])
        svcs = context.user_data.get("la_services") or get_cached_services()
        if idx >= len(svcs):
            await q.answer("Expired.", show_alert=True); return
        svc = svcs[idx]; sid = svc.get("sid","Service"); rngs = svc.get("ranges",[])
        if not rngs:
            await q.answer("No ranges.", show_alert=True); return
        context.user_data["la_sid"] = sid; context.user_data["la_ranges"] = rngs
        await q.message.edit_text(
            LANG_TEXTS[get_user_lang(uid)]["pick_country"].format(sid=html.escape(sid)),
            parse_mode="HTML", reply_markup=_countries_kb(rngs, uid))
        return

    if data.startswith("rng_"):
        idx = int(data.split("_",1)[1])
        rngs = context.user_data.get("la_ranges",[])
        if idx >= len(rngs):
            await q.answer("Try again.", show_alert=True); return
        rng = rngs[idx]; sid = context.user_data.get("la_sid","")
        asyncio.create_task(fast_allocate_number(q, context, rng, sid))
        return

    if data == "custom_range":
        context.user_data["mode"] = "custom_range"
        await q.message.edit_text(
            LANG_TEXTS[get_user_lang(uid)]["custom_range_prompt"], parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                ikb("◀️ BACK", callback_data="back_services", style="danger")
            ]]))
        return

    if data == "back_services":
        svcs = get_cached_services() or context.user_data.get("la_services",[])
        if not svcs:
            await q.message.edit_text(f"{WARNING} Service list unavailable."); return
        context.user_data["la_services"] = svcs
        await q.message.edit_text(
            LANG_TEXTS[get_user_lang(uid)]["get_active_node"], parse_mode="HTML",
            reply_markup=_services_kb(svcs, uid))
        return

    if data == "same_range":
        rng = last_range.get(uid)
        if rng:
            try: await q.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([[ikb("⏳ Loading...", callback_data="noop")]]))
            except: pass
            await process_numbers(update, context, rng, 1)
        return

    if data == "noop": await q.answer()

    if data.startswith("copy_"):
        # tap-to-copy emulation: we display a copy-friendly format
        item = data.replace("copy_", "", 1)
        lang = get_user_lang(uid)
        txt = (f"📋 <b>{'Tap the number below and copy:' if lang=='en' else 'নিচের নম্বরটি কপি করুন:'}</b>\n\n"
               f"<code>{html.escape(item)}</code>")
        await q.answer("👆 Tap to copy", show_alert=False)
        try: await q.message.reply_text(txt, parse_mode="HTML")
        except: pass
        return

    if data.startswith("copyall_"):
        await q.answer("👆 Copy shown above.", show_alert=False)
        return

    if data.startswith("ref_link_"):
        await refer_cmd.__wrapped__(None) if False else None
        # just send refer message
        await context.bot.send_message(uid, "🎁 Use /start to see your invite link, or press 👥 REFER button.",
                                        reply_markup=main_keyboard(uid))
        return

    if data.startswith("my_history_"):
        await history_cmd(update, context)
        return

    # Withdraw
    if data == "withdraw_start":
        bal = get_user(uid)['balance']
        if bal < MIN_WITHDRAW:
            await q.message.reply_text(
                LANG_TEXTS[get_user_lang(uid)]["withdraw_min_err"].format(
                    bal=format_balance(bal), min_val=MIN_WITHDRAW),
                parse_mode="HTML"); return
        context.user_data["withdraw_mode"] = "select_method"
        await q.message.reply_text(LANG_TEXTS[get_user_lang(uid)]["withdraw_method_prompt"],
                                    reply_markup=withdraw_methods_kb(uid))
        return
    if data == "wd_confirm": await _wd_confirm(update, context); return
    if data == "wd_cancel":  await _wd_cancel(update, context);  return

    if data.startswith("adm_app_"): await _adm_approve(update, context, data.replace("adm_app_","")); return
    if data.startswith("adm_rej_"): await _adm_reject(update, context, data.replace("adm_rej_","")); return

    if data.startswith("fulldump_"):
        target = data.replace("fulldump_","")
        logs = load_data(ACTIVITY_LOGS_FILE)
        user_otps = [l for l in logs if str(l.get("uid"))==str(target) and l.get("action")=="OTP_RECEIVED"]
        body = (f"📊 PACKET ANALYSIS — {target}\n"
                f"💰 BAL: {format_balance(get_user(target).get('balance',0))} BDT\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\nOTP LOGS:\n")
        for i, l in enumerate(user_otps[-30:], 1):
            try:
                dt = datetime.fromisoformat(l['timestamp']); d = l.get('details',{})
                body += f"{i}. {dt.strftime('%d/%m/%Y %I:%M %p')} — 📟{d.get('number')} 🔑{d.get('otp')}\n"
            except: continue
        f = io.BytesIO(body.encode()); f.name = f"DUMP_{target}.txt"
        await q.message.reply_document(document=f, caption=f"📂 Dump for <code>{target}</code>", parse_mode="HTML")
        return

# ============================================================
#                  ⌨️ COMMAND HANDLERS ⌨️
# ============================================================
async def cmd_getnum(u, c): await show_app_selection(u, c)
async def cmd_search(u, c):
    uid = u.effective_user.id; lang = get_user_lang(uid)
    c.user_data["mode"] = "search_otp"
    await u.message.reply_text(LANG_TEXTS[lang]["search_otp_prompt"], parse_mode="HTML",
                               reply_markup=cancel_keyboard(uid))
async def cmd_balance(u, c):
    uid = u.effective_user.id; lang = get_user_lang(uid)
    await u.message.reply_text(f"💰 Balance: <code>{format_balance(get_user(uid)['balance'])} BDT</code>",
                               parse_mode="HTML", reply_markup=main_keyboard(uid))
async def cmd_profile(u, c): await profile_cmd(u, c)
async def cmd_history(u, c): await history_cmd(u, c)
async def cmd_leaderboard(u, c): await leaderboard_cmd(u, c)
async def cmd_2fa(u, c): await ask_2fa_key(u, c)

# ============================================================
#                  🚀 APP INITIALIZATION 🚀
# ============================================================
async def post_init(app):
    # Workers
    for _ in range(20):
        asyncio.create_task(worker_loop())
    asyncio.create_task(monitor_loop(app))
    asyncio.create_task(liveaccess_refresh_loop())
    # Bot commands menu
    await app.bot.set_my_commands([
        BotCommand("start","🚀 Start / Restart bot"),
        BotCommand("get1number","📲 Get a number"),
        BotCommand("searchotp","🔎 Search OTP"),
        BotCommand("2fa","🔑 Generate 2FA code"),
        BotCommand("balance","🪙 Check balance"),
        BotCommand("profile","👑 View profile"),
        BotCommand("history","📜 Your history"),
        BotCommand("leaderboard","🏆 Today's top 10"),
        BotCommand("refer","👥 Invite & earn"),
        BotCommand("withdraw","💸 Withdraw"),
        BotCommand("cancel","🛑 Cancel operation"),
        BotCommand("language","🌐 Change language"),
    ])

def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    print(f"{ACCENT} 🔶  STARTING NUMBER PANEL PRO BOT  🔶 {ACCENT}")
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("get1number", cmd_getnum))
    app.add_handler(CommandHandler("searchotp", cmd_search))
    app.add_handler(CommandHandler("2fa", cmd_2fa))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("profile", cmd_profile))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    app.add_handler(CommandHandler("refer", refer_cmd))
    app.add_handler(CommandHandler("withdraw", cmd_balance))
    app.add_handler(CommandHandler("language", lambda u,c: u.message.reply_text(
        "🌐 <b>Select language / ভাষা বাছাই করুন:</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            ikb("🇺🇸 English", callback_data="set_lang_en", style="primary"),
            ikb("🇧🇩 বাংলা", callback_data="set_lang_bn", style="success")
        ]]))))
    app.add_handler(CommandHandler("cancel", lambda u,c: (
        c.user_data.clear(),
        u.message.reply_text(f"{DANGER} Everything cancelled.", reply_markup=main_keyboard(u.effective_user.id))
    )))

    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"{SUCCESS} ✅ Bot is online")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
