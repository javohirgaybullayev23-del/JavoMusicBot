import os
import telebot
from yt_dlp import YoutubeDL

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8628355750:AAGqT2SsTft1sfgnmRZfXMo--XMEJFSt3Tc')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men JavoMusic Botman 🎵\nQo'shiq nomini yozing, men uni topib MP3 formatda tashlab beraman!")

@bot.message_handler(func=lambda message: True)
def download_music(message):
    query = message.text
    msg = bot.reply_to(message, f"🔍 <b>{query}</b> qidirilmoqda...", parse_mode='HTML')
    
    filename = None
    
    # SoundCloud va boshqa ochiq platformalardan qidiradi (bloklanmaydi!)
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'scsearch1:',  # SoundCloud Search
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            file_id = video_info['id']
            title = video_info.get('title', 'Qo\'shiq')
            filename = f"{file_id}.mp3"

        bot.edit_message_text(f"📤 <b>{title}</b> yuklanmoqda...", message.chat.id, msg.message_id, parse_mode='HTML')
        
        with open(filename, 'rb') as audio:
            bot.send_audio(
                message.chat.id, 
                audio, 
                caption=f"🎵 <b>{title}</b>\n\n🤖 @JavoMusicBot orqali yuklandi", 
                parse_mode='HTML'
            )
            
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        print(f"Xatolik: {e}")
        bot.edit_message_text("❌ Kechirasiz, qo'shiq topilmadi. Boshqacha nom bilan qidirib ko'ring!", message.chat.id, msg.message_id)
        
    finally:
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass

if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.infinity_polling()
