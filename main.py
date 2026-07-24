import os
import requests
import telebot
from keep_alive import keep_alive

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8628355750:AAGqT2SsTft1sfgnmRZfXMo--XMEJFSt3Tc')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men JavoMusic Botman 🎵\nQo'shiq nomini yozing, men uni topib MP3 formatda tashlab beraman!")

@bot.message_handler(func=lambda message: True)
def download_music(message):
    query = message.text.strip()
    msg = bot.reply_to(message, f"🔍 <b>{query}</b> qidirilmoqda...", parse_mode='HTML')
    
    mp3_url = None
    title = query
    artist = "Music"

    # 1-Manba: Audio API
    try:
        api_url = f"https://api.vkmusic.ru/search?q={requests.utils.quote(query)}"
        res = requests.get(api_url, timeout=7).json()
        if 'data' in res and len(res['data']) > 0:
            track = res['data'][0]
            artist = track.get('artist', 'Artist')
            title = track.get('title', query)
            mp3_url = track.get('url')
    except Exception:
        pass

    # 2-Manba (Agar 1-manbadan topilmasa)
    if not mp3_url:
        try:
            api_url = f"https://hitmo.me/api/search?q={requests.utils.quote(query)}"
            res = requests.get(api_url, timeout=7).json()
            if 'tracks' in res and len(res['tracks']) > 0:
                track = res['tracks'][0]
                artist = track.get('artist', 'Artist')
                title = track.get('title', query)
                mp3_url = track.get('mp3')
        except Exception:
            pass

    # Qo'shiq topilgan bo'lsa yuborish
    if mp3_url:
        try:
            full_title = f"{artist} - {title}"
            bot.edit_message_text(f"📤 <b>{full_title}</b> yuklanmoqda...", message.chat.id, msg.message_id, parse_mode='HTML')

            bot.send_audio(
                message.chat.id,
                mp3_url,
                title=title,
                performer=artist,
                caption=f"🎵 <b>{full_title}</b>\n\n🤖 @JavoMusicBot orqali yuklandi",
                parse_mode='HTML'
            )
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            print(f"Yuborishda xatolik: {e}")
            bot.edit_message_text("❌ Qo'shiq faylini yuborishda xatolik bo'ldi. Qayta urinib ko'ring!", message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ Kechirasiz, bu nom bo'yicha qo'shiq topilmadi. Boshqacha yozib ko'ring!", message.chat.id, msg.message_id)

if __name__ == '__main__':
    keep_alive()
    print("Bot qo'shiqlarni izlashga tayyor...")
    bot.infinity_polling()
