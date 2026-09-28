"""Разбор строки ввода на команду и аргументы."""


class ParsedCommand:
    """Результат разбора строки: имя команды и список аргументов."""

    def __init__(self, name, args):
        """Сохраняет имя команды и её аргументы."""
        self.name = name
        self.args = args

    def __repr__(self):
        """Возвращает отладочное представление команды."""
        return f"ParsedCommand({self.name!r}, {self.args!r})"


def parse_line(line):
    """Разделяет строку по пробелам на команду и аргументы.

    Возвращает ParsedCommand или None, если строка пустая.
    """
    parts = line.split()
    if not parts:
        return None
    return ParsedCommand(parts[0], parts[1:])
