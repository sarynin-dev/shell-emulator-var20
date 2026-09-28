"""Формирование приглашения к вводу на основе данных реальной ОС."""

import getpass
import socket


def get_username():
    """Возвращает имя текущего пользователя ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return "user"


def get_hostname():
    """Возвращает короткое имя хоста ОС."""
    return socket.gethostname().split(".")[0]


def make_prompt(cwd_display="~"):
    """Строит приглашение вида username@hostname:~$."""
    return f"{get_username()}@{get_hostname()}:{cwd_display}$ "
