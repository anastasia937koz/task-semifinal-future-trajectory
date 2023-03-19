import csv


def read_csv(path_file):
    """
    Считываени входного .csv файла
    :param path_file: путь к входному файлу
    :return: списов данных из файла
    """
    data_list = []
    with open(path_file) as csvfile:
        datareader = csv.reader(csvfile, delimiter=";")
        for row in datareader:
            data_list.append(row)
    return data_list[1:]
