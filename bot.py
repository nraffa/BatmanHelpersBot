import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import requests
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = '5337208924:AAGWULDuW_JBpViTcVSx0wxChN54z-3jvlo'

import os
PORT = int(os.environ.get('PORT', 88))



# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

FLIGHT_REQUEST,FLIGHT_INPUT = range(2)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi! I am Alfred Thaddeus Crane Pennyworth, or simply Alfred. Some know me as as Bruce Wayne's loyal and tireless butler, legal guardian, best friend, aide-de-camp, and surrogate father figure.\n\nTo do some money on the side I am a part-time bot. My initial functionality is to provide you with helpful information about flights.\n\nPlease type /flight to get started.")

def flight(update:Update, context):
    """Ask for the flight number and date"""
    update.message.reply_text(
        'Please, provide a flight number and a date. An example with the correct format would be: IBE6023/2022-04-19')
    return FLIGHT_REQUEST

def get_flight_data(flight_number, flight_date):

	flight_number = str(flight_number)
	flight_date = str(flight_date)

	url = "https://aerodatabox.p.rapidapi.com/flights/number/"+flight_number+"/"+flight_date #IB6856/2022-04-20"
	
	headers = {
	"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com",
	"X-RapidAPI-Key": "1333b9c49dmsh3af848369f388d8p14cff0jsne7c5bfff1524"
	}
	response = requests.request("GET", url, headers=headers)
	
	return response

def get_flight_details(api_response,selected_option):
    #Give in a structured way the flight details
    selected_option = int(selected_option)
    flight_details = f'Below you will be able to see the flight details of the item {selected_option}:\n\n'
    
    flight_details += f'Airline: {api_response[selected_option]["airline"]["name"]}\n'
    flight_details += f'Aircraft: {api_response[selected_option]["aircraft"]["model"]}\n'
    flight_details += f'Flight number: {api_response[selected_option]["number"]}\n'
    flight_details += f'Origin: {api_response[selected_option]["departure"]["airport"]["name"]}\n'
    flight_details += f'Departure: {api_response[selected_option]["departure"]["scheduledTimeLocal"]}\n'
    flight_details += f'Destination: {api_response[selected_option]["arrival"]["airport"]["name"]}\n'
    flight_details += f'Arrival: {api_response[selected_option]["arrival"]["scheduledTimeLocal"]}\n'   
    flight_details += f'Flight status: {api_response[selected_option]["status"]}\n'

    return flight_details

def get_query_info(update,CallbackContext):

    """Stores the flight number and date input by the user"""

    #take the necessary data from the message
    flight_number = update.message.text.split(sep='/')[0]
    flight_date = update.message.text.split(sep='/')[1]
    
    api_response = get_flight_data(flight_number, flight_date)

    i=0
    #get the flight details of all the flights that match the query
    for i in range(len(api_response.json())):
        flight_details = get_flight_details(api_response.json(),i)
        update.message.reply_text(flight_details)
        if i == len(api_response.json()):
            update.message.reply_text('I hope that was helpful!')

    return FLIGHT_INPUT

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def cancel(update:Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("flight", flight))
    dp.add_handler(MessageHandler(Filters.regex('[A-Z]{2}\d{4}\/\d{4}-\d{2}-\d{2}'), get_query_info)) 

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    #updater.start_polling()

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url = 'https://batman-helper-bot.herokuapp.com/' + TOKEN )

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
