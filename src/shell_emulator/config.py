"""Параметры командной строки эмулятора."""

import argparse


class Config:
    """Настройки эмулятора, заданные пользователем."""

    def __init__(self, vfs_path=None, script_path=None):
        """Сохраняет путь к VFS и путь к стартовому скрипту."""
        self.vfs_path = vfs_path
        self.script_path = script_path

    def describe(self):
        """Возвращает строки отладочного вывода всех параметров."""
        return [
            f"[config] vfs_path    = {self.vfs_path or '<не задан>'}",
            f"[config] script_path = {self.script_path or '<не задан>'}",
        ]


def build_arg_parser():
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS (JSON-файл)",
    )
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту с командами эмулятора",
    )
    return parser


def parse_config(argv=None):
    """Разбирает аргументы командной строки и возвращает Config."""
    ns = build_arg_parser().parse_args(argv)
    return Config(vfs_path=ns.vfs_path, script_path=ns.script_path)
