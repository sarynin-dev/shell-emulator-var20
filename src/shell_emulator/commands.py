"""Команды эмулятора (на этапе 1 — заглушки)."""

from shell_emulator.errors import ShellError


def cmd_stub(shell, name, args):
    """Заглушка: выводит имя команды и её аргументы."""
    shell.write(f"{name} {' '.join(args)}".rstrip())
    return 0


def cmd_ls(shell, args):
    """Заглушка команды ls."""
    return cmd_stub(shell, "ls", args)


def cmd_cd(shell, args):
    """Заглушка команды cd."""
    return cmd_stub(shell, "cd", args)


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


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
