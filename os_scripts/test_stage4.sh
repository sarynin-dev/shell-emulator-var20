#!/bin/sh
# Этап 4: основной сценарий и все варианты ошибок команд.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/run.sh"
VFS="$ROOT/vfs/deep.json"
TMP="${TMPDIR:-/tmp}/stage4_$$.vsh"

echo "=== Основной сценарий ==="
"$RUN" --vfs "$VFS" --script "$ROOT/scripts/stage4.vsh"
echo "код возврата: $?"

# Каждая ошибочная команда запускается отдельным скриптом,
# так как стартовый скрипт останавливается на первой ошибке.
while IFS= read -r CMD; do
    echo "=== Ошибка: $CMD ==="
    printf '%s\n' "$CMD" > "$TMP"
    "$RUN" --vfs "$VFS" --script "$TMP" | tail -n +3
done <<'CMDS'
ls /nope
ls -z
cd notes.txt
cd /nope
cd a b
cat
cat docs
cat photo.jpg
cat nope.txt
tree notes.txt
tree a b
uniq
uniq a b
uniq nope.txt
uniq -x notes.txt
CMDS
rm -f "$TMP"
