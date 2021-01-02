import datetime
import calendar
import pandas as pd
from telegram.ext import (Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove


data = pd.read_csv('data.csv')
data.tanggal = pd.to_datetime(data.tanggal, dayfirst=True)
data.tanggal = data.tanggal.dt.date

# Block 1, function to show calendar, get from github
# telegramcalendar.py from https://github.com/unmonoqueteclea/calendar-telegram
print('Block 1, function to show calendar, get from github')
def create_callback_data(action, year, month, day):
    """ Create the callback data associated to each button"""
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    """ Separate the callback data"""
    return data.split(";")


def create_calendar(year=None, month=None):
    """
    Create an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    """
    now = datetime.datetime.now()
    if year == None: year = now.year
    if month == None: month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    # First row - Month and Year
    row = []
    row.append(InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore))
    keyboard.append(row)
    # Second row - Week Days
    row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        row.append(InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if(day == 0):
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.append(row)
    # Last row - Buttons
    row = []
    row.append(InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day)))
    row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
    row.append(InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day)))
    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def process_calendar_selection(bot, update):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    """
    ret_data = (False, None)
    query = update.callback_query
    (action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        bot.answer_callback_query(callback_query_id=query.id)
    elif action == "DAY":
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id
                              )
        ret_data = True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")
        # UNKNOWN
    return ret_data


# Block 2, The bot
print('Block 2, The bot')
updater = Updater('YOUR BOT TOKEN', use_context=False)
dp = updater.dispatcher
print('Bot running')


def start(bot, update):
    text = 'Hallo silahkan lihat /menu yang tersedia'
    update.message.reply_text(text)
    return ConversationHandler.END


start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)
# ------------------------------------------------- #


def menu(bot, update):
    text = 'Menu yang tersedia.\n\n/caritanggalhoax\tCari hoax berdasarkan tanggal terbit artikel.\n/carijudulhoax\tCari hoax berdasarkan judul artikel.'
    update.message.reply_text(text)
    return ConversationHandler.END


menu_handler = CommandHandler('menu', menu)
dp.add_handler(menu_handler)
# ------------------------------------------------- #


QUERY = range(1)
def carijudulhoax(bot, update):
    update.message.reply_text("Masukkan judul hoax yang dicari.")
    return QUERY


def hasilcarijudulhoax(bot, update):
    query = update.message.text.strip().lower()

    datum = data[data['judul'].str.lower().str.contains(query)].copy()
    if datum.empty:
        text = 'Tidak terdapat hoax dengan judul ' + query
    else:
        text = 'Berikut adalah artikel hoax dengan judul ' + query + '\n\n'
        for row in datum.itertuples():
            text += '[' + str(row.tanggal) + ']' + '\n' + row.judul + '\n' + row.link + '\n\n'

            if len(text) > 3500:
                print(query, len(text))
                update.message.reply_text(text)
                text = ''

    print(query, len(text))
    update.message.reply_text(text)
    return ConversationHandler.END


obrolancarijudulhoax = ConversationHandler(
    entry_points=[CommandHandler('carijudulhoax', carijudulhoax)],
    states={QUERY: [MessageHandler(Filters.text, hasilcarijudulhoax)]},
    fallbacks=[]
)
dp.add_handler(obrolancarijudulhoax)
# ------------------------------------------------- #


def caritanggalhoax(bot, update):
    update.message.reply_text("Please select a date: ",
                              reply_markup=create_calendar())


def hasilcaritanggalhoax(bot, update):
    selected, date = process_calendar_selection(bot, update)
    if selected:
        datum = data[data.tanggal == date.date()]
        if datum.empty:
            text = 'Tidak terdapat artikel hoax yang terbit pada tanggal ' + date.strftime('%d-%m-%Y')
        else:
            text = 'Berikut adalah artikel hoax yang terbit pada tanggal ' + date.strftime('%d-%m-%Y') + '\n\n'
            for row in datum.itertuples():
                text += '[' + str(row.tanggal) + ']' + '\n' + row.judul + '\n' + row.link + '\n\n'
        bot.send_message(chat_id=update.callback_query.from_user.id,
                         text=text,
                         reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


caritanggalhoax_handler = CommandHandler('caritanggalhoax', caritanggalhoax)
dp.add_handler(caritanggalhoax_handler)
hasilcaritanggalhoax_handler = CallbackQueryHandler(hasilcaritanggalhoax)
dp.add_handler(hasilcaritanggalhoax_handler)
# ------------------------------------------------- #


updater.start_polling()
updater.idle()
