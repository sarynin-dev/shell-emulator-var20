#!/bin/sh
# Запуск эмулятора. Все аргументы передаются эмулятору.
# Пример: ./run.sh --vfs vfs/deep.json --script scripts/stage4.vsh
DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$DIR/src" exec python3 -m shell_emulator "$@"
