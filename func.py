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