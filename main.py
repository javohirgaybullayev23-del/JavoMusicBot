import os
import requests
import telebot
from keep_alive import keep_alive

# Telegram Bot Tokeni
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8628355750:AAGqT2SsTft1sfgnmRZfXMo--XMEJFSt3Tc')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Salom! Men JavoMusic Botman 🎵\n\n"
        "Istalgan xonanda yoki qo'shiq nomini yozing (masalan: <i>Janob Rasul</i>, <i>Miyagi</i>, <i>Billie Eilish</i>), "
        "men har qanday qo'shiqni topib MP3 formatda tashlab beraman!", 
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: True)
def download_any_music(message):
    query = message.text.strip()
    msg = bot.reply_to(message, f"🔍 <b>{query}</b> bo'yicha qo'shiq qidirilmoqda...", parse_mode='HTML')
    
    audio_url = None
    song_title = query
    artist_name = "JavoMusic"

    # 1-USUL: VK/Ochiq Musiqa Baza
    try:
        url = f"https://api.vkmusic.ru/search?q={requests.utils.quote(query)}"
        res = requests.get(url, timeout=7).json()
        if res and 'data' in res and len(res['data']) > 0:
            track = res['data'][0]
            audio_url = track.get('url')
            song_title = track.get('title', query)
            artist_name = track.get('artist', 'Ijrochi')
    except Exception:
        pass

    # 2-USUL: Zaxira Musiqa Serveri (1-usul topolmasa)
    if not audio_url:
        try:
            url = f"https://hitmo.me/api/search?q={requests.utils.quote(query)}"
            res = requests.get(url, timeout=7).json()
            if res and 'tracks' in res and len(res['tracks']) > 0:
                track = res['tracks'][0]
                audio_url = track.get('mp3')
                song_title = track.get('title', query)
                artist_name = track.get('artist', 'Ijrochi')
        except Exception:
            pass

    # 3-USUL: YouTube orqali MP3 izlash (Aksar hollarda eng aniq manba)
    if not audio_url:
        try:
            yt_search = f"https://inv.tux.im/api/v1/search?q={requests.utils.quote(query)}&type=video"
            yt_res = requests.get(yt_search, timeout=8).json()
            if yt_res and len(yt_res) > 0:
                video = yt_res[0]
                video_id = video.get('videoId')
                song_title = video.get('title', query)
                artist_name = video.get('author', 'YouTube')

                # MP3 ga o'giruvchi API
                dl_api = "https://co.wuk.sh/api/json"
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                payload = {"url": f"https://www.youtube.com/watch?v={video_id}", "isAudioOnly": True, "aFormat": "mp3"}
                
                dl_res = requests.post(dl_api, json=payload, headers=headers, timeout=12).json()
                if 'url' in dl_res:
                    audio_url = dl_res['url']
        except Exception:
            pass

    # YUKLAB BERISH QISMI
    if audio_url:
        try:
            full_name = f"{artist_name} - {song_title}"
            bot.edit_message_text(f"📤 <b>{full_name}</b> MP3 tayyorlanmoqda va yuborilmoqda...", message.chat.id, msg.message_id, parse_mode='HTML')

            bot.send_audio(
                message.chat.id,
                audio_url,
                title=song_title,
                performer=artist_name,
                caption=f"🎵 <b>{full_name}</b>\n\n🤖 @JavoMusicBot orqali yuklab olindi",
                parse_mode='HTML'
            )
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            print(f"Yuborishda xatolik: {e}")
            bot.edit_message_text("❌ MP3 faylni Telegram'ga yuklashda xatolik bo'ldi. Boshqa qo'shiq nomini yozib ko'ring!", message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ Kechirasiz, bu nom bo'yicha hech qanday qo'shiq topilmadi. Qo'shiqchi yoki qo'shiq nomini to'g'rilab yozib ko'ring!", message.chat.id, msg.message_id)

if __name__ == '__main__':
    keep_alive()
    print("Bot har qanday qo'shiqni qidirishga tayyor...")
    bot.infinity_polling()
