"""Точка входа: python -m shell_emulator [--vfs PATH] [--script PATH]."""

import sys

from shell_emulator.config import parse_config
from shell_emulator.shell import EXIT_ERROR, Shell
from shell_emulator.vfs import VfsError, load_vfs


def create_shell(config):
    """Создаёт оболочку и загружает VFS. При ошибке возвращает None."""
    shell = Shell(config=config)
    for line in config.describe():
        shell.write(line)
    if config.vfs_path:
        try:
            shell.vfs = load_vfs(config.vfs_path)
        except VfsError as exc:
            shell.error(f"vfs: ошибка загрузки: {exc}")
            return None
    return shell


def main(argv=None):
    """Разбирает параметры, выполняет стартовый скрипт и запускает REPL."""
    shell = create_shell(parse_config(argv))
    if shell is None:
        return EXIT_ERROR
    try:
        if shell.config.script_path:
            shell.run_script(shell.config.script_path)
        if shell.running:
            shell.repl()
    except KeyboardInterrupt:
        shell.write("")
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
