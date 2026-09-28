#!/bin/sh
# Этап 5: основной сценарий и все варианты ошибок команд.
# Запускать из корня проекта: пути к VFS в скрипте относительные.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
VFS="vfs/deep.json"
TMP="${TMPDIR:-/tmp}/stage5_$$.vsh"
BEFORE="$(cksum "$VFS")"

echo "=== Основной сценарий ==="
./run.sh --vfs "$VFS" --script scripts/stage5.vsh
echo "код возврата: $?"

while IFS= read -r CMD; do
    echo "=== Ошибка: $CMD ==="
    printf '%s\n' "$CMD" > "$TMP"
    ./run.sh --vfs "$VFS" --script "$TMP" | tail -n +3
done <<'CMDS'
chmod 999 notes.txt
chmod u+z notes.txt
chmod 644
chmod 644 nope.txt
chown Alice! notes.txt
chown user:Bad^ notes.txt
chown : notes.txt
chown user
chown user nope.txt
vfs-load
vfs-load vfs/no_such.json
vfs-load vfs/broken.json
vfs-load vfs/not_json.json
help nope
help a b
CMDS
rm -f "$TMP"

echo "=== Проверка: файл VFS на диске не изменился ==="
if [ "$BEFORE" = "$(cksum "$VFS")" ]; then
    echo "OK: $VFS не изменён"
else
    echo "ОШИБКА: $VFS изменён"
fi
