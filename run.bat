@echo off
rem Запуск эмулятора в Windows. Все аргументы передаются эмулятору.
set PYTHONPATH=%~dp0src
python -m shell_emulator %*
