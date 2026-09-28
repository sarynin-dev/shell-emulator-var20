#!/bin/sh
# Запуск модульных тестов.
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" && PYTHONPATH="$DIR/src" exec python3 -m unittest discover -s tests -v
