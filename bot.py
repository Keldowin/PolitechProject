from func import *
from cfg import TOKEN
from ui_text import *

import logging
import sqlite3
import time
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

keyboardM = InlineKeyboardMarkup()
keyboardM.add(InlineKeyboardButton('Поиск термина 🔍',callback_data="TerminSerch"),InlineKeyboardButton('Тренировка терминов 📖',callback_data="Learn"))
keyboardM.add(InlineKeyboardButton('Обратная связь 👨‍💻',url="https://www.youtube.com/"))

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
        pass
    else:
        user_registration(userid)
        await main_menu(message)

    await message.answer(text=UI_TEXT_MenuCommand,reply_markup=keyboardM,parse_mode='HTML')

class TerminSerch(StatesGroup):
    waiting_for_input = State()
    end = 0

@dp.callback_query_handler(lambda c: c.data == 'TerminSerch')
async def TerminSerchMethod(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,f"Введите <b>термин</b>, который хотите найти",parse_mode='HTML')
    await TerminSerch.waiting_for_input.set()
    TerminSerch.end = 0

# Обрабатываем ответ на второй вопрос
@dp.message_handler(state=TerminSerch.waiting_for_input)
async def OutPutSerch(message: types.Message, state: FSMContext):
    # Получаем ответ пользователя
    SerchInput = message.text
    SerchInput = SerchInput.capitalize()
    if TerminSerch.end != 1:
        # Ищем в бд
        SerchFunc = sql.execute(f'SELECT `id`,`Termens_short` FROM `Termens` WHERE lower(`Termens_short`) LIKE "%{SerchInput}%"')
        SerchFunc = SerchFunc.fetchall()
        if not SerchFunc:
            await bot.send_message(chat_id=message.from_user.id,text="Ничего не найдено, попробуйте найти заново")
            TerminSerch.end = 0
        else:
            keyboard = InlineKeyboardMarkup()
            for i in range(len(SerchFunc)):
                TerminId = str(SerchFunc[i][0])
                TerminShortName = SerchFunc[i][1]
                keyboard.add(InlineKeyboardButton(TerminShortName,callback_data="Termin_"+TerminId))
            TerminSerch.end = 1
            await bot.send_message(chat_id=message.chat.id,text="Вот что удалось найти:",reply_markup=keyboard,parse_mode='HTML')
    await state.finish()

#Обработка термина
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('Termin_'))
async def process_callback_button_dz(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    Termin_id = callback_query.data.split('_')[1]
    TerminData = get_termin(Termin_id)
    if TerminData:
        await callback_query.message.answer(text=f"▪ <u><b>{TerminData[0][0]}</b></u>\n\n{TerminData[0][1]}",parse_mode='HTML')
        TerminSerch.end = 1
    else:
        await callback_query.message.answer(text=f"Определение не найдено, попробуйте найти заново")
        TerminSerch.end = 0
    
    

if __name__ == '__main__':
    executor.start_polling(dp)