import os
import logging
from telethon import TelegramClient, events
from flask import Flask
import threading

# قراءة المتغيرات الأساسية (يمكنك تعديلها هنا مباشرة أو تركها تسحب من البيئة)
API_ID = int(os.getenv("API_ID", "0"))  # ضع api_id الخاص بك هنا إذا لم تستعمل البيئة
API_HASH = os.getenv("API_HASH", "")    # ضع api_hash الخاص بك هنا
BOT_TOKEN = os.getenv("BOT_TOKEN")

# معرفات الأشخاص المسموح لهم فقط بنشر الإعلانات أو التحكم
AUTHORIZED_USER_IDS = [822007358, 2065539959]

# معرف مجموعة الإدارة الخاص بك
ADMIN_GROUP_ID = -1003963584914

# المجموعات المستهدفة للنشر
TARGET_GROUP_IDS = [-1003952714985, -1002470205630, -1004407774851]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تهيئة عميل تيليتون للبوت
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage)
async def handle_announcement(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    
    if not sender or sender.id not in AUTHORIZED_USER_IDS:
        return

    text = event.raw_text or ""

    # 1. معالجة أمر الحذف /del (سواء كتب وحده أو متبوعاً بمعرف البوت)
    if text.strip().startswith('/del'):
        try:
            # حذف الرسالة التي تم الرد عليها (Reply) إن وجدت
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                await reply_msg.delete()
            
            # حذف أمر /del نفسه
            await event.delete()
            logging.info("تم تنفيذ أمر الحذف بنجاح عبر Telethon.")
        except Exception as e:
            logging.error(f"فشل تنفيذ أمر الحذف: {e}")
        return

    # 2. منطق نشر الإعلانات (يقتصر حصرياً على مجموعة الإدارة)
    if chat.id != ADMIN_GROUP_ID:
        return

    # إعادة إرسال الرسالة (سواء نص أو صورة) إلى كل المجموعات المستهدفة
    for group_id in TARGET_GROUP_IDS:
        try:
            await client.send_message(group_id, event.message)
            logging.info(f"تم بنجاح نشر الإعلان في المجموعة: {group_id}")
        except Exception as e:
            logging.error(f"فشل النشر إلى المجموعة {group_id}: {e}")

def run_bot():
    if not BOT_TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN!")
        return
    print("البوت يعمل ويتلتقط كافة الرسائل والأوامر عبر Telethon...")
    client.run_until_disconnected()

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
