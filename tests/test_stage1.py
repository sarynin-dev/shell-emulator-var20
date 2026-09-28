"""Тесты этапа 1: парсер, приглашение, заглушки, exit."""

import io
import unittest

from shell_emulator.parser import parse_line
from shell_emulator.prompt import make_prompt
from shell_emulator.shell import Shell


def run(lines):
    """Выполняет строки в новой оболочке и возвращает (shell, вывод)."""
    out = io.StringIO()
    shell = Shell(out=out)
    for line in lines:
        shell.execute(line)
    return shell, out.getvalue()


class ParserTest(unittest.TestCase):
    """Проверка разбора строки."""

    def test_split_by_spaces(self):
        """Команда и аргументы разделяются пробелами."""
        cmd = parse_line("ls  -l   /home ")
        self.assertEqual(cmd.name, "ls")
        self.assertEqual(cmd.args, ["-l", "/home"])

    def test_empty_line(self):
        """Пустая строка даёт None."""
        self.assertIsNone(parse_line("   "))


class PromptTest(unittest.TestCase):
    """Проверка приглашения."""

    def test_format(self):
        """Приглашение имеет вид user@host:~$."""
        prompt = make_prompt()
        self.assertIn("@", prompt)
        self.assertTrue(prompt.endswith(":~$ "))


class StubCommandsTest(unittest.TestCase):
    """Проверка заглушек и обработки ошибок."""

    def test_unknown_command(self):
        """Неизвестная команда даёт сообщение об ошибке."""
        _, out = run(["foo bar"])
        self.assertIn("foo: command not found", out)

    def test_exit_stops_shell(self):
        """exit останавливает цикл и задаёт код возврата."""
        shell, _ = run(["exit 3"])
        self.assertFalse(shell.running)
        self.assertEqual(shell.exit_code, 3)

    def test_exit_bad_argument(self):
        """exit с нечисловым аргументом — ошибка."""
        shell, out = run(["exit abc"])
        self.assertIn("numeric argument required", out)
        self.assertTrue(shell.running)

    def test_repl_reads_until_exit(self):
        """REPL выполняет команды до exit."""
        out = io.StringIO()
        shell = Shell(out=out)
        code = shell.repl(io.StringIO("unknown\nexit 2\nls\n"))
        self.assertEqual(code, 2)
        self.assertIn("unknown: command not found", out.getvalue())


if __name__ == "__main__":
    unittest.main()
