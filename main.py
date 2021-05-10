#!/usr/bin/env python3

import logging, subprocess, os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Auth
token = os.getenv('TTYGRAM_TOKEN')
chatid_value = os.getenv('TTYGRAM_CHAT_ID')

# Main actions
CHOOSE, COMMAND, CHDIR, DONE = range(4)

# Keyboards
reply_keyboard = [
    ['command'],
    ['chat_id', 'sysinfo'],
    ['done'],
]
command_keyboard = [
    ['chdir'],
    ['done'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_command = ReplyKeyboardMarkup(command_keyboard, one_time_keyboard=True)

#--> Additional actions

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

#--> Shell actions

def chdir(update, context):
    try :
        os.chdir(update.message.text)
        ret = 'cwd:' + subprocess.check_output('pwd', shell = True).decode('utf-8')
    except : 
        ret = 'cannot chdir to ' + update.message.text
    update.message.reply_text(
        ret + "\nType commands until you are done.",
        reply_markup = markup_command
    )
    return COMMAND

def chdir_handler(update, context):
    update.message.reply_text(
        'Type the path you want to cd to:'
    )
    return CHDIR

def exec_command(command):
    try :
        ret = subprocess.check_output(command, stderr = subprocess.STDOUT, shell = True, timeout = 2).decode('utf-8')
    except subprocess.CalledProcessError as err: 
        ret = err.output.decode('utf-8')
    except subprocess.TimeoutExpired as err: 
        ret = 'Timeout: this could be due to executing a command which does not exit.'
    if (len(ret) > 4096):
        ret = 'sorry, command output is too long :('
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
            "Type commands until you are done.",
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

#--> General actions

def start(update, context):
    update.message.reply_text(
        "🤖 Welcome 👋  I am TTYbot, an interactive bot terminal. " 
        "Choose an action to start:",
        reply_markup=markup
    )
    return CHOOSE

def done(update, context):
    update.message.reply_text(
        "See you then 👋",
        reply_markup = ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

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
                MessageHandler(Filters.regex('^chdir$'), chdir_handler),
                MessageHandler(Filters.text & (~Filters.command), command)
            ],
            CHDIR: [
                MessageHandler(Filters.text & Filters.command, chdir)
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
