import logging
import os

from telegram import Update, ForceReply
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

from source_query.SourceQuery import SourceQuery

emoji_cry = u'\U0001F622'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    print(update.message)
    if update.message.text.lower() == 'сервер':
        try:
            query = SourceQuery(os.environ['CS_SERVER_IP'], int(os.environ['CS_SERVER_PORT']))

            s = query.get_server(markdown_v2=True)
            print(s)

            query.disconnect()
            update.message.reply_markdown_v2(s, quote=False)
        except Exception as e:
            print(e)
            s = 'Не могу соединиться с сервером ' + emoji_cry
            update.message.reply_text(s, quote=False)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ['TG_TOKEN'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e. message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo, edited_updates=False))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
