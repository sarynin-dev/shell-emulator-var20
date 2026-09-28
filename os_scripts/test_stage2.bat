@echo off
chcp 65001 >NUL
rem Этап 2: проверка всех параметров командной строки эмулятора.
set ROOT=%~dp0..
echo === 1. Без параметров ===
call "%ROOT%\run.bat" < NUL
echo === 2. Только --vfs ===
call "%ROOT%\run.bat" --vfs "%ROOT%\vfs\minimal.json" < NUL
echo === 3. Только --script ===
call "%ROOT%\run.bat" --script "%ROOT%\scripts\stage2_ok.vsh"
echo === 4. --vfs и --script (скрипт с ошибкой) ===
call "%ROOT%\run.bat" --vfs "%ROOT%\vfs\minimal.json" --script "%ROOT%\scripts\stage2.vsh"
echo === 5. Несуществующий скрипт ===
call "%ROOT%\run.bat" --script "%ROOT%\scripts\no_such_file.vsh" < NUL
