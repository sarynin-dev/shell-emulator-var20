"""Ядро эмулятора: цикл REPL и выполнение команд."""

import sys

from shell_emulator.commands import COMMANDS
from shell_emulator.errors import ShellError
from shell_emulator.parser import parse_line
from shell_emulator.prompt import make_prompt
from shell_emulator.vfs import Vfs

EXIT_ERROR = 1
EXIT_NOT_FOUND = 127
COMMENT_PREFIX = "#"


def is_skippable(line):
    """Проверяет, что строка скрипта пустая или является комментарием."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_PREFIX)


class Shell:
    """Эмулятор командной оболочки."""

    def __init__(self, config=None, out=None):
        """Создаёт оболочку с настройками config и потоком вывода out."""
        self.config = config
        self.out = out if out is not None else sys.stdout
        self.running = True
        self.exit_code = 0
        self.vfs = Vfs()

    def write(self, text):
        """Выводит строку текста пользователю."""
        print(text, file=self.out)

    def error(self, message):
        """Выводит сообщение об ошибке."""
        print(message, file=self.out)

    def stop(self, code):
        """Останавливает цикл REPL."""
        self.running = False
        self.exit_code = code

    def prompt(self):
        """Возвращает текущее приглашение к вводу."""
        return make_prompt(self.vfs.display_path())

    def execute(self, line):
        """Выполняет одну строку. Возвращает код возврата команды."""
        parsed = parse_line(line)
        if parsed is None:
            return 0
        handler = COMMANDS.get(parsed.name)
        if handler is None:
            self.error(f"{parsed.name}: command not found")
            return EXIT_NOT_FOUND
        try:
            return handler(self, parsed.args)
        except ShellError as exc:
            self.error(str(exc))
            return EXIT_ERROR

    def run_script(self, path):
        """Выполняет стартовый скрипт, имитируя диалог с пользователем.

        Каждая команда выводится вместе с приглашением, затем её вывод.
        Выполнение останавливается при первой ошибке.
        Возвращает код возврата последней выполненной команды.
        """
        try:
            with open(path, encoding="utf-8") as script:
                lines = script.read().splitlines()
        except OSError as exc:
            self.error(f"script: {path}: {exc.strerror}")
            self.stop(EXIT_ERROR)
            return EXIT_ERROR
        for number, line in enumerate(lines, start=1):
            if not self.running:
                break
            if is_skippable(line):
                continue
            self.write(self.prompt() + line.strip())
            code = self.execute(line)
            if code != 0 and self.running:
                self.error(f"script: остановлен на строке {number}")
                self.stop(code)
                return code
        return self.exit_code

    def repl(self, stream=None):
        """Интерактивный цикл: чтение, выполнение, вывод."""
        stream = stream if stream is not None else sys.stdin
        while self.running:
            self.out.write(self.prompt())
            self.out.flush()
            line = stream.readline()
            if not line:
                self.write("")
                break
            self.execute(line)
        return self.exit_code
