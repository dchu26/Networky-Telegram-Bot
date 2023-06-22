# Networky-Telegram-Bot
Refer to https://github.com/dchu26/Telegram-Conversation-Demo for details on how to sign in on Telegram API and create your bot using the bot token and username; How to upload to Google Spreadsheet in Google Cloud.

The link for our created bot is https://t.me/networky_intro_bot . You do not need to do any of the steps down below for this bot to work, but if you want to use your own created Telegram API bot and Telegram account to work with bot.py, follow the 2 steps down below! :)

## How to get your own chat_id for bot.py
1. If you don't already, you need to create a Telegram username for your profile. You can do this by going to Telegram -> Settings, and underneath your pic and display name you will see the option to add a username.
2. Once you have a username, type into the Telegram search bar for "Telegram Bot Raw" and click it to go into a conversation with it. Press /start , and the bot will display a brief JSON script of your profile information. Under "chat" and next to "id", should be a number. Under this section in bot.py
```
for url in urls:
        parameters = {
            "chat_id" : {YOUR CHAT ID},
            "photo" : url,
            "caption" : ""
        }
        resp = requests.get(base_url, data = parameters)
        print(resp.text)
```
put your chat ID in "{YOUR CHAT ID}".
5. Save the file and now it's connected to your own personal chat ID!

## How to get your own base_url for bot.py
1. The default base URL for all Telegram API bots goes as so:
   ```
   https://api.telegram.org/bot
   ```
4. After the word "bot" at the end of the link, add your HTTP API Token that @BotFather gave to you when you first created the bot. You may use the one given already in bot.py, but if you want to add yours, this is what you do.
5. The link should now look like this:
   ```
   https://api.telegram.org/bot{YOUR TOKEN}
   ```
6. For this project, we are using the Telegram API function sendPhoto to get our bot to send the user photos. To do this, you must put "/sendPhoto" at the end of your link.
7. Your link should finally look something like this
   ```
   https://api.telegram.org/bot{YOUR TOKEN NUMBER}/sendPhoto
   ```
8. Copy and paste this link next to the base_url variable in quotes and you are done!
9. Should ultimately look like this in bot.py:
   ```
   base_url = "https://api.telegram.org/bot{YOUR TOKEN}/sendPhoto"
   ```
10. Save the file and now your own Telegram API bot link in bot.py!
