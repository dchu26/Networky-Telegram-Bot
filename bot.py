import os
import ast
import csv
import pandas as pd
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import gspread
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

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

gclient = gspread.authorize(credentials)

gs = gclient.open_by_key('1AwBtbAt8Ex7HxInxR88SZJCjDyZ2QLxj16vvK3GcYLI')

sheet_one = gs.worksheet('Networky_Intro_Bot')

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
    

def dict_to_pd(data):
    df = pd.DataFrame.from_dict([data])

    df_values = df.values.tolist()
    gs.values_append(sheet_name, {'valueInputOption': 'RAW'}, {
                 'values': df_values})


# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global dictionary
    dictionary = defaultdict(dict)
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
    count = len(dictionary[update.message.chat.id])
    if count == 0:
        dictionary[update.message.chat.id]["first_name"] = text
        msg = "Nice to meet you " + text + "!\
            \nWhat's your last name?"
        await context.bot.send_message(chat_id=get_chat_id(update, context), text=msg)
    elif count == 1:
        dictionary[update.message.chat.id]["last_name"] = text
        await add_suggested_actions(update, context, q1, a1)
    elif count == 3:
        dictionary[update.message.chat.id]["mode_id"] = text
        await add_suggested_actions(update, context, q2, a2)
    elif count == 4:
        msg1 = "Great 🙌\
        \nNext, what is your number 1 personal or professional goal right now?"
        await context.bot.send_message(chat_id=get_chat_id(update, context), text=msg1)
    elif count == 5:
        dictionary[update.message.chat.id]["goal"] = text
        msg2 = "And, do you have any other personal or professional goals right now?\
            \nPlease share a few more with me…"
        await context.bot.send_message(chat_id=get_chat_id(update, context), text=msg2)
    elif count == 6:
        dictionary[update.message.chat.id]['other_goals'] = text
        msg3 = "You are doing great!\
            \nFinal question, what skillsets are you looking to learn more about?"
        await context.bot.send_message(chat_id=get_chat_id(update, context), text=msg3)
    elif count == 7:
        dictionary[update.message.chat.id]['skills'] = text
        msg4 = "Well done! \
            \nHere are the top 3 people I think you should meet"
        await context.bot.send_message(chat_id=get_chat_id(update, context), text=msg4)
        for url in range(len(urls)):
            parameters = {
                "chat_id" : get_chat_id(update, context),
                "photo" : urls[url],
                "caption" : linkedin[url]
            }
            resp = requests.get(base_url, data = parameters)
        dict_to_pd(dictionary[update.message.chat.id])



async def handle_callback(update, context):
    ans = update.callback_query.data
    if ans in a1:
        dictionary[update.callback_query.from_user.id]['mode'] = ans
        await update.callback_query.message.edit_text("Great, what's your " + ans + "?")
    else:
        if ans == a2[-1]:
            msg6 = "How would you describe yourself? 👀"
            await update.callback_query.message.edit_text(msg6)
        else:
            dictionary[update.callback_query.from_user.id]["role"] = ans
            msg7 = "Great 🙌\
            \nNext, what is your number 1 personal or professional goal right now?"
            await update.callback_query.message.edit_text(msg7)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')


    if text is not None:
        if len(dictionary[update.message.chat.id]) == 4:
            dictionary[update.message.chat.id]['role'] = text
            msg8 = "Great 🙌\
            \nNext, what is your number 1 personal or professional goal right now?"
            await context.bot.send_message(chat_id=get_chat_id(update, context), text=msg8)
        else:
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