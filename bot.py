export default {
  async email(message, env, ctx) {
    // 1. Apni details yahan dalo
    const apiToken = "8796073858:AAFAs8De-EKsS5Xp851U6QYcZ5m6cjM_z5Q"; 
    const chatId = "8475127861";       
    
    // 2. Email ki details nikalna
    const subject = message.headers.get("subject") || "No Subject";
    const from = message.from;
    
    // 3. Email ki body padhna
    const reader = message.raw.getReader();
    const { value } = await reader.read();
    const body = new TextDecoder().decode(value);
    
    // 4. OTP nikalne ka logic (4 se 6 digit ke number)
    const otpMatch = body.match(/\d{4,6}/);
    const otp = otpMatch ? otpMatch[0] : "OTP nahi mila";

    // 5. Telegram par bhejne wala message
    const text = `📩 *Naya Mail Aaya!* \n\n*From:* ${from}\n*Subject:* ${subject}\n*OTP:* ${otp}\n\n*Domain:* di2.in`;

    // 6. Telegram API ko call karna
    await fetch(`https://api.telegram.org/bot${apiToken}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
        parse_mode: "Markdown"
      })
    });
  }
}
