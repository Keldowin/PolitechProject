import os
import sqlite3
import sys
import pathlib
script_path = pathlib.Path(sys.argv[0]).parent  # абсолютный путь до каталога, где лежит скрипт
#===SQLite connect===#
try:
    db = sqlite3.connect(script_path / "qldb.db")
    sql = db.cursor()
except sqlite3.Error as error:
    print("Error", error)

SerchTermin = "Кре".capitalize()
SerchFunc = sql.execute(f'SELECT `Termens_short`,`Termens_full` FROM `Termens` WHERE lower(`Termens_short`) LIKE "%{SerchTermin}%"')
SerchFunc = SerchFunc.fetchall()
if not SerchFunc:
    print('Ничего не найдено')
else:
    for i in range(len(SerchFunc)):
        print(SerchFunc[i][0])
        print(SerchFunc[i][1])