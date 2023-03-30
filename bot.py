from func import *
from cfg import TOKEN
from ui_text import *

import logging
import sqlite3
#import datetime
#import locale
#locale.setlocale(locale.LC_TIME, 'ru_RU')

import sys
import pathlib
script_path = pathlib.Path(sys.argv[0]).parent  # абсолютный путь до каталога, где лежит скрипт

#Главные библеотеки

#Установленные библеотеки
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#Caps = const
logging.basicConfig(level=logging.INFO)
#===SQLite connect===#
try:
    db = sqlite3.connect(script_path / "qldb.db")
    sql = db.cursor()
except sqlite3.Error as error:
    print("Error", error)
#===SQLite connect===#
bot = Bot(TOKEN) #Боту передаём токен
dp = Dispatcher(bot,storage=MemoryStorage()) #Диспетчеру передаём бота

#Help меню
@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,text=UI_TEXT_HelpCommand,parse_mode='HTML')
 
#Меню
@dp.message_handler(commands=['menu','start'])
async def main_menu(message: types.Message):
    userid = message.from_user.id #узнаём юзер айди пользователя
    #Проверка зареган ли пользователь
    if cheak_registration(userid):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Термины 🔖',callback_data="Hello"),InlineKeyboardButton('Тренировка 📖',callback_data="Hello"))
        keyboard.add(InlineKeyboardButton('Обратная связь 👨‍💻',url="https://www.youtube.com/"))
        #MenuKeyborad.add(KeyboardButton('Расписание уроков'))
    else:
        user_registration(userid)
        await main_menu(message)

    await message.answer(text=UI_TEXT_MenuCommand,reply_markup=keyboard,parse_mode='HTML')

if __name__ == '__main__':
    executor.start_polling(dp)