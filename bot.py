import os
from collections import defaultdict
from dotenv import load_dotenv, find_dotenv

from typing import Final

from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto
)

# pip install python-telegram-bot
from telegram.ext import (
        CallbackQueryHandler,
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes,
        PollHandler,
        PollAnswerHandler
    )


load_dotenv(find_dotenv())

print('Starting up bot...')

TOKEN: Final = os.environ.get("TOKEN")
BOT_USERNAME: Final = '@networky_intro_bot'

text_count = [0,2,4,5,6,7,8]
poll_count = [1,3,9]

q1 = "What’s the best way for me to send you your matches from Tess network?"
a1 = ['Email', 'Telegram', 'SMS', 'WhatsApp']
q2 = "All set 👏 Now, for me to find the best matches for you, I will ask you a few more questions. \
    \nWhat best describes you?"
a2 = ['Investor', 'Founder', 'Builder', 'Engineer', 'Business Dev & Marketing', 'Advisor', 'Other']
 

dictionary = defaultdict(dict)


# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global count
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
    
'''
def get_answer(update):
  answers = update.poll.options

  ret = ""

  for answer in answers:
    if answer.voter_count == 1:
      # found it
      ret = answer.text
      break
  return ret
  '''


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
        count += 1
        await add_suggested_actions(update, context, q2, a2)
    elif count == 3:
        count += 1
        dictionary[update.message.chat.id]["role"] = text
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

    print(dictionary)

async def handle_callback(update, context):
    ans = update.callback_query.data
    global count
    if ans in a1:
        dictionary[update.callback_query.from_user.id]['mode'] = ans
        print(dictionary)
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

    '''
    # React to group messages only if users mention the bot directly
    if message_type == 'group':
        # Replace with your bot username
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    else:
        response: str = handle_response(text)
    '''

    global count

    if text is not None:
        await handle_response(update, context, text)
        print(count, text)
    
    '''
    elif update.callback_query is not None:
        print('hello')
    '''

'''
async def poll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll.options
    print(answer)


async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    await update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )
'''
    
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