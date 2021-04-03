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
    PicklePersistence
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

class BotService:
    SETTINGS_COLORS, SETTINGS_END = range(2)

    def __init__(self, token: str, palette_service: PaletteService, upload_path: str):
        self.token = token
        self.palette_service = palette_service

        if not os.path.exists(upload_path):
            try:
                os.makedirs(upload_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        self.upload_path = upload_path

    def photo_handler(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)

        user = update.message.from_user
        photo_file = update.message.photo[-1].get_file()

        input_path = self.upload_path + str(user.username) + "_" + time.strftime("%Y%m%d%H%M%S")
        output_path = input_path + "_processed.png"

        photo_file.download(input_path)
        logger.info("Photo of %s: %s", user.first_name, input_path)

        # load user settings for palette generator
        if 'colors' in context.user_data and 'bars' in context.user_data:
            num_colors = context.user_data['colors']
            bars_type = context.user_data['bars']
            palette_service.generate(input_path, output_path, colors=num_colors, weighted_palette=(bars_type == 'Weighted'))
        else:
            palette_service.generate(input_path, output_path) # generate palette with default settings

        file_handler = open(output_path, 'rb')

        context.bot.send_photo(chat_id=update.message.chat_id, photo=file_handler)

        update.message.reply_text('Here you go! 👨🏽‍🎨')

        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(output_path):
            os.remove(output_path)

    def start_command(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            'Hey! I\'m a super smart palette generator. Try me 👀\n'
            'Send a picture to visualize the most dominant colors. or send /help if you need it\n'
        )

        if 'bars' in context.user_data and 'colors' in context.user_data:
            update.message.reply_text('Your current settings for a palette are: %s bars composed by %d colors' % (context.user_data['bars'], context.user_data['colors']))

    def help_command(self, update: Update, context: CallbackContext):
        update.message.reply_text('Just send a picture in this chat to obtain a palette of colors from the picture. No picture will be stored on server.\nType /settings to change your palette preferences or /default to restore preferences to default values')

    def about_command(self, update: Update, context: CallbackContext):
        update.message.reply_text('Author: Manuel Scurti - source code available on https://github.com/manuelscurti')

    def default_command(self, update: Update, context: CallbackContext):
        context.user_data.pop('bars', None)
        context.user_data.pop('colors', None)
        
        update.message.reply_text('Settings restored to original ones!')



    def settings_cancel(self, update: Update, _: CallbackContext) -> int:
        update.message.reply_text(
            'Settings unchanged!', reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    def settings_bars_options(self, update: Update, context: CallbackContext) -> int:
        reply_keyboard = [['Uniform', 'Weighted']]

        update.message.reply_text(
            # 'Change your preferences here. Tap /cancel to leave settings as they are',
            'Do you prefer uniform bars or weighted bars for the palette?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )

        return self.SETTINGS_COLORS # go to colors selection

    def __settings_bars_save(self, update: Update, context: CallbackContext):
        # validity of the input is already checked by conversation handler
        text = update.message.text
        context.user_data['bars'] = text

    def settings_colors_options(self, update: Update, context: CallbackContext) -> int:
        self.__settings_bars_save(update, context) # save previous bars option

        reply_keyboard = [[2,3,4],[5,6,7]]

        update.message.reply_text(
            'How many colors do you want the palette to be made of?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )

        return self.SETTINGS_END # go to save settings

    def __settings_colors_save(self, update: Update, context: CallbackContext):
        text = update.message.text
        if text.isnumeric():
            num_colors = int(text)
            if num_colors >= 2 and num_colors <= 7:
                context.user_data['colors'] = num_colors

    def settings_end(self, update: Update, context: CallbackContext) -> int:
        self.__settings_colors_save(update, context)

        update.message.reply_text(
            'Your new preferences have been saved:\n'
            '%s bars composed by %d colors' % (context.user_data['bars'], context.user_data['colors']),
            reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    def settings_conversation_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[CommandHandler('settings', self.settings_bars_options)], # starts by asking bars preferences
            states={
                self.SETTINGS_COLORS: [MessageHandler(Filters.regex('^(Uniform|Weighted)$'), self.settings_colors_options)],
                self.SETTINGS_END: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)$'), self.settings_end)]
            },
            fallbacks=[CommandHandler('cancel', self.settings_cancel)]
        )

    def start(self):
        updater = Updater(self.token, persistence=PicklePersistence(filename='user_settings.dat'))

        dispatcher = updater.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.photo, self.photo_handler))
        dispatcher.add_handler(CommandHandler('start', self.start_command))
        dispatcher.add_handler(CommandHandler('help', self.help_command))
        dispatcher.add_handler(CommandHandler('about', self.about_command))
        dispatcher.add_handler(CommandHandler('default', self.default_command))
        dispatcher.add_handler(self.settings_conversation_handler())

        updater.start_polling()

        updater.idle()

if __name__ == '__main__':
    palette_service = PaletteService(ScikitClusteringService(), MatplotlibImageService())

    bot = BotService(os.environ["BOT_TOKEN"], palette_service, "uploads/")
    bot.start()