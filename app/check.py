import socket
import subprocess
import re
from datetime import datetime
import platform
from langdetect import detect

from app.exception import NotFoundHostnameException


class Checker:
    """Класс, который проверяет доступ к IP-адресам"""

    def __init__(self, hostname=None, port=None):
        self.hostname = hostname
        self.port = port

    def check(self):
        """
        Основная функция, которая  производит предварительную обработку данных,
        выводит информацию о сайте и проверяет доступ к каждому IP-адресу

        :return:
        """
        self.preprocess_data()
        self.print_info()
        for ip_object in self.ip_address:
            try:
                socket.inet_aton(ip_object)

                if self.port:
                    for port_object in self.port:
                        packet_loss, rtt_max_ms, port_check_state = self.availability(
                            ip_object, port_object
                        )
                        self.show(
                            datetime.now(),
                            self.hostname,
                            ip_object,
                            packet_loss,
                            rtt_max_ms,
                            port_object,
                            port_check_state,
                        )
                else:
                    packet_loss, rtt_max_ms, port_check_state = self.availability(
                        ip_object
                    )
                    self.show(
                        datetime.now(),
                        self.hostname,
                        ip_object,
                        packet_loss,
                        rtt_max_ms,
                        "-1",
                        port_check_state,
                    )
            except socket.gaierror:
                print(f"Данный IP-адрес {ip_object} неверный")
        print("\n")

    def availability(self, ip_address, port=None):
        """
        Производит команду ICMP (ping) взависимости от операционной системы, проверяет доступ к сайту
        :param ip_address: адресс сайта
        :param port: порт сайта
        :return: потерянные пакеты, задержку в мс и удалось открыть сайт или нет
        """
        if platform.system() == "Windows":
            ping_command = ["ping", ip_address]
            ping_output = subprocess.run(
                ping_command,
                encoding="IBM866",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if detect(ping_output.stdout) == "ru":
                packet_loss_pattern = re.compile(r"\d+(\.\d+)?% потерь")
                rtt_pattern = re.compile(r"Среднее = \d+ мсек")
            else:
                packet_loss_pattern = re.compile(r"\d+(\.\d+)?% loss")
                rtt_pattern = re.compile(r"Avarage = \d+ms")
        else:
            ping_command = ["ping", "-c", "4", ip_address]
            ping_output = subprocess.run(
                ping_command,
                encoding="IBM866",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            packet_loss_pattern = re.compile(r"\d+(\.\d+)?% packet loss")
            rtt_pattern = re.compile(
                r"rtt min/avg/max/mdev = \d+\.\d+/(\d+\.\d+)/\d+\.\d+/\d+\.\d+ ms"
            )

        number_pattern = re.compile(r"\d+(\.\d+)?")
        packet_loss_match = packet_loss_pattern.search(ping_output.stdout)
        if packet_loss_match:
            number_match = number_pattern.search(packet_loss_match.group(0))
            packet_loss = float(number_match.group(0)) / 100
        else:
            packet_loss = 1

        rtt_match = rtt_pattern.search(ping_output.stdout)
        if rtt_match:
            number_match = number_pattern.search(rtt_match.group(0))
            rtt_max_ms = float(number_match.group(0))
        else:
            rtt_max_ms = 2000

        if port is not None:
            port_check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port_check_socket.settimeout(1)
            port_check_result = port_check_socket.connect_ex((ip_address, int(port)))
            if port_check_result == 0:
                port_check_state = "Opened"
            else:
                port_check_state = "Unknown"
            port_check_socket.close()
        else:
            port_check_state = "???"
        return packet_loss, rtt_max_ms, port_check_state

    def show(
        self,
        check_date_and_time,
        hostname,
        ip_address,
        packet_loss,
        rtt_max_ms,
        port,
        port_check_state,
    ):
        """
        Вид вывода

        :param check_date_and_time: время вывода
        :param hostname: доменное имя
        :param ip_address: ip адрес сайта
        :param packet_loss: потери пакетов
        :param rtt_max_ms: задержка в мс
        :param port: порт сайта
        :param port_check_state: Opened, если удалось открыть сайт, Unknown в противном случае
        :return:
        """
        result = check_date_and_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        result += " | " + hostname if hostname is not None else " | ???"
        result += " | " + ip_address
        result += " | " + str(float(packet_loss))
        result += " | " + str(rtt_max_ms) + " ms"
        result += " | " + str(port)
        result += " | " + port_check_state
        print(result)

    def is_ip(self, element):
        """
        Возвращает True, если это IP-адрес, в противном случае False
        :param element: доменное имя или ip-адрес
        :return: True или False
        """
        return element.replace(".", "").isdigit()

    def preprocess_data(self):
        """
        Предварительная обработка входных данным, а именно доменного имени, ip-адресов и портов
        :return:
        """
        if self.is_ip(self.hostname):
            self.ip_address = [self.hostname]
            self.hostname = None
        else:
            addr_info = socket.getaddrinfo(self.hostname, None)
            ip_addresses = set()
            for addr in addr_info:
                if self.is_ip(addr[4][0]):
                    ip_addresses.add(addr[4][0])
            self.ip_address = list(ip_addresses)

        if self.port is not None and self.port.replace(",", "").isdigit():
            self.port = self.port.split(",")
        else:
            self.port = []

    def print_info(self):
        """
        Вывод информации о доменном имени
        :return:
        """
        info = [
            self.hostname if self.hostname is not None else "???",
            self.ip_address,
            self.port,
        ]
        print(info)


def check_all(data):
    """
    Проверка всех доменных имен

    :param data: список с данными о доменном имени сайта и порта к нему
    :return:
    """
    for hostname, port in data:
        try:
            if hostname:
                checker = Checker(hostname=hostname, port=port if port else None)
                checker.check()
            else:
                raise NotFoundHostnameException
        except NotFoundHostnameException:
            print("Доменное имя сервера или IP-адрес не найден", end="\n\n\n")
        except socket.gaierror:
            print(f"Не удалось разрешить доменное имя сервера {hostname}", end="\n\n\n")
