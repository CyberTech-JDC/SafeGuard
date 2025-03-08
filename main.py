Python 3.13.2 (tags/v3.13.2:4f8bb39, Feb  4 2025, 15:23:48) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import telebot
... import requests
... import json
... 
... BOT_TOKEN = "7990927398:AAGt1gyLqFaukoPK4wDGvjlKO83zNlCix5Y"
... FIREBASE_URL = "https://safeguard-alert-default-rtdb.firebaseio.com/"
... 
... bot = telebot.TeleBot(BOT_TOKEN)
... 
... @bot.message_handler(commands=['register'])
... def register_user(message):
...     chat_id = message.chat.id
...     update_firebase(chat_id)
...     bot.send_message(chat_id, "✅ Registered successfully! You will now receive alerts.")
... 
... def update_firebase(chat_id):
...     data = json.dumps(chat_id)  # Store chat_id as a simple value
...     response = requests.put(FIREBASE_URL, data)
...     
...     if response.status_code == 200:
...         print(f"✅ Chat ID {chat_id} updated in Firebase")
...     else:
...         print("❌ Failed to update Firebase")
... 
... bot.polling()
