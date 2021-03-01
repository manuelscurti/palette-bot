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
from paletter import PaletteService, ScikitClusteringService, MatplotlibImageService
from functools import wraps

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
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

class BotService:
    def __init__(self, token: str, palette_service: PaletteService):
        self.token=token
        self.palette_service=palette_service

    def photo_handler(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)

        user = update.message.from_user
        photo_file = update.message.photo[-1].get_file()

        input_path = "pics/"+str(user.username) + "_" + time.strftime("%Y%m%d%H%M%S")
        output_path = input_path + "_processed.png"

        photo_file.download(input_path)
        logger.info("Photo of %s: %s", user.first_name, input_path)

        palette_service.generate(input_path, output_path)

        file_handler = open(output_path, 'rb')

        context.bot.send_photo(chat_id=update.message.chat_id, photo=file_handler)

        update.message.reply_text('Here you go! 👨🏽‍🎨')

        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(output_path):
            os.remove(output_path)

    def start_handler(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            'Hey! I\'m a super smart palette generator. Try me 👀\n'
            'Send a picture to visualize the most dominant colors. or send /help if you need it\n'
        )

    def help_handler(self, update: Update, context: CallbackContext):
        update.message.reply_text('TODO: write help here')

    def start(self):
        updater = Updater(self.token)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.photo, self.photo_handler))
        dispatcher.add_handler(CommandHandler('start', self.start_handler))
        dispatcher.add_handler(CommandHandler('help', self.help_handler))

        updater.start_polling()

        updater.idle()

if __name__ == '__main__':
    palette_service = PaletteService(ScikitClusteringService(), MatplotlibImageService())

    bot = BotService(os.environ["BOT_TOKEN"], palette_service)
    bot.start()