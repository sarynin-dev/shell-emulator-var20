"""Реестр команд эмулятора и служебные команды."""

from shell_emulator.errors import ShellError
from shell_emulator.fs_commands import (
    cmd_cat, cmd_cd, cmd_ls, cmd_tree, cmd_uniq,
)


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


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "cat": cmd_cat,
    "tree": cmd_tree,
    "uniq": cmd_uniq,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
