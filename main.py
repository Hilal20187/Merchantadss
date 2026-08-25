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
    
    if chat_id != ADMIN_GROUP_ID or user_id not in AUTHORIZED_USER_IDS:
        return

    message = update.message
    if not message:
        return

    for group_id in TARGET_GROUP_IDS:
        try:
            await context.bot.copy_message(
                chat_id=group_id,
                from_chat_id=chat_id,
                message_id=message.message_id
            )
            logging.info(f"تم بنجاح النشر إلى المجموعة: {group_id}")
        except Exception as e:
            logging.error(f"فشل النشر إلى المجموعة {group_id}: {e}")

def run_bot():
    if not TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN!")
        return
    
    # بناء تطبيق البوت
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.SUPERGROUP & filters.ALL, handle_announcement))
    
    print("البوت بدأ الاستماع للرسائل...")
    # تشغيل البوت بطريقة تضمن عدم توقف السيرفر
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# إعداد سيرفر الويب الوهمي ليبقى مجانياً على Render
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # تشغيل البوت في مسار (Thread) مستقل
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # تشغيل سيرفر الويب الرئيسي
    run_server()
 
