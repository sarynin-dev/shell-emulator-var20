"""Реестр команд эмулятора и служебные команды."""

from shell_emulator.errors import ShellError
from shell_emulator.fs_commands import (
    cmd_cat, cmd_cd, cmd_ls, cmd_tree, cmd_uniq,
)
from shell_emulator.perm_commands import cmd_chmod, cmd_chown
from shell_emulator.vfs import VfsError, load_vfs

HELP = {
    "ls": ("ls [-a] [-l] [путь...]",
           "содержимое каталога; -a скрытые, -l подробно"),
    "cd": ("cd [путь | ~ | -]",
           "смена каталога; без аргумента — домой, - — назад"),
    "cat": ("cat [-n] файл...",
            "вывод файлов; -n нумерует строки"),
    "tree": ("tree [-d] [путь]",
             "дерево каталогов; -d только каталоги"),
    "uniq": ("uniq [-c] [-d] [-u] [-i] файл",
             "удаление соседних повторов строк"),
    "chmod": ("chmod [-R] РЕЖИМ файл...",
              "смена прав: 755 или u+x,go-w (в памяти)"),
    "chown": ("chown [-R] ВЛАДЕЛЕЦ[:ГРУППА] файл...",
              "смена владельца и группы (в памяти)"),
    "vfs-load": ("vfs-load путь",
                 "загрузка новой VFS из JSON-файла с диска"),
    "vfs-info": ("vfs-info", "сведения о текущей VFS"),
    "help": ("help [команда]", "список команд или справка по команде"),
    "exit": ("exit [N]", "выход из эмулятора с кодом N"),
}
USAGE_WIDTH = 38


def cmd_exit(shell, args):
    """Завершает работу эмулятора с указанным кодом возврата."""
    if len(args) > 1:
        raise ShellError("exit: too many arguments")
    code = 0
    if args:
        if not args[0].lstrip("-").isdigit():
            raise ShellError(f"exit: {args[0]}: numeric argument required")
        code = int(args[0])
    shell.stop(code)
    return code


def cmd_vfs_info(shell, args):
    """Служебная команда: сведения о загруженной VFS."""
    if args:
        raise ShellError("vfs-info: too many arguments")
    dirs, files, depth = shell.vfs.stats()
    shell.write(f"source:      {shell.vfs.source}")
    shell.write(f"directories: {dirs}")
    shell.write(f"files:       {files}")
    shell.write(f"max depth:   {depth}")
    return 0


def cmd_vfs_load(shell, args):
    """vfs-load путь — загрузка новой VFS с диска."""
    if len(args) != 1:
        raise ShellError("vfs-load: usage: vfs-load путь")
    try:
        vfs = load_vfs(args[0])
    except VfsError as exc:
        raise ShellError(f"vfs-load: {exc}") from exc
    shell.vfs = vfs
    shell.previous_dir = None
    shell.write(f"VFS загружена: {args[0]}")
    return 0


def cmd_help(shell, args):
    """help [команда] — список команд с описанием."""
    if len(args) > 1:
        raise ShellError("help: too many arguments")
    names = args or sorted(HELP)
    for name in names:
        if name not in HELP:
            raise ShellError(f"help: no help topics match '{name}'")
        usage, description = HELP[name]
        shell.write(f"{usage:<{USAGE_WIDTH}} {description}")
    return 0


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "cat": cmd_cat,
    "tree": cmd_tree,
    "uniq": cmd_uniq,
    "chmod": cmd_chmod,
    "chown": cmd_chown,
    "vfs-load": cmd_vfs_load,
    "vfs-info": cmd_vfs_info,
    "help": cmd_help,
    "exit": cmd_exit,
}
