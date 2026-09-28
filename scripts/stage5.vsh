# Стартовый скрипт этапа 5: chmod, chown, vfs-load, help
# (запуск с vfs/deep.json). Все изменения VFS выполняются в памяти.
# --- help ---
help
help chmod
# --- chmod: восьмеричный и символьный режимы, -R ---
ls -l run.sh notes.txt
chmod 600 notes.txt
chmod u-x,go=r run.sh
ls -l run.sh notes.txt
chmod a+x notes.txt
chmod g+w,o-r notes.txt
ls -l notes.txt
chmod -R 700 docs
ls -la docs/drafts
# --- chown: владелец, владелец:группа, :группа, -R ---
chown alice notes.txt
chown bob:staff run.sh
chown :users photo.jpg
chown -R guest:guest projects
ls -l
tree projects
ls -l projects/app
# --- vfs-load: загрузка другой VFS с диска ---
vfs-load vfs/few_files.json
vfs-info
ls -l
# Повторная загрузка deep.json: изменения выше не сохранились на диск.
vfs-load vfs/deep.json
ls -l
# --- обработка ошибок: скрипт остановится на первой ошибке. ---
# --- Остальные ошибки проверяет os_scripts/test_stage5.sh.   ---
chmod 999 notes.txt
ls never_executed
