import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = "8796073858:AAFAs8De-EKsS5Xp851U6QYcZ5m6cjM_z5Q"

user_emails = {}

def get_email(username):
    res = requests.get(f"https://api.guerrillamail.com/ajax.php?f=set_email_user&email_user={username}")
    data = res.json()
    return data["email_addr"], data["sid_token"]

def check_inbox(sid_token):
    res = requests.get(f"https://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token={sid_token}")
    return res.json().get("list", [])

def read_email(sid_token, mail_id):
    res = requests.get(f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={sid_token}")
    return res.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✏️ Custom Email Banao", callback_data="custom_email")],
        [InlineKeyboardButton("📧 Random Email Banao", callback_data="random_email")],
        [InlineKeyboardButton("📬 Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("🗑️ Email Delete Karo", callback_data="delete_email")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("FakeMail Bot mein swagat hai!\n\nNeeche se option chuno:", reply_markup=markup)

async def custom_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    context.user_data["waiting_for_username"] = True
    await query.message.reply_text("Apna pasandida username likho!\n\nJaise: yash123 ya coolboy456\n\n(Sirf letters aur numbers — koi space nahi!)")

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.user_data.get("waiting_for_username"):
        return
    username = update.message.text.strip().lower()
    if not username.isalnum():
        await update.message.reply_text("Sirf letters aur numbers use karo! Dobara try karo:")
        return
    context.user_data["waiting_for_username"] = False
    email, sid = get_email(username)
    user_emails[user_id] = {"email": email, "sid": sid}
    keyboard = [
        [InlineKeyboardButton("📬 Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("🗑️ Delete Karo", callback_data="delete_email")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"✅ Tera custom email ready hai!\n\n{email}\n\nYe email kisi ko bhi de sakte ho — unlimited use kar sakte ho!",
        reply_markup=markup
    )

async def random_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    res = requests.get("https://api.guerrillamail.com/ajax.php?f=get_email_address")
    data = res.json()
    email = data["email_addr"]
    sid = data["sid_token"]
    user_emails[user_id] = {"email": email, "sid": sid}
    keyboard = [
        [InlineKeyboardButton("📬 Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("🗑️ Delete Karo", callback_data="delete_email")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        f"✅ Tera random email:\n\n{email}\n\nUnlimited use karo!",
        reply_markup=markup
    )

async def inbox_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in user_emails:
        await query.message.reply_text("Pehle email banao!")
        return
    sid = user_emails[user_id]["sid"]
    email = user_emails[user_id]["email"]
    messages = check_inbox(sid)
    if not messages:
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="check_inbox")]]
        markup = InlineKeyboardMarkup(keyboard)