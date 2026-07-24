import os
import requests
import telebot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8628355750:AAGqT2SsTft1sfgnmRZfXMo--XMEJFSt3Tc')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men JavoMusic Botman 🎵\nQo'shiq nomini yozing, men uni topib MP3 formatda tashlab beraman!")

@bot.message_handler(func=lambda message: True)
def download_music(message):
    query = message.text
    msg = bot.reply_to(message, f"🔍 <b>{query}</b> qidirilmoqda...", parse_mode='HTML')
    
    try:
        # 1. Deezer / Open API orqali qo'shiqni qidirish (IP bloklanmaydi)
        search_url = f"https://api.deezer.com/search?q={query}"
        response = requests.get(search_url).json()
        
        if not response.get('data'):
            bot.edit_message_text("❌ Kechirasiz, qo'shiq topilmadi. Boshqacha nom bilan qidirib ko'ring!", message.chat.id, msg.message_id)
            return

        track = response['data'][0]
        title = f"{track['artist']['name']} - {track['title']}"
        preview_url = track['preview'] # MP3 havola

        bot.edit_message_text(f"📤 <b>{title}</b> yuborilmoqda...", message.chat.id, msg.message_id, parse_mode='HTML')

        # 2. MP3 faylni ko'chirib olish va Telegram'ga yuborish
        audio_data = requests.get(preview_url).content
        
        bot.send_audio(
            message.chat.id,
            audio_data,
            title=track['title'],
            performer=track['artist']['name'],
            caption=f"🎵 <b>{title}</b>\n\n🤖 @JavoMusicBot orqali yuklandi",
            parse_mode='HTML'
        )
        
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        print(f"Xatolik: {e}")
        bot.edit_message_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring!", message.chat.id, msg.message_id)

if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.infinity_polling()
