import telebot
from dotenv import load_dotenv
import os

load_dotenv('.env')


# create a bot object
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(token='TOKEN')


# handler the /start command
@bot.message_handler(commands=['start'])
def start(message):
    ...


# handler the /help command
@bot.message_handler(commands=['help'])
def help(message):
    ...

if __name__ == '__main__':
    bot.polling()



