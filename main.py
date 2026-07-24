import os
import telebot
from yt_dlp import YoutubeDL

# Bot Token
TOKEN = "8628355750:AAGqT2SsTft1sfgnmRZfXMo--XMEJFSt3Tc"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    start_text = (
        "🎮 <b>JAVOMUSIC BOT ISHGA TUSHDI!</b> 🎮\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👾 <i>2D Audio Search Engine Active!</i>\n\n"
        "🎵 Menga istalgan qo'shiq nomini yozing!\n"
        "<i>Masalan: <b>Mirjalol Nematov anor</b></i>\n\n"
        "⚡️ Men uni YouTube'dan toza <b>MP3 formatda</b> topib beraman!"
    )
    bot.send_message(message.chat.id, start_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def search_and_download(message):
    query = message.text
    msg = bot.reply_to(
        message, 
        f"🔍 <b>[2D SEARCH]</b> <i>'{query}' YouTube'dan qidirilmoqda va yuklanmoqda...</i>", 
        parse_mode="HTML"
    )
    
    # Faylni vaqtinchalik saqlash joyi va nomi
    output_template = "downloads/%(id)s.%(ext)s"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    filename_mp3 = None

    try:
        os.makedirs("downloads", exist_ok=True)
        with YoutubeDL(ydl_opts) as ydl:
            # YouTube'dan ma'lumotni olamiz
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]
                
            # YouTube'dagi AYNAN to'liq nomini olamiz
            youtube_title = info.get('title', 'Audio')
            channel_name = info.get('uploader', 'YouTube')
            
            # Fayl nomini aniqlaymiz
            base_filename = ydl.prepare_filename(info)
            filename_mp3 = os.path.splitext(base_filename)[0] + ".mp3"

        # MP3 faylni yuborish (YouTube tagidagi asl nomi bilan!)
        with open(filename_mp3, 'rb') as audio:
            bot.send_audio(
                chat_id=message.chat.id, 
                audio=audio, 
                title=youtube_title,        # YouTube'dagi sarlavha
                performer=channel_name,     # Kanal nomi
                caption=(
                    f"🎧 <b>{youtube_title}</b>\n\n"
                    f"👤 <b>Kanal:</b> {channel_name}\n"
                    f"✨ <i>@JavoMusicBot orqali yuklandi</i>"
                ),
                parse_mode="HTML"
            )
        
        # "Qidirilmoqda..." degan xabarni o'chiramiz
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            f"❌ Kechirasiz, qo'shiq topilmadi yoki FFmpeg bilan bog'liq xatolik yuz berdi!\n\n`{e}`", 
            message.chat.id, 
            msg.message_id,
            parse_mode="Markdown"
        )
        print(f"Xatolik: {e}")

    finally:
        # Kompyuterdagi vaqtincha saqlangan MP3 faylni o'chirish (joy to'lib ketmasligi uchun)
        if filename_mp3 and os.path.exists(filename_mp3):
            os.remove(filename_mp3)

print("👾 JavoMusic Bot kompyuterda tayyor va ishlamoqda!")
bot.infinity_polling()
