import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
import threading

# --- إعدادات البوت ---
TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USER_IDS = [123456789, 987654321] # استبدل بمعرفاتكم
TARGET_GROUP_IDS = [-1001234567890, -1009876543210] # استبدل بمعرفات المجموعات

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- دالة معالجة الرسائل (البوت) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USER_IDS:
        return
    message = update.message
    if not message:
        return
    for group_id in TARGET_GROUP_IDS:
        try:
            await context.bot.copy_message(
                chat_id=group_id,
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )
        except Exception as e:
            logging.error(f"فشل الإرسال إلى المجموعة {group_id}: {e}")

def run_bot():
    if not TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN!")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.ALL, handle_message))
    print("البوت يعمل الآن...")
    app.run_polling()

# --- إعداد السيرفر الوهمي (Web Service) لجعله مجانياً على Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_server():
    # Render يعطي البورت عبر متغير PORT، وإلا نستخدم 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # تشغيل البوت في خيط (Thread) منفصل
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل السيرفر الوهمي
    run_server()
 
