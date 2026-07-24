import os
import requests
import telebot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8628355750:AAGqT2SsTft1sfgnmRZfXMo--XMEJFSt3Tc')
bot = telebot.TeleBot(TOKEN)

# Invidious ochiq YouTube proksi serverlari
INVIDIOUS_INSTANCES = [
    "https://invidious.nerdvpn.de",
    "https://inv.tux.stream",
    "https://invidious.drgns.space"
]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men JavoMusic Botman 🎵\nQo'shiq nomini yozing, men uni topib MP3 formatda tashlab beraman!")

@bot.message_handler(func=lambda message: True)
def download_music(message):
    query = message.text
    msg = bot.reply_to(message, f"🔍 <b>{query}</b> qidirilmoqda...", parse_mode='HTML')
    
    search_results = None
    # Serverlardan biri ishlamasa, keyingisiga o'tadi
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"{instance}/api/v1/search?q={requests.utils.quote(query)}&type=video"
            res = requests.get(url, timeout=7)
            if res.status_code == 200 and len(res.json()) > 0:
                search_results = res.json()
                break
        except Exception:
            continue

    if not search_results:
        bot.edit_message_text("❌ Kechirasiz, qo'shiq topilmadi yoki tarmoqda xatolik bo'ldi. Qaytadan urinib ko'ring!", message.chat.id, msg.message_id)
        return

    first_video = search_results[0]
    title = first_video.get('title', 'Qo\'shiq')
    video_id = first_video.get('videoId')

    bot.edit_message_text(f"📤 <b>{title}</b> yuklanmoqda...", message.chat.id, msg.message_id, parse_mode='HTML')

    # Audio faylni proksi orqali xavfsiz olish
    audio_url = f"https://yt.drgnz.club/latest/http://invidious.nerdvpn.de/latest/https://www.youtube.com/watch?v={video_id}"
    
    # Kobalt / Invidious audio havolasi
    stream_url = f"https://co.wuk.sh/api/json"
    payload = {
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "isAudioOnly": True,
        "aFormat": "mp3"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(stream_url, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        if "url" in res_data:
            download_link = res_data["url"]
            bot.send_audio(
                message.chat.id,
                download_link,
                title=title,
                caption=f"🎵 <b>{title}</b>\n\n🤖 @JavoMusicBot orqali yuklandi",
                parse_mode='HTML'
            )
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ MP3 tayyorlashda xatolik bo'ldi. Qayta urinib ko'ring!", message.chat.id, msg.message_id)

    except Exception as e:
        print(f"Xatolik: {e}")
        bot.edit_message_text("❌ Server bilan bog'lanishda xatolik yuz berdi.", message.chat.id, msg.message_id)

if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.infinity_polling()
