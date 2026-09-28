# Стартовый скрипт этапа 4: ls, cd, cat, tree, uniq (запуск с vfs/deep.json).
# --- ls: все режимы ---
ls
ls -a
ls -l
ls -la docs
ls notes.txt /etc
ls -l /etc/shadow
# --- cd: относительные и абсолютные пути, .., ~, - ---
cd docs/drafts
ls
cd ../..
cd /var/log
cd -
cd
cd ~/projects/app
cd ~
# --- cat: текст, нумерация строк, несколько файлов, base64 ---
cat notes.txt
cat -n notes.txt run.sh
cat /etc/hostname docs/report.txt
cat hello.txt
# --- tree: всё дерево, поддерево, только каталоги ---
tree
tree docs
tree -d /
# --- uniq: все режимы ---
uniq notes.txt
uniq -c /var/log/syslog
uniq -d notes.txt
uniq -u notes.txt
uniq -ci /var/log/syslog
# --- обработка ошибок: скрипт остановится на первой ошибке. ---
# --- Остальные ошибки проверяет os_scripts/test_stage4.sh.   ---
ls /nope
cat photo.jpg
