@echo off
rem Этап 5: основной сценарий (запуск из корня проекта).
cd /d "%~dp0.."
call run.bat --vfs vfs\deep.json --script scripts\stage5.vsh
