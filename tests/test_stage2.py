"""Тесты этапа 2: параметры командной строки и стартовый скрипт."""

import io
import os
import tempfile
import unittest

from shell_emulator.config import parse_config
from shell_emulator.shell import Shell


def write_script(text):
    """Создаёт временный файл скрипта и возвращает путь к нему."""
    fd, path = tempfile.mkstemp(suffix=".vsh")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


class ConfigTest(unittest.TestCase):
    """Разбор параметров командной строки."""

    def test_all_options(self):
        """Оба параметра попадают в конфигурацию."""
        config = parse_config(["--vfs", "a.json", "--script", "s.vsh"])
        self.assertEqual(config.vfs_path, "a.json")
        self.assertEqual(config.script_path, "s.vsh")

    def test_defaults(self):
        """Без параметров значения не заданы."""
        config = parse_config([])
        self.assertIsNone(config.vfs_path)
        self.assertIn("<не задан>", config.describe()[0])


class ScriptTest(unittest.TestCase):
    """Выполнение стартового скрипта."""

    def run_script(self, text):
        """Выполняет текст как скрипт, возвращает (shell, вывод)."""
        path = write_script(text)
        self.addCleanup(os.remove, path)
        out = io.StringIO()
        shell = Shell(out=out)
        shell.run_script(path)
        return shell, out.getvalue()

    def test_echo_input_and_output(self):
        """Скрипт показывает и ввод (с приглашением), и вывод."""
        _, out = self.run_script("# комментарий\ncd /tmp\n")
        self.assertIn("$ cd /tmp\n", out)
        self.assertNotIn("комментарий", out)

    def test_stop_on_first_error(self):
        """Скрипт останавливается на первой ошибке."""
        shell, out = self.run_script("bad\ncd never\n")
        self.assertIn("bad: command not found", out)
        self.assertIn("строке 1", out)
        self.assertNotIn("cd never", out)
        self.assertFalse(shell.running)

    def test_missing_script(self):
        """Отсутствующий скрипт — ошибка и остановка."""
        out = io.StringIO()
        shell = Shell(out=out)
        shell.run_script("/no/such/script.vsh")
        self.assertIn("script: /no/such/script.vsh", out.getvalue())
        self.assertFalse(shell.running)


if __name__ == "__main__":
    unittest.main()
