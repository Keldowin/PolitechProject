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

        TerminOutputMode = randint(1, 3) #Получаем режим вывода вопросв (1 - T.F.F / 2 - F.T.F / 3 - F.F.T)
        BadTermins = sql.execute('SELECT `Termens_full` FROM Termens LIMIT 2;') #Запрос на 2 плохих ответа
        BadTermins = BadTermins.fetchall()

        ShortTermin_full = textwrap.shorten(Termin[0][1], width=50, placeholder="...")
        ShortTermin_bad = textwrap.shorten(BadTermins[0][0], width=50, placeholder="...")
        ShortTermin_bad2 = textwrap.shorten(BadTermins[1][0], width=50, placeholder="...")
        #Строим ответы
        if TerminOutputMode == 1:
            keyboard.add(InlineKeyboardButton(ShortTermin_full,callback_data='TrueAnswer'))
            keyboard.add(InlineKeyboardButton(ShortTermin_bad,callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton(ShortTermin_bad2,callback_data='FalseAnswer'))
        elif TerminOutputMode == 2:
            keyboard.add(InlineKeyboardButton(ShortTermin_bad,callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton(ShortTermin_full,callback_data='TrueAnswer'))
            keyboard.add(InlineKeyboardButton(ShortTermin_bad2,callback_data='FalseAnswer'))
        elif TerminOutputMode == 3:
            keyboard.add(InlineKeyboardButton(ShortTermin_bad,callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton(ShortTermin_bad2,callback_data='FalseAnswer'))
            keyboard.add(InlineKeyboardButton(ShortTermin_full,callback_data='TrueAnswer'))

        keyboard.add(InlineKeyboardButton('⬅ Назад в меню',callback_data='Menu'))
        TerminText = f"Выберите правильное определение на термин:\n<u><b>{Termin[0][0]}</b></u>"
        await callback_query.message.edit_text(text=TerminText,reply_markup=keyboard,parse_mode='HTML')