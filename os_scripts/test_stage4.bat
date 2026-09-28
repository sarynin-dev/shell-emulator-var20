@echo off
chcp 65001 >NUL
rem Этап 4: основной сценарий.
set ROOT=%~dp0..
call "%ROOT%\run.bat" --vfs "%ROOT%\vfs\deep.json" --script "%ROOT%\scripts\stage4.vsh"
