from bot import *
#locale.setlocale(locale.LC_TIME, 'ru_RU')


def cheak_registration(userid : int): #Проверяем зареган ли пользователь или нет
    cheak = sql.execute(f"SELECT `user_id` FROM `Users` WHERE `user_id` = {userid}")
    return bool(cheak.fetchall())

def user_registration(userid : int): #Регестрируем пользователя
    sql.execute(f"INSERT INTO `Users` (User_id) VALUES ({userid})")
    db.commit()

def get_user(userid : int):
    if cheak_registration(userid):
        user = sql.execute(f"SELECT `user_id` FROM `Users` WHERE `user_id` = {userid}")
        return user.fetchall()
    else:
        return False

def get_users():
    users = sql.execute(f"SELECT `user_id` FROM `Users`")
    if users:
        users = users.fetchall()
        return users
    else:
        return False
    
def get_termin(id : int):
    termin = sql.execute(f"SELECT `Termens_short`,`Termens_full` FROM `Termens` WHERE `id` = {id}")
    if termin:
        termin = termin.fetchall()
        return termin
    else:
        return False

async def generate_test(callback_query):
    TerminsCount = sql.execute('SELECT `id` FROM `Termens`')
    TerminsCount = len(TerminsCount.fetchall())
    TerminRand = randint(0, TerminsCount)
    #Получаем рандомный термин
    Termin = get_termin(TerminRand)
    if Termin:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Следующий термин ➡',callback_data='NextTermin'),InlineKeyboardButton('Показать определение 📖',callback_data='FullTermin_'+str(TerminRand)))

        TerminOutputMode = randint(1, 4) #Получаем режим вывода вопросв (1 - T.F.F / 2 - F.T.F / 3 - F.F.T)
        BadTermins = sql.execute('SELECT `Termens_full` FROM Termens ORDER BY RANDOM() LIMIT 2;') #Запрос на 2 плохих ответа
        BadTermins = BadTermins.fetchall()

        ShortTermin_full = Termin[0][1]
        ShortTermin_bad = BadTermins[0][0]
        ShortTermin_bad2 = BadTermins[1][0]
        #Строим ответы
        if TerminOutputMode == 1:
            TerminMode = f"1. {ShortTermin_full}\n\n2. {ShortTermin_bad}\n\n3. {ShortTermin_bad2}"
            keyboard.add(InlineKeyboardButton("Вариант 1.",callback_data='TrueAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 2.",callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 3.",callback_data='FalseAnswer'))
        elif TerminOutputMode == 2:
            TerminMode = f"1. {ShortTermin_bad}\n\n2. {ShortTermin_full}\n\n3. {ShortTermin_bad2}"
            keyboard.add(InlineKeyboardButton("Вариант 1.",callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 2.",callback_data='TrueAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 3.",callback_data='FalseAnswer'))
        elif TerminOutputMode == 3:
            TerminMode = f"1. {ShortTermin_bad}\n\n2. {ShortTermin_bad2}\n\n3. {ShortTermin_full}"
            keyboard.add(InlineKeyboardButton("Вариант 1.",callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 2.",callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 3.",callback_data='TrueAnswer'))
        elif TerminOutputMode == 4:
            TerminMode = f"1. {ShortTermin_bad2}\n\n2. {ShortTermin_bad}\n\n3. {ShortTermin_full}"
            keyboard.add(InlineKeyboardButton("Вариант 1.",callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 2.",callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton("Вариант 3.",callback_data='TrueAnswer'))

        keyboard.add(InlineKeyboardButton('⬅ Назад в меню',callback_data='Menu'))
        TerminText = f"Выберите <u><b>правильный вариант</b></u> определения на термин:\n<b>{Termin[0][0]}</b>\n\n{TerminMode}"
        await callback_query.message.edit_text(text=TerminText,reply_markup=keyboard,parse_mode='HTML')