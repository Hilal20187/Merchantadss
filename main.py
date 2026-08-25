import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")

# معرفات الأشخاص المسموح لهم فقط بالنشر (أنت وصديقك)
AUTHORIZED_USER_IDS = [822007358, 2065539959]

# معرف مجموعة الإدارة الخاصة بكم (كمجموعة Supergroup)
ADMIN_GROUP_ID = -1003963584914

# المجموعات المستهدفة للنشر
TARGET_GROUP_IDS = [-1003952714985, -1002470205630, -1004407774851]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def handle_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat or chat.id != ADMIN_GROUP_ID:
        return

    # التحقق من المرسل (يجب أن يكون أحد الأشخاص المصرح لهم حصرياً)
    user = update.effective_user
    if not user or user.id not in AUTHORIZED_USER_IDS:
        return

    message = update.effective_message
    if not message:
        return

    text_to_send = message.text or message.caption
    photo = message.photo

    for group_id in TARGET_GROUP_IDS:
        try:
            if photo:
                await context.bot.send_photo(
                    chat_id=group_id,
                    photo=photo[-1].file_id,
                    caption=text_to_send or ""
                )
            elif text_to_send:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=text_to_send
                )
            logging.info(f"تم بنجاح نشر الإعلان في المجموعة: {group_id}")
        except Exception as e:
            logging.error(f"فشل النشر إلى المجموعة {group_id}: {e}")

def run_bot():
    if not TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN!")
        return
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # الاستماع لرسائل المجموعات فقط لضمان دقة معرفات المستخدمين
    application.add_handler(MessageHandler(filters.ChatType.SUPERGROUP & filters.ALL, handle_announcement))
    
    print("البوت يعمل ويتحقق من صلاحياتك بدقة داخل المجموعة...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    run_server()
