"""Виртуальная файловая система (VFS), загружаемая из JSON в память.

Формат JSON-файла::

    {
      "home": "/home/user",
      "root": {
        "type": "dir", "owner": "root", "group": "root", "mode": "755",
        "children": [
          {"name": "a.txt", "type": "file", "content": "текст"},
          {"name": "b.bin", "type": "file", "content_base64": "AAE="}
        ]
      }
    }

Файл на диске только читается: все изменения выполняются в памяти.
"""

import base64
import json

DIR_TYPE = "dir"
FILE_TYPE = "file"
DEFAULT_DIR_MODE = 0o755
DEFAULT_FILE_MODE = 0o644
DEFAULT_OWNER = "root"
PATH_SEP = "/"
HOME_MARK = "~"


class VfsError(Exception):
    """Ошибка работы с VFS (загрузка или поиск пути)."""


class VfsNode:
    """Узел VFS: каталог или файл."""

    def __init__(self, name, is_dir, parent=None):
        """Создаёт узел с именем name; parent — родительский каталог."""
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.mode = DEFAULT_DIR_MODE if is_dir else DEFAULT_FILE_MODE
        self.owner = DEFAULT_OWNER
        self.group = DEFAULT_OWNER
        self.children = {}
        self.data = b""

    def add_child(self, node):
        """Добавляет узел в каталог, запрещая повторяющиеся имена."""
        if node.name in self.children:
            raise VfsError(f"повторяющееся имя '{node.name}'")
        node.parent = self
        self.children[node.name] = node

    def size(self):
        """Возвращает размер файла в байтах (для каталога — 0)."""
        return len(self.data)

    def sorted_children(self):
        """Возвращает дочерние узлы, отсортированные по имени."""
        return [self.children[key] for key in sorted(self.children)]


def decode_content(spec, name):
    """Возвращает содержимое файла из описания в виде байтов."""
    if "content_base64" in spec:
        try:
            return base64.b64decode(spec["content_base64"], validate=True)
        except (ValueError, TypeError) as exc:
            raise VfsError(f"'{name}': некорректный base64") from exc
    content = spec.get("content", "")
    if not isinstance(content, str):
        raise VfsError(f"'{name}': поле content должно быть строкой")
    return content.encode("utf-8")


def parse_mode(value, name):
    """Преобразует восьмеричную строку прав ('755') в число."""
    try:
        return int(str(value), 8)
    except ValueError as exc:
        raise VfsError(f"'{name}': некорректные права '{value}'") from exc


def check_name(spec):
    """Проверяет и возвращает имя узла из описания."""
    name = spec.get("name")
    if not isinstance(name, str) or not name:
        raise VfsError("узел без имени")
    if PATH_SEP in name or name in (".", ".."):
        raise VfsError(f"недопустимое имя '{name}'")
    return name


def node_from_dict(spec, name):
    """Рекурсивно строит узел VFS по описанию из JSON."""
    if not isinstance(spec, dict):
        raise VfsError("описание узла должно быть объектом")
    kind = spec.get("type")
    if kind not in (DIR_TYPE, FILE_TYPE):
        raise VfsError(f"'{name}': неизвестный тип '{kind}'")
    node = VfsNode(name, kind == DIR_TYPE)
    if "mode" in spec:
        node.mode = parse_mode(spec["mode"], name)
    node.owner = str(spec.get("owner", DEFAULT_OWNER))
    node.group = str(spec.get("group", node.owner))
    if node.is_dir:
        for child in spec.get("children", []):
            node.add_child(node_from_dict(child, check_name(child)))
    else:
        node.data = decode_content(spec, name)
    return node


def path_parts(path):
    """Разбивает путь на компоненты, отбрасывая '~', пустые и '.'."""
    if path.startswith(HOME_MARK):
        path = path[len(HOME_MARK):]
    return [part for part in path.split(PATH_SEP) if part not in ("", ".")]


def node_path(node):
    """Возвращает абсолютный путь узла."""
    names = []
    while node.parent is not None:
        names.append(node.name)
        node = node.parent
    return PATH_SEP + PATH_SEP.join(reversed(names))


class Vfs:
    """Виртуальная файловая система с текущим каталогом."""

    def __init__(self, root=None, source="<пустая VFS>"):
        """Создаёт VFS с корнем root (по умолчанию — пустой каталог)."""
        self.root = root if root is not None else VfsNode("", True)
        self.source = source
        self.home = self.root
        self.cwd = self.root

    def set_home(self, path):
        """Назначает домашний каталог и делает его текущим."""
        try:
            node = self.resolve(path)
        except VfsError as exc:
            raise VfsError(f"домашний каталог {path}: {exc}") from exc
        if not node.is_dir:
            raise VfsError(f"домашний каталог {path} не является каталогом")
        self.home = node
        self.cwd = node

    def start_node(self, path):
        """Возвращает узел, от которого отсчитывается путь."""
        if path.startswith(PATH_SEP):
            return self.root
        if path == HOME_MARK or path.startswith(HOME_MARK + PATH_SEP):
            return self.home
        return self.cwd

    def resolve(self, path):
        """Находит узел по абсолютному или относительному пути."""
        node = self.start_node(path)
        for part in path_parts(path):
            if not node.is_dir:
                raise VfsError("Not a directory")
            if part == "..":
                node = node.parent or node
                continue
            if part not in node.children:
                raise VfsError("No such file or directory")
            node = node.children[part]
        return node

    def display_path(self, node=None):
        """Путь для приглашения: домашний каталог заменяется на '~'."""
        node = node if node is not None else self.cwd
        full = node_path(node)
        home = node_path(self.home)
        if node is self.home:
            return HOME_MARK
        if self.home is self.root:
            return full
        if full.startswith(home + PATH_SEP):
            return HOME_MARK + full[len(home):]
        return full

    def stats(self):
        """Возвращает (число каталогов, число файлов, глубину)."""
        return count_nodes(self.root, 0)


def count_nodes(node, depth):
    """Рекурсивно считает каталоги, файлы и максимальную глубину."""
    if not node.is_dir:
        return 0, 1, depth
    dirs, files, deepest = 1, 0, depth
    for child in node.children.values():
        sub_dirs, sub_files, sub_depth = count_nodes(child, depth + 1)
        dirs += sub_dirs
        files += sub_files
        deepest = max(deepest, sub_depth)
    return dirs, files, deepest


def load_vfs(path):
    """Загружает VFS из JSON-файла на диске (файл не изменяется)."""
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise VfsError(f"{path}: {exc.strerror}") from exc
    except json.JSONDecodeError as exc:
        raise VfsError(f"{path}: некорректный JSON ({exc.msg})") from exc
    try:
        return build_vfs(data, path)
    except VfsError as exc:
        raise VfsError(f"{path}: {exc}") from exc


def build_vfs(data, source):
    """Строит VFS из разобранного JSON-объекта."""
    if not isinstance(data, dict) or "root" not in data:
        raise VfsError("нет корневого объекта 'root'")
    root = node_from_dict(data["root"], PATH_SEP)
    if not root.is_dir:
        raise VfsError("корень VFS должен быть каталогом")
    vfs = Vfs(root, source=source)
    if "home" in data:
        vfs.set_home(str(data["home"]))
    return vfs
