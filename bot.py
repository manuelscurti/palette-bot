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
    CallbackContext,
)
import paletter

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Hey! I\'m a super smart palette generator. Try me 👀\n'
        'Send a picture to visualize the most dominant colors. or send /help if you need it\n'
    )


def wait_picture(update: Update, context: CallbackContext) -> int:
     user = update.message.from_user
     photo_file = update.message.photo[-1].get_file()

     timestr = time.strftime("%Y%m%d-%H%M%S")
     filename = str(user.username)+"_"+timestr
     photo_file.download(filename)
     logger.info("Photo of %s: %s", user.first_name, filename)

     #process photo
     output_filename = paletter.generate_palette_from_image(filename, expected_colors=5, width=200, height=200, dpi=1200)
     
     # send result back
     send_palette(update, context, output_filename) 

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