"""Тесты этапа 5: chmod, chown, vfs-load, help."""

import os
import unittest

from test_commands import DEEP, CommandTestCase

FEW = os.path.join(os.path.dirname(DEEP), "few_files.json")


class ChmodTest(CommandTestCase):
    """Команда chmod."""

    def mode_of(self, path):
        """Возвращает права узла по пути."""
        return self.shell.vfs.resolve(path).mode

    def test_octal(self):
        """Восьмеричный режим."""
        self.run_cmd("chmod 640 notes.txt")
        self.assertEqual(self.mode_of("notes.txt"), 0o640)

    def test_symbolic(self):
        """Символьный режим с несколькими выражениями."""
        self.run_cmd("chmod u-x,go=r run.sh")
        self.assertEqual(self.mode_of("run.sh"), 0o644)
        self.run_cmd("chmod +x run.sh")
        self.assertEqual(self.mode_of("run.sh"), 0o755)

    def test_recursive(self):
        """Флаг -R меняет права у всех потомков."""
        self.run_cmd("chmod -R 700 docs")
        self.assertEqual(self.mode_of("docs/drafts/old/draft0.txt"), 0o700)

    def test_errors(self):
        """Неверный режим, нет операнда, нет файла."""
        self.assertIn("invalid mode", self.run_cmd("chmod 999 run.sh")[1])
        self.assertIn("invalid mode", self.run_cmd("chmod u+z run.sh")[1])
        self.assertIn("missing operand", self.run_cmd("chmod 644")[1])
        self.assertIn("No such file", self.run_cmd("chmod 644 nope")[1])


class ChownTest(CommandTestCase):
    """Команда chown."""

    def test_owner_and_group(self):
        """Владелец, владелец:группа, :группа."""
        self.run_cmd("chown alice notes.txt")
        self.run_cmd("chown bob:staff run.sh")
        self.run_cmd("chown :users photo.jpg")
        vfs = self.shell.vfs
        self.assertEqual(vfs.resolve("notes.txt").owner, "alice")
        self.assertEqual(vfs.resolve("run.sh").group, "staff")
        self.assertEqual(vfs.resolve("photo.jpg").owner, "user")
        self.assertEqual(vfs.resolve("photo.jpg").group, "users")

    def test_recursive(self):
        """Флаг -R меняет владельца у всех потомков."""
        self.run_cmd("chown -R guest projects")
        node = self.shell.vfs.resolve("projects/app/main.py")
        self.assertEqual(node.owner, "guest")

    def test_errors(self):
        """Неверные имена и отсутствующие операнды."""
        self.assertIn("invalid user", self.run_cmd("chown A! run.sh")[1])
        self.assertIn("invalid group", self.run_cmd("chown a:B^ x")[1])
        self.assertIn("invalid spec", self.run_cmd("chown : run.sh")[1])
        self.assertIn("missing operand", self.run_cmd("chown user")[1])


class VfsLoadTest(CommandTestCase):
    """Команда vfs-load и неизменность файла на диске."""

    def test_load_and_reset(self):
        """Новая VFS заменяет текущую, изменения не попадают на диск."""
        self.run_cmd("chmod 000 notes.txt")
        code, out = self.run_cmd(f"vfs-load {FEW}")
        self.assertEqual(code, 0)
        self.assertIn("colors.txt", self.run_cmd("ls")[1])
        self.run_cmd(f"vfs-load {DEEP}")
        self.assertEqual(self.shell.vfs.resolve("notes.txt").mode, 0o644)

    def test_errors_keep_old_vfs(self):
        """Ошибка загрузки оставляет прежнюю VFS."""
        code, out = self.run_cmd("vfs-load /no/such.json")
        self.assertEqual(code, 1)
        self.assertIn("No such file", out)
        self.assertIn("notes.txt", self.run_cmd("ls")[1])
        self.assertIn("usage", self.run_cmd("vfs-load")[1])


class HelpTest(CommandTestCase):
    """Команда help."""

    def test_list_all(self):
        """Список содержит все команды."""
        _, out = self.run_cmd("help")
        for name in ("ls", "cd", "cat", "tree", "uniq", "chmod",
                     "chown", "vfs-load", "help", "exit"):
            self.assertIn(name, out)

    def test_single_and_errors(self):
        """Справка по одной команде и ошибки."""
        _, out = self.run_cmd("help uniq")
        self.assertEqual(out.count("\n"), 1)
        self.assertIn("no help topics", self.run_cmd("help nope")[1])
        self.assertIn("too many", self.run_cmd("help a b")[1])


if __name__ == "__main__":
    unittest.main()
