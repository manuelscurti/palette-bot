import logging
import time
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)
from telegram import ParseMode, ChatAction
from telegram.utils.helpers import mention_html
import sys
import traceback
import paletter
from functools import wraps

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

def error(update, context):
    # add all the dev user_ids in this list. You can also add ids of channels or groups.
    devs = [264217449]
    # we want to notify the user of this problem. This will always work, but not notify users if the update is an 
    # callback or inline query, or a poll update. In case you want this, keep in mind that sending the message 
    # could fail
    if update.effective_message:
        text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. " \
               "My developer(s) will be notified."
        update.effective_message.reply_text(text)
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""
    # normally, we always have an user. If not, its either a channel or a poll update.
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
           f"</code>"
    # and send it to the dev(s)
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Hey! I\'m a super smart palette generator. Try me 👀\n'
        'Send a picture to visualize the most dominant colors. or send /help if you need it\n'
    )


@send_action(ChatAction.TYPING)
def wait_picture(update: Update, context: CallbackContext) -> int:
     user = update.message.from_user
     photo_file = update.message.photo[-1].get_file()

     timestr = time.strftime("%Y%m%d-%H%M%S")
     input_filename = str(user.username)+"_"+timestr
     photo_file.download(input_filename)
     logger.info("Photo of %s: %s", user.first_name, input_filename)

     #process photo
     output_filename = paletter.generate_palette_from_image(input_filename, expected_colors=5, width=300, height=300, dpi=1200)

     # send result back
     send_palette(update, context, output_filename) 

     clear_files(input_filename, output_filename)

def clear_files(input_filename: str, output_filename: str):
     if os.path.exists(input_filename):
          os.remove(input_filename)

     if os.path.exists(output_filename):
          os.remove(output_filename)

def get_help(update: Update, context: CallbackContext) -> int:
     
     update.message.reply_text(
        'TODO: write help here'
     )

def send_palette(update: Update, context: CallbackContext, output_filename: str):
     file_handler = open(output_filename, 'rb')

     #context.bot.send_document(chat_id=update.message.chat_id, thumb=file_handler, document=file_handler)
     context.bot.send_photo(chat_id=update.message.chat_id, photo=file_handler)

     update.message.reply_text(
        'Here you go! 👨🏽‍🎨'
     )

def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )


def main() -> None:
    # Create the Updater and pass it your bot's token.


    updater = Updater("1643470843:AAHto026moyTLXUyXEd0nFcv4-HF_paS-Ic")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.photo, wait_picture))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', get_help))
    dispatcher.add_handler(CommandHandler('cancel', cancel))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()