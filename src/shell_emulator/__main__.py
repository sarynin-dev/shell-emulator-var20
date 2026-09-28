"""Точка входа: python -m shell_emulator [--vfs PATH] [--script PATH]."""

import sys

from shell_emulator.config import parse_config
from shell_emulator.shell import Shell


def main(argv=None):
    """Разбирает параметры, выполняет стартовый скрипт и запускает REPL."""
    config = parse_config(argv)
    shell = Shell(config=config)
    for line in config.describe():
        shell.write(line)
    try:
        if config.script_path:
            shell.run_script(config.script_path)
        if shell.running:
            shell.repl()
    except KeyboardInterrupt:
        shell.write("")
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())
