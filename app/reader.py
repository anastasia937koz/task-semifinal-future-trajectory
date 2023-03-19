import csv


def read_csv(path_file):
    """
    Считывание входного .csv файла
    :param path_file: путь к входному файлу
    :return: список данных из файла
    """
    data_list = []
    with open(path_file) as csvfile:
        datareader = csv.reader(csvfile, delimiter=";")
        for row in datareader:
            data_list.append(row)
    return data_list[1:]
