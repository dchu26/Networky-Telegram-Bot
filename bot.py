import os
import ast
import csv
import gspread
import pandas as pd
import requests
from collections import defaultdict
from dotenv import load_dotenv, find_dotenv
from oauth2client.service_account import ServiceAccountCredentials

from typing import Final

from telegram import (
    Update,
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
)

# pip install python-telegram-bot
from telegram.ext import (
        CallbackQueryHandler,
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes,
    )


load_dotenv(find_dotenv())

print('Starting up bot...')

TOKEN: Final = os.environ.get("TOKEN")
BOT_USERNAME: Final = '@networky_intro_bot'
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope)
sheet_name = "Networky_Intro_Bot"
gclient = gspread.authorize(credentials)
base_url = "https://api.telegram.org/bot" + TOKEN + "/sendPhoto"
urls = [
            "https://ibb.co/XjmdqWZ",
            "https://ibb.co/9skMKxc",
            "https://ibb.co/VMrykxZ"
]
linkedin = ["https://www.linkedin.com/in/kaushikpsub/",
            "https://www.linkedin.com/in/samuel-stern-phd-029331116/",
            "https://www.linkedin.com/in/mona-tiesler/"]


text_count = [0,2,4,5,6,7,8]
poll_count = [1,3,9]

q1 = "What’s the best way for me to send you your matches from Tess network?"
a1 = ['Email', 'Telegram', 'SMS', 'WhatsApp']
q2 = "All set 👏 Now, for me to find the best matches for you, I will ask you a few more questions. \
    \nWhat best describes you?"
a2 = ['Investor', 'Founder', 'Builder', 'Engineer', 'Business Dev & Marketing', 'Advisor', 'Other']


# Function for moving data from dictionary to CSV file
def dic_to_csv():
    # Write dictionary into csv file
    
    # Initializing each column name
    csv_columns = ['User_ID', 'first_name', 'last_name',
                   'mode', 'mode_id', 'role', 'goal', 'other_goals', 'skills']
    
    # Try to open the csv file and write to it
    try:
        with open("database.csv", "w") as csvfile:
            # Writing the data to the csv file with these parameters
            writer = csv.DictWriter(
                csvfile, fieldnames=csv_columns, lineterminator='\n')
            # Creating the header in the CSV file
            writer.writeheader()
            # Writing everything else
            for key, val in dictionary.items():
                # Creating key-value with the User ID key
                row = {'User_ID': key}
                row.update(val)
                writer.writerow(row)
    # Any possible error that occurs with opening the csv file
    except IOError:
        print("I/O error")


# Basic function to write csv data to the Google sheet
def csv_to_google():
    # Opens the spreadsheet
    spreadsheet = gclient.open(sheet_name)

    # Reading and writing to the Google Sheet
    with open('database.csv', 'r') as file_obj:
        content = file_obj.read()
        gclient.import_csv(spreadsheet.id, data=content)
    
# Function that gets information from Google Sheet and populates our database
def google_to_dict():
    # Opening the spreadsheet on the first sheet
    spreadsheet = gclient.open(sheet_name).sheet1
    # Getting data from spreadsheet
    data = spreadsheet.get_all_records()
    
    # Getting data for each row
    for record in data:
        # Get the first key-value pair
        first_key = next(iter(record))
        # Getting the key-value records and storing as a dict, excluding the first key-value pair
        record_without_first = {key: value for key, value in record.items() if key != first_key}
        # Initializing database using User ID as the key, and record_without_first as the value
        dictionary[record[first_key]] = record_without_first
    
    # Converting the string representation of the lists into lists when applicable
    # ast.literal_eval() is quite strict on conversion so we have to check if it is valid to convert before we actually do it
    for key in dictionary:
        if is_valid_list_string(dictionary[key]['linkedin']):
            dictionary[key]['linkedin'] = ast.literal_eval(dictionary[key]['linkedin'])
        if is_valid_list_string(dictionary[key]['email']):
            dictionary[key]['email'] = ast.literal_eval(dictionary[key]['email'])
        if is_valid_list_string(dictionary[key]['twitter']):
            dictionary[key]['twitter'] = ast.literal_eval(dictionary[key]['twitter'])


