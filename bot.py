import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = "8796073858:AAFAs8De-EKsS5Xp851U6QYcZ5m6cjM_z5Q"

user_emails = {}

def get_email(username):
    res = requests.get("https://api.guerrillamail.com/ajax.php?f=set_email_user&email_user=" + username)
    data = res.json()
    return data["email_addr"], data["sid_token"]

def check_inbox(sid_token):
    res = requests.get("https://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token=" + sid_token)
    return res.json().get("list", [])

def read_email(sid_token, mail_id):
    res = requests.get("https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id=" + str(mail_id) + "&sid_token=" + sid_token)
    return res.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Custom Email Banao", callback_data="custom_email")],
        [InlineKeyboardButton("Random Email Banao", callback_data="random_email")],
        [InlineKeyboardButton("Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("Email Delete Karo", callback_data="delete_email")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("FakeMail Bot mein swagat hai! Neeche se option chuno:", reply_markup=markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Help Menu\n\nCustom Email - Apne naam se email banao\nRandom Email - Random email banao\nInbox - Emails dekho\nDelete - Email delete karo\n\nTip: Email kisi ko bhi de sakte ho!")

async def custom_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["waiting_for_username"] = True
    await query.message.reply_text("Apna username likho! Jaise: yash123 ya coolboy456\n\nSirf letters aur numbers!")

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.user_data.get("waiting_for_username"):
        return
    username = update.message.text.strip().lower()
    if not username.isalnum():
        await update.message.reply_text("Sirf letters aur numbers use karo!")
        return
    context.user_data["waiting_for_username"] = False
    email, sid = get_email(username)
    user_emails[user_id] = {"email": email, "sid": sid}
    keyboard = [
        [InlineKeyboardButton("Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("Delete Karo", callback_data="delete_email")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Tera custom email ready hai!\n\n" + email + "\n\nUnlimited use karo!", reply_markup=markup)

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
        [InlineKeyboardButton("Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("Delete Karo", callback_data="delete_email")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Tera random email:\n\n" + email + "\n\nUnlimited use karo!", reply_markup=markup)

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
        keyboard = [[InlineKeyboardButton("Refresh", callback_data="check_inbox")]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(email + " ka inbox khali hai abhi.", reply_markup=markup)
        return
    for msg in messages[:5]:
        keyboard = [[InlineKeyboardButton("Read karo", callback_data="read_" + str(msg["mail_id"]))]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("From: " + msg["mail_from"] + "\nSubject: " + msg["mail_subject"], reply_markup=markup)

async def read_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    mail_id = query.data.split("_")[1]
    if user_id not in user_emails:
        await query.message.reply_text("Pehle email banao!")
        return
    sid = user_emails[user_id]["sid"]
    msg = read_email(sid, mail_id)
    body = msg.get("mail_body") or "Content nahi mila"
    body = body[:1000]
    await query.message.reply_text("From: " + str(msg.get("mail_from")) + "\nSubject: " + str(msg.get("mail_subject")) + "\n\n" + body)

async def delete_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id in user_emails:
        email = user_emails[user_id]["email"]
        del user_emails[user_id]
        keyboard = [[InlineKeyboardButton("Naya Email Banao", callback_data="random_email")]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(email + " delete ho gaya! Ab naya email bana sakte ho!", reply_markup=markup)
    else:
        await query.message.reply_text("Koi email nahi hai abhi!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("newemail", random_email))
    app.add_handler(CallbackQueryHandler(custom_email, pattern="custom_email"))
    app.add_handler(CallbackQueryHandler(random_email, pattern="random_email"))
    app.add_handler(CallbackQueryHandler(inbox_check, pattern="check_inbox"))
    app.add_handler(CallbackQueryHandler(read_message, pattern="read_"))
    app.add_handler(CallbackQueryHandler(delete_email, pattern="delete_email"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    print("Bot chal raha hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
