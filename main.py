#!/usr/bin/env python3

import logging, subprocess, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

token = os.getenv('TTYGRAM_TOKEN')
chat_id = os.getenv('TTYGRAM_CHAT_ID')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def helper(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="""Welcome 👋 . These are available comands:
/command <command> - Execute a command.
/chatid - Get your chat_id.
/sysinfo - Get general system info.

NOTE: To log in, add this convesation id to TTYGRAM_CHAT_ID env
""")

def chatid(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = update.effective_chat.id)

def sysinfo(update, context):
    if (chat_id and update.effective_chat.id == int(chat_id)) :
        # Get sys date
        stdout = subprocess.check_output("/bin/date").decode('ascii')
        # Get sys info
        stdout += subprocess.check_output("/usr/bin/landscape-sysinfo").decode('ascii')
        context.bot.send_message(chat_id = update.effective_chat.id, text = stdout)
    else :
        context.bot.send_message(chat_id = update.effective_chat.id, text = "Sorry, not logged yet :(")

def exec_command(command):
    try :
        ret = subprocess.check_output(command, stderr = subprocess.STDOUT, shell = True).decode('utf-8')
    except subprocess.CalledProcessError as err: 
        ret = err.output.decode('utf-8')
    return ret

def command(update, context):
    if (chat_id and update.effective_chat.id == int(chat_id)) :
        context.bot.send_message(chat_id = update.effective_chat.id, text = exec_command(context.args))
    else :
        context.bot.send_message(chat_id = update.effective_chat.id, text = "Sorry, not logged yet :(")

def read_message(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Try executing /help .")

def main():
    #Authenticate bot
    updater = Updater(token, use_context = True)
    
    #Get dispatcher to update handles
    dp = updater.dispatcher

    #Handle commands
    dp.add_handler(CommandHandler('help', helper))
    dp.add_handler(CommandHandler('chatid', chatid))
    dp.add_handler(CommandHandler('sysinfo', sysinfo))
    dp.add_handler(CommandHandler('command', command))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), read_message))

    #Start the bot
    print('Starting bot..')
    updater.start_polling()
    print('Success!')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
