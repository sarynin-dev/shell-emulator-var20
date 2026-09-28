"""Точка входа: python -m shell_emulator."""

import sys

from shell_emulator.shell import Shell


def main():
    """Запускает эмулятор в интерактивном режиме."""
    shell = Shell()
    try:
        return shell.repl()
    except KeyboardInterrupt:
        shell.write("")
        return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
