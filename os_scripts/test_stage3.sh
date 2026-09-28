#!/bin/sh
# Этап 3: запуск эмулятора с различными вариантами VFS.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/run.sh"
SCRIPT="$ROOT/scripts/stage3.vsh"

for VFS in minimal few_files deep; do
    echo "=== VFS: $VFS.json ==="
    "$RUN" --vfs "$ROOT/vfs/$VFS.json" --script "$SCRIPT"
    echo "код возврата: $?"
done

echo "=== Ошибка: некорректный base64 ==="
"$RUN" --vfs "$ROOT/vfs/broken.json" < /dev/null
echo "код возврата: $?"

echo "=== Ошибка: некорректный JSON ==="
"$RUN" --vfs "$ROOT/vfs/not_json.json" < /dev/null
echo "код возврата: $?"

echo "=== Ошибка: VFS не найдена ==="
"$RUN" --vfs "$ROOT/vfs/no_such.json" < /dev/null
echo "код возврата: $?"
