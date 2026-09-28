"""Ядро эмулятора: цикл REPL и выполнение команд."""

import sys

from shell_emulator.commands import COMMANDS
from shell_emulator.errors import ShellError
from shell_emulator.parser import parse_line
from shell_emulator.prompt import make_prompt

EXIT_ERROR = 1
EXIT_NOT_FOUND = 127


class Shell:
    """Эмулятор командной оболочки."""

    def __init__(self, out=None):
        """Создаёт оболочку, пишущую вывод в поток out."""
        self.out = out if out is not None else sys.stdout
        self.running = True
        self.exit_code = 0

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
        return make_prompt()

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
