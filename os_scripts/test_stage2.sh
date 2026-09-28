#!/bin/sh
# Этап 2: проверка всех параметров командной строки эмулятора.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/run.sh"

echo "=== 1. Без параметров (пустой ввод) ==="
"$RUN" < /dev/null

echo "=== 2. Только --vfs ==="
"$RUN" --vfs "$ROOT/vfs/minimal.json" < /dev/null

echo "=== 3. Только --script (скрипт без ошибок) ==="
"$RUN" --script "$ROOT/scripts/stage2_ok.vsh"

echo "=== 4. --vfs и --script (скрипт с ошибкой) ==="
"$RUN" --vfs "$ROOT/vfs/minimal.json" --script "$ROOT/scripts/stage2.vsh"
echo "код возврата: $?"

echo "=== 5. Несуществующий скрипт ==="
"$RUN" --script "$ROOT/scripts/no_such_file.vsh" < /dev/null
echo "код возврата: $?"

echo "=== 6. Неизвестный параметр ==="
"$RUN" --bad-option
echo "код возврата: $?"
