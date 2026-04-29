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
