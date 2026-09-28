"""Команды, изменяющие VFS в памяти: chmod, chown."""

import re

from shell_emulator.errors import ShellError
from shell_emulator.options import require_operands, resolve, split_options

OCTAL_MODE = re.compile(r"^[0-7]{1,4}$")
SYMBOLIC_CLAUSE = re.compile(r"^([ugoa]*)([+\-=])([rwx]*)$")
NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_-]*$")
WHO_MASKS = {"u": 0o700, "g": 0o070, "o": 0o007, "a": 0o777}
PERM_BITS = {"r": 0o444, "w": 0o222, "x": 0o111}
MODE_MASK = 0o7777
OCTAL_BASE = 8
OWNER_SEP = ":"


def who_mask(who):
    """Маска классов пользователей (u, g, o, a); пусто означает a."""
    mask = 0
    for letter in who or "a":
        mask |= WHO_MASKS[letter]
    return mask


def apply_clause(mode, clause):
    """Применяет одно символьное выражение (u+x, go-w, a=r) к правам."""
    who, operator, perms = clause
    mask = who_mask(who)
    bits = 0
    for letter in perms:
        bits |= PERM_BITS[letter]
    bits &= mask
    if operator == "+":
        return mode | bits
    if operator == "-":
        return mode & ~bits
    return (mode & ~mask) | bits


def parse_mode(spec):
    """Разбирает режим chmod. Возвращает функцию: старые права -> новые."""
    if OCTAL_MODE.match(spec):
        value = int(spec, OCTAL_BASE)
        return lambda mode: value
    clauses = []
    for part in spec.split(","):
        match = SYMBOLIC_CLAUSE.match(part)
        if match is None:
            raise ShellError(f"chmod: invalid mode: '{spec}'")
        clauses.append(match.groups())

    def change(mode):
        """Последовательно применяет все символьные выражения."""
        for clause in clauses:
            mode = apply_clause(mode, clause)
        return mode & MODE_MASK
    return change


def walk(node, recursive):
    """Возвращает узел и, при recursive, всех его потомков."""
    nodes = [node]
    if recursive and node.is_dir:
        for child in node.sorted_children():
            nodes.extend(walk(child, recursive))
    return nodes


def target_nodes(shell, cmd, paths, recursive):
    """Находит все узлы для изменения (с потомками при -R)."""
    nodes = []
    for path in paths:
        nodes.extend(walk(resolve(shell, cmd, path), recursive))
    return nodes


def cmd_chmod(shell, args):
    """chmod [-R] РЕЖИМ файл... — смена прав доступа (в памяти)."""
    flags, operands = split_options("chmod", args, "R")
    require_operands("chmod", operands, 2)
    change = parse_mode(operands[0])
    for node in target_nodes(shell, "chmod", operands[1:], "R" in flags):
        node.mode = change(node.mode)
    return 0


def parse_owner(spec):
    """Разбирает ВЛАДЕЛЕЦ[:ГРУППА]. Возвращает (владелец, группа)."""
    owner, _, group = spec.partition(OWNER_SEP)
    if not owner and not group:
        raise ShellError(f"chown: invalid spec: '{spec}'")
    if owner and not NAME_PATTERN.match(owner):
        raise ShellError(f"chown: invalid user: '{spec}'")
    if group and not NAME_PATTERN.match(group):
        raise ShellError(f"chown: invalid group: '{spec}'")
    return owner or None, group or None


def cmd_chown(shell, args):
    """chown [-R] ВЛАДЕЛЕЦ[:ГРУППА] файл... — смена владельца (в памяти)."""
    flags, operands = split_options("chown", args, "R")
    require_operands("chown", operands, 2)
    owner, group = parse_owner(operands[0])
    for node in target_nodes(shell, "chown", operands[1:], "R" in flags):
        if owner:
            node.owner = owner
        if group:
            node.group = group
    return 0
