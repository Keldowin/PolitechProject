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
#===SQLite connect===#
folder_path = "Memes"  # Путь к папке "Termins"

for filename in os.listdir(folder_path):
    if filename.endswith(".jpg"):
        with open(os.path.join(folder_path, filename), "r") as f:
            sql.execute(f'INSERT INTO Memes (MemesPath) VALUES ("{filename}")')
            db.commit()
            print(f'Обработано {filename}')