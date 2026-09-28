"""Общие вспомогательные функции для команд."""

from shell_emulator.errors import ShellError
from shell_emulator.vfs import VfsError

OPTION_PREFIX = "-"


def is_option(arg):
    """Проверяет, что аргумент — набор коротких флагов вида -la."""
    return arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX


def split_options(cmd, args, allowed):
    """Отделяет флаги от операндов.

    Возвращает (множество флагов, список операндов). Флаги можно
    объединять (-la). Неизвестный флаг вызывает ShellError.
    """
    flags = set()
    operands = []
    for arg in args:
        if not is_option(arg):
            operands.append(arg)
            continue
        for letter in arg[1:]:
            if letter not in allowed:
                raise ShellError(f"{cmd}: invalid option -- '{letter}'")
            flags.add(letter)
    return flags, operands


def resolve(shell, cmd, path):
    """Находит узел VFS, превращая ошибку VFS в сообщение команды."""
    try:
        return shell.vfs.resolve(path)
    except VfsError as exc:
        raise ShellError(f"{cmd}: {path}: {exc}") from exc


def require_operands(cmd, operands, minimum, maximum=None):
    """Проверяет число операндов команды."""
    if len(operands) < minimum:
        raise ShellError(f"{cmd}: missing operand")
    if maximum is not None and len(operands) > maximum:
        raise ShellError(f"{cmd}: extra operand '{operands[maximum]}'")


def read_text(cmd, path, node):
    """Возвращает содержимое файла как текст UTF-8."""
    if node.is_dir:
        raise ShellError(f"{cmd}: {path}: Is a directory")
    try:
        return node.data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ShellError(f"{cmd}: {path}: binary file") from exc
