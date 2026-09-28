"""Тесты этапа 4: команды ls, cd, cat, tree, uniq."""

import io
import os
import unittest

from shell_emulator.shell import Shell
from shell_emulator.vfs import load_vfs

DEEP = os.path.join(os.path.dirname(__file__), "..", "vfs", "deep.json")


class CommandTestCase(unittest.TestCase):
    """Базовый класс: оболочка с VFS deep.json."""

    def setUp(self):
        """Создаёт оболочку с загруженной VFS."""
        self.out = io.StringIO()
        self.shell = Shell(out=self.out)
        self.shell.vfs = load_vfs(DEEP)

    def run_cmd(self, line):
        """Выполняет команду, возвращает (код, вывод)."""
        self.out.seek(0)
        self.out.truncate()
        code = self.shell.execute(line)
        return code, self.out.getvalue()


class LsTest(CommandTestCase):
    """Команда ls."""

    def test_plain_and_all(self):
        """Краткий вывод и флаг -a."""
        _, out = self.run_cmd("ls")
        self.assertEqual(out.split()[0], "docs")
        _, out = self.run_cmd("ls -a")
        self.assertTrue(out.startswith(".  .."))

    def test_long(self):
        """Подробный вывод прав, владельца и размера."""
        _, out = self.run_cmd("ls -l /etc/shadow")
        self.assertTrue(out.startswith("-rw-r----- root     shadow"))

    def test_missing(self):
        """Несуществующий путь — код 2 и сообщение."""
        code, out = self.run_cmd("ls /nope")
        self.assertEqual(code, 2)
        self.assertIn("cannot access '/nope'", out)

    def test_bad_option(self):
        """Неизвестный флаг."""
        code, out = self.run_cmd("ls -z")
        self.assertEqual(code, 1)
        self.assertIn("invalid option -- 'z'", out)


class CdTest(CommandTestCase):
    """Команда cd."""

    def test_navigation(self):
        """Относительные пути, .., ~ и -."""
        self.run_cmd("cd docs/drafts")
        self.assertEqual(self.shell.prompt().split(":")[1], "~/docs/drafts$ ")
        self.run_cmd("cd /var/log")
        _, out = self.run_cmd("cd -")
        self.assertEqual(out.strip(), "/home/user/docs/drafts")
        self.run_cmd("cd")
        self.assertIs(self.shell.vfs.cwd, self.shell.vfs.home)

    def test_errors(self):
        """Ошибки cd."""
        self.assertIn("Not a directory", self.run_cmd("cd notes.txt")[1])
        self.assertIn("No such file", self.run_cmd("cd /nope")[1])
        self.assertIn("too many", self.run_cmd("cd a b")[1])
        self.assertIn("OLDPWD", self.run_cmd("cd -")[1])


class CatTest(CommandTestCase):
    """Команда cat."""

    def test_text_and_numbers(self):
        """Вывод нескольких файлов со сквозной нумерацией."""
        _, out = self.run_cmd("cat -n notes.txt run.sh")
        self.assertIn("     4\t#!/bin/sh", out)

    def test_base64_text(self):
        """Текст, записанный в VFS в base64, выводится как текст."""
        _, out = self.run_cmd("cat hello.txt")
        self.assertEqual(out, "Привет, мир!\n")

    def test_errors(self):
        """Каталог, двоичный файл, нет операнда."""
        self.assertIn("Is a directory", self.run_cmd("cat docs")[1])
        self.assertIn("binary file", self.run_cmd("cat photo.jpg")[1])
        self.assertIn("missing operand", self.run_cmd("cat")[1])


class TreeTest(CommandTestCase):
    """Команда tree."""

    def test_tree(self):
        """Дерево поддиректории и итоговая строка."""
        _, out = self.run_cmd("tree docs")
        self.assertIn("│   └── old", out)
        self.assertTrue(out.endswith("2 directories, 3 files\n"))

    def test_dirs_only(self):
        """Флаг -d выводит только каталоги."""
        _, out = self.run_cmd("tree -d /")
        self.assertNotIn(".txt", out)
        self.assertTrue(out.endswith("11 directories\n"))

    def test_not_dir(self):
        """Путь к файлу — ошибка."""
        code, out = self.run_cmd("tree notes.txt")
        self.assertEqual(code, 1)
        self.assertIn("Not a directory", out)


class UniqTest(CommandTestCase):
    """Команда uniq."""

    def test_modes(self):
        """Режимы без флагов, -c, -d, -u, -i."""
        self.assertEqual(self.run_cmd("uniq notes.txt")[1].count("\n"), 2)
        _, out = self.run_cmd("uniq -c /var/log/syslog")
        self.assertIn("      1 Boot OK", out)
        _, out = self.run_cmd("uniq -ci /var/log/syslog")
        self.assertIn("      2 boot ok", out)
        self.assertEqual(self.run_cmd("uniq -d notes.txt")[1],
                         "сдать практику\n")
        self.assertEqual(self.run_cmd("uniq -u notes.txt")[1],
                         "купить молоко\n")

    def test_errors(self):
        """Ошибки uniq."""
        self.assertIn("missing operand", self.run_cmd("uniq")[1])
        self.assertIn("extra operand", self.run_cmd("uniq a b")[1])
        self.assertIn("No such file", self.run_cmd("uniq nope")[1])


if __name__ == "__main__":
    unittest.main()
