import telebot
import psycopg2
from datetime import datetime
from telebot import types

token = '5870159389:AAFfcNf5_U6cnKVYyKsgM5VQ9H-SI0AXzOw'
bot = telebot.TeleBot(token)

date_format = "%m/%d/%Y"
monday_of_first_week = datetime.strptime('1/30/2023', date_format)

delta = (datetime.strptime(datetime.now().strftime(date_format), date_format) - monday_of_first_week)//7
week_number = int(delta.days) + 1

if week_number % 2 == 0:
    week = "Четная"
else:
    week = "Нечетная"

days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]

conn = psycopg2.connect(database="schedule_db_backup",
                        user="Nick",
                        password="",
                        host="localhost",
                        port="5432")
cursor = conn.cursor()

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Текущая неделя", "Следующая неделя")
    bot.send_message(message.chat.id, 'Здравствуйте! Хотите узнать рассписание БВТ2202?\n /help - список команд', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Я умею показывать рассписание БВТ2202\n/week - узнать четность недели\n/mtuci - перейти на официальный сайт МТУСИ')


@bot.message_handler(commands=['week'])
def answer(message):
    if week == 'Нечетная':
        bot.send_message(message.chat.id, 'Сейчас нечетная неделя')
    else:
        bot.send_message(message.chat.id, 'Сейчас четная неделя')


@bot.message_handler(commands=['mtuci'])
def answer(message):
    bot.send_message(message.chat.id, 'Свежая информация о МТУСИ - https://mtuci.ru/')


@bot.message_handler(content_types=['text'])
def answer(message):
    current_day = message.text
    if current_day in days:
        try:
            cursor.execute("SELECT * FROM timetable WHERE day=%s AND week=%s", (current_day, week))
            records = list(cursor.fetchall())
            final_message = current_day + ':\n'
            for daytable in records:
                cursor.execute("SELECT * FROM teacher WHERE subject=%s", (daytable[2],))
                teacher = list(cursor.fetchall())
                final_message += daytable[2] + '\t|\t' + daytable[3] + '\t|\t' + daytable[4] + '\t|\t' + teacher[0][1] + '\n'
            bot.send_message(message.chat.id, final_message)
        except:
            bot.send_message(message.chat.id, 'В этот день у вас нет пар!')
    elif current_day == "Текущая неделя":
        final_message = ''
        for each_day in days:
            final_message += each_day + ':\n'
            try:
                cursor.execute("SELECT * FROM timetable WHERE day=%s AND week=%s", (each_day, week))
                records = list(cursor.fetchall())
                for daytable in records:
                    cursor.execute("SELECT * FROM teacher WHERE subject=%s", (daytable[2],))
                    teacher = list(cursor.fetchall())
                    final_message += daytable[2] + '\t|\t' + daytable[3] + '\t|\t' + daytable[4] + '\t|\t' + teacher[0][
                        1] + '\n'
            except:
                final_message += 'В этот день у вас нет пар!' + '\n'
        bot.send_message(message.chat.id, final_message)
    elif current_day == "Следующая неделя":
        final_message = ''
        if week == 'Четная':
            next_week = 'Нечетная'
        else:
            next_week = 'Четная'
        for each_day in days:
            final_message += each_day + ':\n'
            try:
                cursor.execute("SELECT * FROM timetable WHERE day=%s AND week=%s", (each_day, next_week))
                records = list(cursor.fetchall())
                for daytable in records:
                    cursor.execute("SELECT * FROM teacher WHERE subject=%s", (daytable[2],))
                    teacher = list(cursor.fetchall())
                    final_message += daytable[2] + '\t|\t' + daytable[3] + '\t|\t' + daytable[4] + '\t|\t' + teacher[0][
                        1] + '\n'
            except:
                final_message += 'В этот день у вас нет пар!' + '\n'
        bot.send_message(message.chat.id, final_message)
    else:
        bot.send_message(message.chat.id, 'Прошу прощения, я вас не понял')


bot.infinity_polling()
