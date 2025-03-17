import telebot
import requests
import json
from flask import Flask

# ✅ Define Flask app
app = Flask(__name__)

BOT_TOKEN = "7990927398:AAHn1vCsyBQVFfaKT34cXI-IjqBvvHbQC-I"
FIREBASE_URL = "https://safeguard-alert-default-rtdb.firebaseio.com"

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Store temporary chat states
user_states = {}


# ✅ Route for UptimeRobot
@app.route('/')
def home():
    return "Bot is running!"


@bot.message_handler(commands=['register'])
def register_user(message):
    chat_id = str(message.chat.id)  # Convert to string
    first_name = message.from_user.first_name  # Get first name

    print(
        f"📩 Received /register command from {first_name} (Chat ID: {chat_id})")

    success = update_firebase(chat_id,
                              first_name)  # Save latest chat ID & name

    if success:
        try:
            bot.send_message(
                chat_id,
                f"✅ SafeGuard: Senior Citizen Alert for Fall and Essential Geriatric Assessment and Detection Belt ✅\n\n"
                f"Hello {first_name}, you have been successfully registered as a healthcare provider! \n\n"
                "You will now receive real-time alerts and important notifications "
                "to ensure the safety and well-being of your patients. Stay safe! 🚨"
            )
            print(f"📤 Sent confirmation message to {first_name} ({chat_id})")
        except Exception as e:
            print(f"❌ Failed to send message to {chat_id}: {e}")
    else:
        print(f"⚠️ Skipping message sending due to Firebase update failure.")


@bot.message_handler(commands=['setname'])
def ask_patient_name(message):
    """Step 1: Ask for the patient's name."""
    chat_id = str(message.chat.id)  # Ensure chat_id is a string

    bot.send_message(chat_id, "📝 Please provide the name of the patient.")

    # ✅ Properly store the state
    user_states[chat_id] = "awaiting_name"
    print(f"🔄 Waiting for patient name from {chat_id}")


@bot.message_handler(func=lambda message: str(message.chat.id) in user_states
                     and user_states[str(message.chat.id)] == "awaiting_name")
def set_patient_name(message):
    """Step 2: Save the provided patient name."""
    chat_id = str(message.chat.id)
    patient_name = message.text.strip()  # Get name input

    if not patient_name:  # Check if empty
        bot.send_message(chat_id,
                         "⚠ The name cannot be empty. Please try again.")
        return

    print(f"📩 Received patient name: {patient_name} from {chat_id}")

    # ✅ Update Firebase with the patient's name
    data = json.dumps({"patient_name": patient_name})
    firebase_path = f"{FIREBASE_URL}/.json"  # Update root level

    try:
        response = requests.patch(firebase_path, data)
        if response.status_code == 200:
            bot.send_message(
                chat_id,
                f"✅ Patient's name has been successfully updated to: {patient_name}."
            )
            print(f"✅ Updated patient name in Firebase: {patient_name}")
        else:
            bot.send_message(
                chat_id, "❌ Failed to update name. Please try again later.")
            print(f"❌ Firebase error: {response.text}")
    except requests.exceptions.RequestException as e:
        bot.send_message(chat_id,
                         "🚨 Error updating Firebase. Please try again later.")
        print(f"🚨 Error: {e}")

    # ✅ Remove state after success
    user_states.pop(chat_id, None)


# ✅ New handler for /locatepatient command
@bot.message_handler(commands=['locatepatient'])
def locate_patient(message):
    chat_id = str(message.chat.id)  # Ensure chat_id is a string

    print(f"📩 Received /locatepatient command from {chat_id}")

    # Fetch location data from Firebase
    firebase_path = f"{FIREBASE_URL}/gps.json"
    try:
        response = requests.get(firebase_path)
        if response.status_code == 200:
            gps_data = response.json()

            # Ensure gps data exists
            if gps_data and "lat" in gps_data and "lng" in gps_data:
                latitude = gps_data["lat"]
                longitude = gps_data["lng"]

                # Send location data to the user
                bot.send_message(
                    chat_id,
                    f"📍 The patient's current location has been successfully retrieved. Please find the location on the map below."
                )
                bot.send_location(chat_id, latitude,
                                  longitude)  # Send location as a map
                print(f"✅ Sent patient's location: {latitude}, {longitude}")
            else:
                bot.send_message(chat_id,
                                 "❌ Location data is incomplete in Firebase.")
                print("❌ Incomplete location data in Firebase.")
        else:
            bot.send_message(chat_id,
                             "❌ Failed to fetch location from Firebase.")
            print(f"❌ Firebase error: {response.text}")
    except requests.exceptions.RequestException as e:
        bot.send_message(
            chat_id,
            "🚨 Error fetching location from Firebase. Please try again later.")
        print(f"🚨 Error: {e}")


# ✅ Fix: Always update only "latest_healthcare"
def update_firebase(chat_id, first_name):
    data = json.dumps(
        {"latest_healthcare": {
            "chat_id": chat_id,
            "name": first_name
        }})

    firebase_path = f"{FIREBASE_URL}/.json"  # Update root level
    print(f"🔄 Sending Firebase update: {data}")  # Debugging message

    try:
        response = requests.patch(firebase_path, data)
        print(f"🔍 Firebase response: {response.status_code} - {response.text}"
              )  # Log response

        if response.status_code == 200:
            print(
                f"✅ Latest healthcare provider updated: {chat_id} ({first_name})"
            )
            return True
        else:
            print(f"❌ Failed to update Firebase: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"🚨 Error updating Firebase: {e}")
        return False


if __name__ == "__main__":
    from flask import Flask
    import os

    # ✅ Run bot and Flask together
    def run_flask():
        print("🌍 Starting Flask server...")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    from threading import Thread

    # ✅ Start Flask in a separate thread
    Thread(target=run_flask).start()

    print("🤖 Bot is starting polling...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"🚨 Bot encountered an error: {e}")
