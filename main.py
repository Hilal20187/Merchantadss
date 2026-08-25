import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
import threading

# --- إعدادات البوت ---
TOKEN = os.getenv("BOT_TOKEN")

# معرفات الأصدقاء والمسموح لهم بالتحكم (أنت وأصدقاؤك)
AUTHORIZED_USER_IDS = [822007358, 2065539959]

# معرفات المجموعات المستهدفة للنشر
TARGET_GROUP_IDS = [-1003952714985, -1002470205630, -1004407774851]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- دالة معالجة الرسائل (البوت) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # التحقق من أن المرسل مسموح له
    if user_id not in AUTHORIZED_USER_IDS:
        return

    message = update.message
    if not message:
        return

    # نسخ الرسالة إلى المجموعات المحددة
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

# --- إعداد السيرفر الوهمي (Web Service) لبقائه مجانياً على Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # تشغيل البوت في الخلفية
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل السيرفر
    run_server()
 