# Helper function for checking if a string representation of a list can be converted into a list
def is_valid_list_string(string_representation):
    # Situation where it is possible to do so
    try:
        ast.literal_eval(string_representation)
        return True
    # Situation where the input is invalid for ast.literal_eval()
    except (SyntaxError, ValueError):
        return False
    

# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global count, dictionary
    dictionary = defaultdict(dict)
    count = 0
    await update.message.reply_text('Hello 👋, I’m Networky Intro Bot!')
    await update.message.reply_text('I’m an AI-driven match-making bot that helps you grow your personal network.')
    await update.message.reply_text('I’ll help you connect with 3 people from Tess Hau personal network that I think you’ll love to talk to 😉')
    await update.message.reply_text('Let’s get started…')
    await update.message.reply_text('First, I’d like to get to know you more ☺')
    await update.message.reply_text('Tell me, what’s your first name?')
    # await update.message.reply_text('')


# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')


# Lets us use the /custom command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command, you can add whatever text you want here.')


def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id
    

async def add_suggested_actions(update, context, question, answers):
    options = []

    for item in answers:
        options.append(InlineKeyboardButton(item, callback_data=item))

    reply_markup = InlineKeyboardMarkup([options])

    # update.message.reply_text(response.message, reply_markup=reply_markup)
    await context.bot.send_message(chat_id=get_chat_id(update, context), text=question, reply_markup=reply_markup)


async def handle_response(update, context, text: str) -> str:
    global count

    if count == 0:
        count += 1
        dictionary[update.message.chat.id]["first_name"] = text
        msg = "Nice to meet you " + text + "!\
            \nWhat's your last name?"
        await update.message.reply_text(msg)
    elif count == 1:
        count += 1
        dictionary[update.message.chat.id]["last_name"] = text
        await add_suggested_actions(update, context, q1, a1)
    elif count == 2:
        dictionary[update.message.chat.id]["mode_id"] = text
        count += 1
        await add_suggested_actions(update, context, q2, a2)
    elif count == 3:
        count += 2
        dictionary[update.message.chat.id]["role"] = text
        msg = "Great 🙌\
        \nNext, what is your number 1 personal or professional goal right now?"
        await update.message.reply_text(msg)
    elif count == 4:
        count += 1
        msg = "Great 🙌\
        \nNext, what is your number 1 personal or professional goal right now?"
        await update.message.reply_text(msg)
    elif count == 5:
        count += 1
        dictionary[update.message.chat.id]["goal"] = text
        msg = "And, do you have any other personal or professional goals right now?\
            \nPlease share a few more with me…"
        await update.message.reply_text(msg)
    elif count == 6:
        count += 1
        dictionary[update.message.chat.id]['other_goals'] = text
        msg = "You are doing great!\
            \nFinal question, what skillsets are you looking to learn more about?"
        await update.message.reply_text(msg)
    elif count == 7:
        count += 1
        dictionary[update.message.chat.id]['skills'] = text
        msg = "Well done! \
            \nHere are the top 3 people I think you should meet"
        await update.message.reply_text(msg)
        for url in range(len(urls)):
            parameters = {
                "chat_id" : get_chat_id(update, context),
                "photo" : urls[url],
                "caption" : linkedin[url]
            }
            resp = requests.get(base_url, data = parameters)
    else:
        dic_to_csv()
        csv_to_google()



async def handle_callback(update, context):
    global count
    ans = update.callback_query.data
    if ans in a1:
        dictionary[update.callback_query.from_user.id]['mode'] = ans
        await update.callback_query.message.edit_text("Great, what's your " + ans + "?")
    else:
        if ans == a2[-1]:
            msg = "How would you describe yourself? 👀"
            await update.callback_query.message.edit_text(msg)
        else:
            count += 2
            dictionary[update.callback_query.from_user.id]["role"] = ans
            msg = "Great 🙌\
            \nNext, what is your number 1 personal or professional goal right now?"
            await update.callback_query.message.edit_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')


    if text is not None:
        await handle_response(update, context, text)
    
    
# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    
    #app.add_handler(PollAnswerHandler(poll_handler))
    app.add_handler(CallbackQueryHandler(handle_callback))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=1)