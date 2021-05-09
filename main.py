#!/usr/bin/env python3

import logging, subprocess, os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

token = os.getenv('TTYGRAM_TOKEN')
chat_id = os.getenv('TTYGRAM_CHAT_ID')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="🧀")

def sys_info():
    # Get sys date
    ret = subprocess.check_output("/bin/date").decode('ascii')
    # Get sys info
    ret += subprocess.check_output("/usr/bin/landscape-sysinfo").decode('ascii')
    return ret

def exec_command(command):
    try :
        ret = subprocess.check_output(command, stderr = subprocess.STDOUT, shell = True).decode('utf-8')
    except subprocess.CalledProcessError as err: 
        ret = err.output.decode('utf-8')
    return ret

def command_handler(update, context):
    if (update.message.text == "chatid") :
            context.bot.send_message(chat_id = update.effective_chat.id, text = update.effective_chat.id)
    elif (chat_id and update.effective_chat.id == int(chat_id)) :
        if (update.message.text == "sysinfo") :
            context.bot.send_message(chat_id = update.effective_chat.id, text = sys_info())
        else :
            context.bot.send_message(chat_id = update.effective_chat.id, text = exec_command(update.message.text))
    else :
        context.bot.send_message(chat_id = update.effective_chat.id, text = "I don't know you :(")

def main():
    #Authenticate bot
    updater = Updater(token, use_context = True)
    
    #Get dispatcher to update handles
    dp = updater.dispatcher

    #Handle commands
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), command_handler))

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
