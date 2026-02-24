import telebot
import anthropic
from telebot import types

# =============================
# TOKENLARNI BU YERGA KIRITING
# =============================
TELEGRAM_TOKEN = "7861770184:AAH-a48RvYf-er0_JfhGtYHY0nBOMPDRD40"
CLAUDE_API_KEY = "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"
# =============================

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Har bir foydalanuvchi uchun suhbat tarixi
chat_history = {}

# ─────────────────────────────
# ASOSIY MENYU TUGMALARI
# ─────────────────────────────
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("💬 Suhbat")
    btn2 = types.KeyboardButton("❓ Yordam")
    btn3 = types.KeyboardButton("🔄 Suhbatni tozalash")
    btn4 = types.KeyboardButton("ℹ️ Bot haqida")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# ─────────────────────────────
# /start KOMANDASI
# ─────────────────────────────
@bot.message_handler(commands=['start'])
def start(message):
    chat_history[message.chat.id] = []
    name = message.from_user.first_name
    text = (
        f"Assalomu alaykum, {name}! 👋\n\n"
        "Men Claude AI yordamida ishlaydigan aqlli botman 🤖\n"
        "Istalgan savolingizni yozing, javob beraman!\n\n"
        "👇 Quyidagi tugmalardan foydalaning:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# ─────────────────────────────
# /help KOMANDASI
# ─────────────────────────────
@bot.message_handler(commands=['help'])
def help_command(message):
    show_help(message)

# ─────────────────────────────
# TUGMALAR HANDLE
# ─────────────────────────────
@bot.message_handler(func=lambda m: m.text in [
    "💬 Suhbat", "❓ Yordam", "🔄 Suhbatni tozalash", "ℹ️ Bot haqida"
])
def handle_buttons(message):
    if message.text == "💬 Suhbat":
        bot.send_message(
            message.chat.id,
            "Yaxshi! Savolingizni yozing, javob beraman 😊",
            reply_markup=main_menu()
        )

    elif message.text == "❓ Yordam":
        show_help(message)

    elif message.text == "🔄 Suhbatni tozalash":
        chat_history[message.chat.id] = []
        bot.send_message(
            message.chat.id,
            "✅ Suhbat tarixi tozalandi! Yangi suhbat boshlashingiz mumkin.",
            reply_markup=main_menu()
        )

    elif message.text == "ℹ️ Bot haqida":
        text = (
            "🤖 *Bu bot haqida:*\n\n"
            "• AI: Claude (Anthropic)\n"
            "• Til: O'zbek tili\n"
            "• Imkoniyat: Suhbat tarixi eslab qolinadi\n"
            "• Yaratuvchi: Siz! 😄\n\n"
            "Savollar uchun /help"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

# ─────────────────────────────
# YORDAM FUNKSIYASI
# ─────────────────────────────
def show_help(message):
    text = (
        "📖 *Yordam:*\n\n"
        "• Istalgan savolingizni yozing\n"
        "• Bot Claude AI orqali javob beradi\n"
        "• Bot oldingi xabarlarni eslab qoladi\n\n"
        "*Komandalar:*\n"
        "/start — Botni qayta ishga tushirish\n"
        "/help — Yordam\n\n"
        "*Tugmalar:*\n"
        "💬 Suhbat — Suhbat boshlash\n"
        "🔄 Suhbatni tozalash — Tarixni o'chirish\n"
        "ℹ️ Bot haqida — Ma'lumot"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

# ─────────────────────────────
# CLAUDE AI JAVOB
# ─────────────────────────────
@bot.message_handler(func=lambda m: True)
def claude_reply(message):
    user_id = message.chat.id

    if user_id not in chat_history:
        chat_history[user_id] = []

    # Foydalanuvchi xabarini qo'shamiz
    chat_history[user_id].append({
        "role": "user",
        "content": message.text
    })

    # Yuklanyapti xabari
    loading_msg = bot.send_message(user_id, "⏳ Javob tayyorlanmoqda...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=(
                "Sen foydali, do'stona va aqlli yordamchisan. "
                "Har doim O'zbek tilida javob ber. "
                "Javoblarni qisqa va aniq qilib yoz. "
                "Kerak bo'lsa emoji ishlat."
            ),
            messages=chat_history[user_id]
        )

        answer = response.content[0].text

        # Javobni tarixga qo'shamiz
        chat_history[user_id].append({
            "role": "assistant",
            "content": answer
        })

        # Yuklanyapti xabarini o'chirib, javob yuboramiz
        bot.delete_message(user_id, loading_msg.message_id)
        bot.send_message(user_id, answer, reply_markup=main_menu())

    except Exception as e:
        bot.delete_message(user_id, loading_msg.message_id)
        bot.send_message(
            user_id,
            "❌ Xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
            reply_markup=main_menu()
        )
        print(f"Xatolik: {e}")

# ─────────────────────────────
# BOTNI ISHGA TUSHIRISH
# ─────────────────────────────
print("✅ Bot ishga tushdi!")
bot.polling(none_stop=True)
