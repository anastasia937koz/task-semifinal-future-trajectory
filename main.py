from app.check import check_all
from app.reader import read_csv

try:
    PATH_FILE = "input/data.csv"
    data = read_csv(PATH_FILE)

    check_all(data)
except ValueError:
    print("Входные данные некорректны")
