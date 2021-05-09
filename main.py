#!/usr/bin/env python3

import logging, subprocess, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

token = os.getenv('TTYGRAM_TOKEN')
chatid_value = os.getenv('TTYGRAM_CHAT_ID')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

CHOOSE, COMMAND, DONE = range(3)

reply_keyboard = [
    ['command'],
    ['chat_id', 'sysinfo'],
    ['done'],
]

command_keyboard = [
    ['done'],
]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_command = ReplyKeyboardMarkup(command_keyboard, one_time_keyboard=True)

def start(update, context):
    update.message.reply_text(
        "Welcome 👋  Choose an action:",
        reply_markup=markup
    )
    return CHOOSE

def done(update, context):
    update.message.reply_text(
        "See you then 👋",
        reply_markup = ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

def chat_id(update, context):
    update.message.reply_text(
        update.effective_chat.id,
        reply_markup = markup
    )
    return CHOOSE

def sysinfo(update, context):
    if (chatid_value and update.effective_chat.id == int(chatid_value)) :
        # Sys date
        stdout = subprocess.check_output("/bin/date").decode('ascii')
        # Sys info
        stdout += subprocess.check_output("/usr/bin/landscape-sysinfo").decode('ascii')
        update.message.reply_text(
            stdout,
            reply_markup = markup
        )
    else :
        update.message.reply_text(
            "Not logged in yet. Get your chat_id, add export it as TTYGRAM_CHAT_ID and restart me 🙂",
            reply_markup = markup
        )
    return CHOOSE

def exec_command(command):
    try :
        ret = subprocess.check_output(command, stderr = subprocess.STDOUT, shell = True).decode('utf-8')
    except subprocess.CalledProcessError as err: 
        ret = err.output.decode('utf-8')
    return ret

def command(update, context):
    update.message.reply_text(
        exec_command(update.message.text),
        reply_markup = markup_command
    )
    return COMMAND

def init_shell(update, context):
    if (chatid_value and update.effective_chat.id == int(chatid_value)) :
        update.message.reply_text(
            "Start typing commands until you are done.",
            reply_markup = markup_command
        )
        return COMMAND
    else :
        update.message.reply_text(
            "Not logged in yet. Get your chat_id, add export it as TTYGRAM_CHAT_ID and restart me 🙂",
            reply_markup = markup
        )
        return CHOOSE

def finish_shell(update, context):
    update.message.reply_text(
        "Select an option",
        reply_markup = markup
    )
    return CHOOSE

def wrong_option(update, context):
    update.message.reply_text(
        "Select a valid option. If you are done, press done. 🙂",
        reply_markup = markup
    )
    return CHOOSE

def default(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Invoke /start to start.")

def main():

    updater = Updater(token, use_context = True)
    dp = updater.dispatcher

    #Handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE: [
                MessageHandler(Filters.regex('^chat_id$'), chat_id),
                MessageHandler(Filters.regex('^sysinfo$'), sysinfo),
                MessageHandler(Filters.regex('^command$'), init_shell),
            ],
            COMMAND: [
                MessageHandler(Filters.regex('^done$'), finish_shell),
                MessageHandler(Filters.text & (~Filters.command), command)
            ],
            DONE: [ MessageHandler(Filters.regex('^done$'), done)]
        },
        fallbacks=[
            MessageHandler(Filters.regex('^done$'), done),
            MessageHandler(Filters.text & Filters.command, wrong_option)
        ],
    )
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), default))
    print('Starting bot..')
    updater.start_polling()
    print('Success!')

    updater.idle()

if __name__ == '__main__':
    main()
