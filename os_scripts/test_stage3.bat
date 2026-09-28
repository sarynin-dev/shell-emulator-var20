@echo off
rem Этап 3: запуск эмулятора с различными вариантами VFS.
set ROOT=%~dp0..
for %%V in (minimal few_files deep) do (
    echo === VFS: %%V.json ===
    call "%ROOT%\run.bat" --vfs "%ROOT%\vfs\%%V.json" --script "%ROOT%\scripts\stage3.vsh"
)
echo === Ошибка: некорректный base64 ===
call "%ROOT%\run.bat" --vfs "%ROOT%\vfs\broken.json" < NUL
echo === Ошибка: некорректный JSON ===
call "%ROOT%\run.bat" --vfs "%ROOT%\vfs\not_json.json" < NUL
echo === Ошибка: VFS не найдена ===
call "%ROOT%\run.bat" --vfs "%ROOT%\vfs\no_such.json" < NUL
