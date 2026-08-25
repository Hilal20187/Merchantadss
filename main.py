import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# قراءة الـ Token أماناً من متغيرات البيئة في المنصة
TOKEN = os.getenv("BOT_TOKEN")

# ضع هنا معرفات الحسابات المسموح لها بالتنفيذ (أنت وأصدقاؤك)
AUTHORIZED_USER_IDS = [123456789, 987654321]  # استبدل هذه الأرقام بمعرفاتكم الحقيقية

# ضع هنا معرفات المجموعات التي تريد النشر فيها (Chat IDs)
TARGET_GROUP_IDS = [-1001234567890, -1009876543210]  # استبدل هذه الأرقام بمعرفات مجموعاتكم

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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

def main():
    if not TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN في متغيرات البيئة!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.ALL, handle_message))

    print("البوت يعمل الآن على السحابة بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
