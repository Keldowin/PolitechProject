from func import *
from cfg import TOKEN
from ui_text import *

import logging
import sqlite3
import time
from random import randint
import textwrap
#import datetime
#import locale
#locale.setlocale(locale.LC_TIME, 'ru_RU')

import sys
import pathlib
script_path = pathlib.Path(sys.argv[0]).parent  # абсолютный путь до каталога, где лежит скрипт

#Главные библеотеки

#Установленные библеотеки
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import markdown

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
keyboardM.add(InlineKeyboardButton('Перемена ⛱',callback_data='Memes'))
keyboardM.add(InlineKeyboardButton('Обратная связь 👨‍💻',url="https://docs.google.com/forms/d/e/1FAIpQLSdQiqVmsf2WSlNUBf_PKS0sC2v_VQaHU38-XH0QWEU3Ct8KJA/viewform?usp=sf_link"))

#Help меню
@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,text=UI_TEXT_HelpCommand,parse_mode='HTML')
 
#Меню
@dp.message_handler(commands=['menu','start'])
async def main_menu(message: types.Message, back_to = False):
    userid = message.from_user.id #узнаём юзер айди пользователя
    #Проверка зареган ли пользователь
    if cheak_registration(userid):
        pass
    else:
        user_registration(userid)
        await main_menu(message)

    if back_to:
         await message.edit_text(text=UI_TEXT_MenuCommand,reply_markup=keyboardM,parse_mode='HTML')
    else:
        await message.answer(text=UI_TEXT_MenuCommand,reply_markup=keyboardM,parse_mode='HTML')

#Функция возвращения в меню
@dp.callback_query_handler(lambda c: c.data == 'Menu')
async def ReturnToMenu(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await main_menu(callback_query.message, True)

#Функция вывода мемов (без повторов)
@dp.callback_query_handler(lambda c: c.data == 'Memes')
async def SendMemes(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    #Достаём рандомно мем
    GetMeme = sql.execute('SELECT `MemesPath` FROM `Memes`')
    GetMeme = GetMeme.fetchall()
    RandomId = randint(1, len(GetMeme))
    photo = InputFile("Memes/"+GetMeme[RandomId][0])

    #Генерируем клавиатуру для переключения мемов и возврата в меню
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Следующий мем 😁',callback_data='NextMeme_'+str(RandomId)))

    await bot.send_photo(chat_id=callback_query.message.chat.id,photo=photo,reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('NextMeme_'))
async def process_callback_button_dz(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    LastId = int(callback_query.data.split('_')[1])
    GetMeme = sql.execute('SELECT `MemesPath` FROM `Memes`')
    GetMeme = GetMeme.fetchall()

    RandomId = randint(1, len(GetMeme))
    while RandomId == LastId:
        RandomId = randint(1, len(GetMeme))
    photo = InputFile("Memes/"+GetMeme[RandomId][0])

    #Генерируем клавиатуру для переключения мемов и возврата в меню
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Следующий мем 😁',callback_data='NextMeme_'+str(RandomId)))

    await bot.send_photo(chat_id=callback_query.message.chat.id,photo=photo,reply_markup=keyboard)

@dp.message_handler(commands=['termin'])
async def termincommand(message: types.Message):
    await bot.send_message(message.from_user.id,f"Введите <b>термин</b>, который хотите найти",parse_mode='HTML')
    await TerminSerch.waiting_for_input.set()
    TerminSerch.end = 0 

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
            await bot.send_message(chat_id=message.from_user.id,text="Ничего не найдено, попробуйте найти заново /termin")
            TerminSerch.end = 0
        else:
            keyboard = InlineKeyboardMarkup()
            for i in range(len(SerchFunc)):
                TerminId = str(SerchFunc[i][0])
                TerminShortName = SerchFunc[i][1]
                keyboard.add(InlineKeyboardButton(TerminShortName,callback_data="Termin_"+TerminId))
            TerminSerch.end = 1
            keyboard.add(InlineKeyboardButton('⬅ Назад в меню',callback_data='Menu'))
            await bot.send_message(chat_id=message.chat.id,text="Вот что удалось найти:",reply_markup=keyboard,parse_mode='HTML')
    await state.finish()

#Обработка термина
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('Termin_'))
async def process_callback_button_dz(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    Termin_id = callback_query.data.split('_')[1]
    TerminData = get_termin(Termin_id)
    if TerminData:
        ShortTermin = TerminData[0][0]
        keyborad = InlineKeyboardMarkup()
        keyborad.add(InlineKeyboardButton('⬅ Назад к поиску',callback_data='BackSerch_'+ShortTermin[0]))
        await callback_query.message.edit_text(text=f"▪ <u><b>{TerminData[0][0]}</b></u>\n\n{TerminData[0][1]}",parse_mode='HTML',reply_markup=keyborad)
        TerminSerch.end = 1
    else:
        await callback_query.message.answer(text=f"Определение не найдено, попробуйте найти заново /termin")
        TerminSerch.end = 0
    
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('BackSerch_'))
async def process_callback_button_dz(callback_query: types.CallbackQuery):
    #Получаем первую букву прошлого запроса и по ней составялем зарново новый запрос
    FirstLetter = callback_query.data.split('_')[1]

    SerchInput = FirstLetter
    # Ищем в бд
    SerchFunc = sql.execute(f'SELECT `id`,`Termens_short` FROM `Termens` WHERE lower(`Termens_short`) LIKE "%{SerchInput}%"')
    SerchFunc = SerchFunc.fetchall()
    if not SerchFunc:
        await bot.send_message(text="Ничего не найдено, попробуйте найти заново /termin")
    else:
        keyboard = InlineKeyboardMarkup()
        for i in range(len(SerchFunc)):
            TerminId = str(SerchFunc[i][0])
            TerminShortName = SerchFunc[i][1]
            keyboard.add(InlineKeyboardButton(TerminShortName,callback_data="Termin_"+TerminId))

        keyboard.add(InlineKeyboardButton('⬅ Назад в меню',callback_data='Menu'))
        await callback_query.message.edit_text(text="Вот что удалось найти:",reply_markup=keyboard,parse_mode='HTML')

#Тренировка терминов
@dp.callback_query_handler(lambda c: c.data == 'Learn')
async def TerminSerchMethod(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await generate_test(callback_query)

#Выдаём следующий термин
@dp.callback_query_handler(lambda c: c.data == 'NextTermin')
async def TerminSerchMethod(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await generate_test(callback_query)

#Выдаём определение термина
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('FullTermin_'))
async def CheckFullTermin(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    TerminRand = callback_query.data.split('_')[1] #Получаем айди из TerminRand

    #Выводим и термин и определение
    Termin = get_termin(TerminRand)
    if Termin:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Следующий термин ➡',callback_data='NextTermin'))
        keyboard.add(InlineKeyboardButton('⬅ Назад в меню',callback_data='Menu'))
        TerminText = f"Термин:\n<u><b>{Termin[0][0]}</b></u>\n\nОпределение: {Termin[0][1]}"
        await callback_query.message.edit_text(text=TerminText,reply_markup=keyboard,parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data == 'TrueAnswer')
async def TerminSerchMethod(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Правильный ответ ✔",show_alert=True)
    
    await generate_test(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'FalseAnswer')
async def TerminSerchMethod(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Неправильный ответ ❌",show_alert=True)
    await TerminSerchMethod(callback_query)

if __name__ == '__main__':
    executor.start_polling(dp)