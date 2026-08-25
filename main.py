import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")

# معرفات الأصدقاء المصرح لهم
AUTHORIZED_USER_IDS = [822007358, 2065539959]

# مجموعة الإدارة الخاصة بكم
ADMIN_GROUP_ID = -1003963584914

# المجموعات المستهدفة للنشر
TARGET_GROUP_IDS = [-1003952714985, -1002470205630, -1004407774851]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def handle_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التأكد من أن الرسالة من مجموعة الإدارة ومن أحد الأصدقاء المصرح لهم
    if chat_id != ADMIN_GROUP_ID or user_id not in AUTHORIZED_USER_IDS:
        return

    message = update.message
    if not message:
        return

    # نشر الرسالة إلى كل المجموعات المستهدفة
    for group_id in TARGET_GROUP_IDS:
        try:
            await context.bot.copy_message(
                chat_id=group_id,
                from_chat_id=chat_id,
                message_id=message.message_id
            )
        except Exception as e:
            logging.error(f"فشل النشر إلى المجموعة {group_id}: {e}")

def run_bot():
    if not TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN!")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    
    # استقبال الرسائل داخل المجموعات
    app.add_handler(MessageHandler(filters.ChatType.SUPERGROUP & filters.ALL, handle_announcement))
    
    print("البوت يعمل الآن...")
    app.run_polling()

app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    run_server()

 
