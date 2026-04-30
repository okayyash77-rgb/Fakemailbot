import requests
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = "8796073858:AAFAs8De-EKsS5Xp851U6QYcZ5m6cjM_z5Q"

user_emails = {}

def get_email(username):
    return username + "@di2.in", username

def check_inbox(username):
    res = requests.get("https://maildrop.cc/v2/mailbox/" + username)
    data = res.json()
    if isinstance(data, list):
        return data
    return []

def read_email(username, mail_id):
    res = requests.get("https://maildrop.cc/v2/mailbox/" + username + "/" + str(mail_id))
    return res.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✏️ Custom Email Banao", callback_data="custom_email")],
        [InlineKeyboardButton("📧 Random Email Banao", callback_data="random_email")],
        [InlineKeyboardButton("📬 Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("🗑️ Email Delete Karo", callback_data="delete_email")],
        [InlineKeyboardButton("📢 Channel Join Karo", url="https://t.me/fmSupportChannel")],
        [InlineKeyboardButton("💬 Support Group", url="https://t.me/fmSupportGc")],
        [InlineKeyboardButton("👤 Admin Contact", url="https://t.me/ShanksMm")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔐 FakeMail Bot mein swagat hai!\n\n"
        "📧 Apna custom ya random email banao\n"
        "✅ Kisi bhi website pe use karo\n"
        "🛡️ Spam se bachao apni privacy!\n\n"
        "Neeche se option chuno:",
        reply_markup=markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Channel", url="https://t.me/fmSupportChannel")],
        [InlineKeyboardButton("💬 Support Group", url="https://t.me/fmSupportGc")],
        [InlineKeyboardButton("👤 Admin", url="https://t.me/ShanksMm")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🆘 Help Menu\n\n"
        "✏️ Custom Email - Apne naam se email banao\n"
        "📧 Random Email - Random email banao\n"
        "📬 Inbox - Emails dekho\n"
        "🗑️ Delete - Email delete karo\n\n"
        "💡 Tip: Email kisi ko bhi de sakte ho!\n"
        "📧 Domain: @di2.in",
        reply_markup=markup
    )

async def custom_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["waiting"] = True
    await query.message.reply_text(
        "✏️ Apna username likho!\n\n"
        "Jaise: yash123\n\n"
        "Tumhara email banega: yash123@di2.in"
    )

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.user_data.get("waiting"):
        return
    username = update.message.text.strip().lower()
    context.user_data["waiting"] = False
    email, sid = get_email(username)
    user_emails[user_id] = {"email": email, "sid": sid}
    keyboard = [
        [InlineKeyboardButton("📬 Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("🗑️ Delete Karo", callback_data="delete_email")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/fmSupportChannel")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/fmSupportGc")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ Tera email ready hai!\n\n" + email + "\n\nUnlimited use karo!",
        reply_markup=markup
    )

async def random_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email, sid = get_email(username)
    user_emails[user_id] = {"email": email, "sid": sid}
    keyboard = [
        [InlineKeyboardButton("📬 Inbox Check Karo", callback_data="check_inbox")],
        [InlineKeyboardButton("🗑️ Delete Karo", callback_data="delete_email")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/fmSupportChannel")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/fmSupportGc")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "✅ Tera random email:\n\n" + email + "\n\nUnlimited use karo!",
        reply_markup=markup
    )

async def inbox_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in user_emails:
        await query.message.reply_text("⚠️ Pehle email banao!")
        return
    sid = user_emails[user_id]["sid"]
    email = user_emails[user_id]["email"]
    messages = check_inbox(sid)
    if not messages:
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="check_inbox")],
            [InlineKeyboardButton("🗑️ Delete Karo", callback_data="delete_email")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("📭 " + email + " ka inbox khali hai.", reply_markup=markup)
        return
    for msg in messages[:5]:
        keyboard = [[InlineKeyboardButton("📖 Read karo", callback_data="read_" + str(msg["id"]))]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "📩 From: " + str(msg.get("origfrom", "Unknown")) + "\nSubject: " + str(msg.get("subject", "No subject")),
            reply_markup=markup
        )

async def read_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    mail_id = query.data.split("_")[1]
    if user_id not in user_emails:
        await query.message.reply_text("⚠️ Pehle email banao!")
        return
    sid = user_emails[user_id]["sid"]
    msg = read_email(sid, mail_id)
    body = msg.get("body") or "Content nahi mila"
    body = body[:1000]
    await query.message.reply_text(
        "📧 From: " + str(msg.get("origfrom", "Unknown")) + "\nSubject: " + str(msg.get("subject", "No subject")) + "\n\n" + body
    )

async def delete_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id in user_emails:
        email = user_emails[user_id]["email"]
        del user_emails[user_id]
        keyboard = [
            [InlineKeyboardButton("📧 Naya Email Banao", callback_data="random_email")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/fmSupportChannel")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/fmSupportGc")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🗑️ " + email + " delete ho gaya!\n\nAb naya email bana sakte ho!", reply_markup=markup)
    else:
        await query.message.reply_text("⚠️ Koi email nahi hai!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
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
