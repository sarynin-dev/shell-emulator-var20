"""Команды для работы с VFS: ls, cd, cat, tree, uniq."""

from shell_emulator.errors import ShellError
from shell_emulator.options import (
    read_text, require_operands, resolve, split_options,
)
from shell_emulator.vfs import VfsError, node_path

HIDDEN_PREFIX = "."
DIR_SIZE = 4096
PERM_LETTERS = "rwx"
PERM_SHIFTS = (6, 3, 0)
BITS_PER_CLASS = 3
LS_EXIT_TROUBLE = 2
SINGLE = 1
PREVIOUS_DIR = "-"


def mode_string(node):
    """Возвращает права узла в виде строки drwxr-xr-x."""
    chars = ["d" if node.is_dir else "-"]
    for shift in PERM_SHIFTS:
        for index, letter in enumerate(PERM_LETTERS):
            bit = 1 << (BITS_PER_CLASS - 1 - index + shift)
            chars.append(letter if node.mode & bit else "-")
    return "".join(chars)


def long_line(node, name):
    """Строка подробного вывода ls -l для узла."""
    size = DIR_SIZE if node.is_dir else node.size()
    return (f"{mode_string(node)} {node.owner:<8} {node.group:<8} "
            f"{size:>6} {name}")


def dir_entries(node, show_all):
    """Возвращает пары (имя, узел) содержимого каталога для ls."""
    entries = []
    if show_all:
        entries.append((".", node))
        entries.append(("..", node.parent or node))
    for child in node.sorted_children():
        if show_all or not child.name.startswith(HIDDEN_PREFIX):
            entries.append((child.name, child))
    return entries


def ls_print(shell, entries, long_format):
    """Выводит список записей в кратком или подробном формате."""
    if long_format:
        for name, node in entries:
            shell.write(long_line(node, name))
    elif entries:
        shell.write("  ".join(name for name, _ in entries))


def ls_operand(shell, path, flags, with_header):
    """Выводит один операнд ls: файл или содержимое каталога."""
    node = shell.vfs.resolve(path)
    if not node.is_dir:
        ls_print(shell, [(path, node)], "l" in flags)
        return
    if with_header:
        shell.write(f"{path}:")
    ls_print(shell, dir_entries(node, "a" in flags), "l" in flags)


def cmd_ls(shell, args):
    """ls [-a] [-l] [путь...] — содержимое каталогов VFS."""
    flags, operands = split_options("ls", args, "al")
    paths = operands or ["."]
    code = 0
    for index, path in enumerate(paths):
        if index:
            shell.write("")
        try:
            ls_operand(shell, path, flags, len(paths) > SINGLE)
        except VfsError as exc:
            shell.error(f"ls: cannot access '{path}': {exc}")
            code = LS_EXIT_TROUBLE
    return code


def cmd_cd(shell, args):
    """cd [путь | - | ~] — смена текущего каталога VFS."""
    if len(args) > SINGLE:
        raise ShellError("cd: too many arguments")
    vfs = shell.vfs
    target = args[0] if args else "~"
    if target == PREVIOUS_DIR:
        if shell.previous_dir is None:
            raise ShellError("cd: OLDPWD not set")
        node = shell.previous_dir
        shell.write(node_path(node))
    else:
        node = resolve(shell, "cd", target)
    if not node.is_dir:
        raise ShellError(f"cd: {target}: Not a directory")
    shell.previous_dir = vfs.cwd
    vfs.cwd = node
    return 0


def cmd_cat(shell, args):
    """cat [-n] файл... — вывод содержимого файлов."""
    flags, operands = split_options("cat", args, "n")
    require_operands("cat", operands, 1)
    number = 0
    for path in operands:
        text = read_text("cat", path, resolve(shell, "cat", path))
        for line in text.splitlines():
            number += 1
            prefix = f"{number:>6}\t" if "n" in flags else ""
            shell.write(prefix + line)
    return 0


def tree_walk(shell, node, prefix, dirs_only, counts):
    """Рекурсивно выводит ветви дерева и считает каталоги и файлы."""
    children = [c for c in node.sorted_children()
                if c.is_dir or not dirs_only]
    for index, child in enumerate(children):
        last = index == len(children) - 1
        shell.write(prefix + ("└── " if last else "├── ") + child.name)
        counts[0 if child.is_dir else 1] += 1
        if child.is_dir:
            extension = "    " if last else "│   "
            tree_walk(shell, child, prefix + extension, dirs_only, counts)


def cmd_tree(shell, args):
    """tree [-d] [путь] — вывод дерева каталогов VFS."""
    flags, operands = split_options("tree", args, "d")
    require_operands("tree", operands, 0, 1)
    path = operands[0] if operands else "."
    node = resolve(shell, "tree", path)
    if not node.is_dir:
        raise ShellError(f"tree: {path}: Not a directory")
    shell.write(path)
    counts = [0, 0]
    tree_walk(shell, node, "", "d" in flags, counts)
    summary = f"{counts[0]} directories"
    if "d" not in flags:
        summary += f", {counts[1]} files"
    shell.write("")
    shell.write(summary)
    return 0


def group_adjacent(lines, ignore_case):
    """Группирует соседние одинаковые строки: [(строка, количество)]."""
    groups = []
    for line in lines:
        key = line.lower() if ignore_case else line
        if groups and groups[-1][2] == key:
            groups[-1][1] += 1
        else:
            groups.append([line, 1, key])
    return [(line, count) for line, count, _ in groups]


def uniq_filter(groups, flags):
    """Оставляет группы согласно флагам -d и -u."""
    if "d" in flags:
        groups = [g for g in groups if g[1] > SINGLE]
    if "u" in flags:
        groups = [g for g in groups if g[1] == SINGLE]
    return groups


def cmd_uniq(shell, args):
    """uniq [-c] [-d] [-u] [-i] файл — удаление соседних повторов."""
    flags, operands = split_options("uniq", args, "cdui")
    require_operands("uniq", operands, 1, 1)
    path = operands[0]
    text = read_text("uniq", path, resolve(shell, "uniq", path))
    groups = group_adjacent(text.splitlines(), "i" in flags)
    for line, count in uniq_filter(groups, flags):
        prefix = f"{count:>7} " if "c" in flags else ""
        shell.write(prefix + line)
    return 0
