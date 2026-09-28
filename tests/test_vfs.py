"""Тесты этапа 3: загрузка VFS из JSON и работа с путями."""

import os
import unittest

from shell_emulator.vfs import VfsError, load_vfs

VFS_DIR = os.path.join(os.path.dirname(__file__), "..", "vfs")


def vfs_file(name):
    """Возвращает путь к тестовой VFS из каталога vfs/."""
    return os.path.join(VFS_DIR, name)


class LoadTest(unittest.TestCase):
    """Загрузка разных вариантов VFS."""

    def test_minimal(self):
        """Минимальная VFS содержит только корень."""
        vfs = load_vfs(vfs_file("minimal.json"))
        self.assertEqual(vfs.stats(), (1, 0, 0))
        self.assertEqual(vfs.display_path(), "~")

    def test_base64_content(self):
        """Двоичные данные декодируются из base64."""
        vfs = load_vfs(vfs_file("few_files.json"))
        logo = vfs.resolve("/logo.png")
        self.assertTrue(logo.data.startswith(b"\x89PNG"))
        self.assertEqual(logo.mode, 0o600)

    def test_deep_tree(self):
        """VFS с вложенностью не менее 3 уровней и домашним каталогом."""
        vfs = load_vfs(vfs_file("deep.json"))
        _, _, depth = vfs.stats()
        self.assertGreaterEqual(depth, 3)
        self.assertEqual(vfs.display_path(), "~")
        node = vfs.resolve("docs/drafts/old/draft0.txt")
        self.assertFalse(node.is_dir)

    def test_errors(self):
        """Некорректные VFS вызывают VfsError."""
        for name in ("broken.json", "not_json.json", "no_such.json"):
            with self.assertRaises(VfsError):
                load_vfs(vfs_file(name))

    def test_source_file_unchanged(self):
        """Файл VFS на диске не изменяется при загрузке."""
        path = vfs_file("deep.json")
        before = os.path.getmtime(path)
        load_vfs(path)
        self.assertEqual(before, os.path.getmtime(path))


class ResolveTest(unittest.TestCase):
    """Разрешение путей."""

    def setUp(self):
        """Загружает VFS с глубокой структурой."""
        self.vfs = load_vfs(vfs_file("deep.json"))

    def test_relative_and_parent(self):
        """Относительные пути, '.', '..' и '~'."""
        self.assertEqual(self.vfs.resolve("../user/./docs").name, "docs")
        self.assertEqual(self.vfs.resolve("~/docs").name, "docs")
        self.assertIs(self.vfs.resolve("/.."), self.vfs.root)

    def test_missing_and_not_dir(self):
        """Ошибки: нет такого пути, путь через файл."""
        with self.assertRaisesRegex(VfsError, "No such file"):
            self.vfs.resolve("/nope")
        with self.assertRaisesRegex(VfsError, "Not a directory"):
            self.vfs.resolve("notes.txt/x")

    def test_display_path(self):
        """Путь в приглашении: ~ внутри домашнего каталога."""
        self.vfs.cwd = self.vfs.resolve("docs")
        self.assertEqual(self.vfs.display_path(), "~/docs")
        self.vfs.cwd = self.vfs.resolve("/var/log")
        self.assertEqual(self.vfs.display_path(), "/var/log")


if __name__ == "__main__":
    unittest.main()
