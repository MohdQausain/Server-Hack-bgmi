import telebot
import subprocess
import datetime
import os

from keep_alive import keep_alive
keep_alive()

# Insert your Telegram bot token here
bot = telebot.TeleBot('8147017569:AAGp8qsOlZgEB4-cN-Ex4xyegaAJ12jkqgQ')

# Admin user IDs
admin_id = ["6684327127"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from a given file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Initialize allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                return "Logs cleared successfully ✅"
    except FileNotFoundError:
        return "No logs found to clear."

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

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        return "Expired" if remaining_time.days < 0 else str(remaining_time)
    return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit in ["hour", "hours"]:
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit in ["day", "days"]:
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit in ["week", "weeks"]:
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit in ["month", "months"]:
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
                time_unit = duration_str[-4:].lower()  # Extract the time unit
                if time_unit not in ['hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months']:
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID and the duration (e.g., 1hour, 2days, 3weeks, 4months) to add 😘."
    else:
        response = "You have not purchased yet. Purchase now from:- @venomXcrazy."

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = (f"👤 Your Info:\n\n"
                f"🆔 User ID: <code>{user_id}</code>\n"
                f"📝 Username: {username}\n"
                f"🔖 Role: {user_role}\n"
                f"📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n"
                f"⏳ Remaining Approval Time: {remaining_time}")
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) > 1:
        user_to_remove = command[1]
        if user_to_remove in allowed_user_ids:
            allowed_user_ids.remove(user_to_remove)
            with open(USER_FILE, "w") as file:
                for user in allowed_user_ids:
                    file.write(f"{user}\n")
            response = f"User {user_to_remove} removed successfully 👍."
        else:
            response = f"User {user_to_remove} not found in the list ❌."
    else:
        response = '''Please specify a user ID to remove. 
✅ Usage: /remove <userid>'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    response = clear_logs()
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    try:
        with open(USER_FILE, "r+") as file:
            user_content = file.read()
            if user_content.strip() == "":
                response = "Users are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Users cleared successfully ✅"
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
                for user_id in user_ids:
                    try:
                        user_info = bot.get_chat(int(user_id))
                        username = user_info.username
                        response += f"- @{username} (ID: {user_id})\n"
                    except Exception as e:
                        response += f"- User ID: {user_id}\n"
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
    username = user_info.username if user_info.username else f"UserID: {user_info.id}"

    bot.reply_to(message, f"💥 Attack initiated by {username} on {target} through port {port} for {time} seconds!")
    
    # Start the attack in a separate thread or subprocess if required
    subprocess.Popen(['python3', 'attack_script.py', target, port, str(time)])

@bot.message_handler(commands=['bgmi'])
def start_attack(message):
    user_id = str(message.chat.id)
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "You are not authorized to use this command. Purchase now from:- @venomXcrazy.")
        return
    
    command = message.text.split()
    if len(command) < 4:
        bot.reply_to(message, "Please provide the target IP/URL, port, and time for the attack.\nUsage: /bgmi <target> <port> <time>")
        return

    target = command[1]
    port = command[2]
    time = command[3]
    record_command_logs(user_id, "Attack", target, port, time)
    start_attack_reply(message, target, port, time)

bot.polling(none_stop=True)
