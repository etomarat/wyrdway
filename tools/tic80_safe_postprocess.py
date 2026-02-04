"""Постпроцессор “safe build” для TIC-80.

Назначение: после `tq-bundler` привести единый `build.py` к синтаксису, который
стабильно работает при экспорте (win/html) и в старых рантаймах TIC-80.
"""

import ast
import io
import sys
import tokenize


class Tic80WebTransformer(ast.NodeTransformer):
    """Приводит Python-код к подмножеству, которое понимает web TIC-80 1.1.x.

    Цель: сохранить поведение игры, но убрать синтаксис, который ломает старый
    PocketPy/парсер (PEP526/PEP604/typing-стабы).

    Делает:
    - удаляет `if TYPE_CHECKING: ...` целиком
    - удаляет `from typing import ...` и `import typing`
    - удаляет аннотации типов в присваиваниях и def-ах
    - удаляет overload-стабы (`@overload def ...: ...`)
    - удаляет Protocol-классы целиком
    - удаляет докстринги (как Expr-константы)
    """

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "typing":
            return None
        if node.module is not None and node.module.startswith("typing."):
            return None
        return node

    def visit_Import(self, node: ast.Import):
        kept = []
        for alias in node.names:
            if alias.name == "typing":
                continue
            kept.append(alias)
        if not kept:
            return None
        node.names = kept
        return node

    def visit_If(self, node: ast.If):
        if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            return None
        return self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        target = node.target
        value = node.value
        if value is None:
            value = ast.Constant(None)
        assign = ast.Assign(targets=[target], value=value)
        return ast.copy_location(assign, node)

    def visit_Assign(self, node: ast.Assign):
        # В некоторых версиях PocketPy/web-TIC-80 встречались проблемы с многострочными
        # tuple-литералами в class body (особенно для __slots__).
        #
        # Поэтому приводим `__slots__ = (...)` к `__slots__ = [...]`.
        #
        # Также выкидываем type-alias присваивания через typing-объекты:
        #   Foo = Literal[...]
        #   Bar = Callable[...]
        # На web-рантайме `typing` может быть недоступен, а алиасы нам в рантайме не нужны.
        if len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id == "__slots__":
                if isinstance(node.value, ast.Tuple):
                    node.value = ast.List(
                        elts=list(node.value.elts), ctx=ast.Load())
            elif isinstance(t, ast.Name):
                typing_names = {
                    "Literal",
                    "Callable",
                    "Protocol",
                    "TypeAlias",
                    "Final",
                    "overload"
                }
                v = node.value
                if isinstance(v, ast.Name) and v.id in typing_names:
                    return None
                if isinstance(v, ast.Subscript):
                    if isinstance(v.value, ast.Name) and v.value.id in typing_names:
                        return None
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Удаляем overload-стабы: они нужны только для типов, а на web-рантайме
        # могут тянуть typing/Protocol/overload.
        i = 0
        while i < len(node.decorator_list):
            d = node.decorator_list[i]
            if isinstance(d, ast.Name) and d.id == "overload":
                if len(node.body) == 1:
                    b = node.body[0]
                    if isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant) and b.value.value is Ellipsis:
                        return None
                    if isinstance(b, ast.Pass):
                        return None
                node.decorator_list.pop(i)
                continue
            i += 1

        # В некоторых сборках TIC-80 отсутствуют `classmethod`/`staticmethod` как builtins.
        # Для “safe build” важнее загрузиться, чем сохранить поведение этих декораторов.
        node.decorator_list = [
            d for d in node.decorator_list
            if not (isinstance(d, ast.Name) and d.id in ("classmethod", "staticmethod"))
        ]

        node.returns = None
        for arg in node.args.posonlyargs:
            arg.annotation = None
        for arg in node.args.args:
            arg.annotation = None
        for arg in node.args.kwonlyargs:
            arg.annotation = None
        if node.args.vararg is not None:
            node.args.vararg.annotation = None
        if node.args.kwarg is not None:
            node.args.kwarg.annotation = None

        node = self.generic_visit(node)
        node.body = _strip_leading_docstring(node.body)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        node.decorator_list = [
            d for d in node.decorator_list
            if not (isinstance(d, ast.Name) and d.id in ("classmethod", "staticmethod"))
        ]
        node.returns = None
        for arg in node.args.posonlyargs:
            arg.annotation = None
        for arg in node.args.args:
            arg.annotation = None
        for arg in node.args.kwonlyargs:
            arg.annotation = None
        if node.args.vararg is not None:
            node.args.vararg.annotation = None
        if node.args.kwarg is not None:
            node.args.kwarg.annotation = None
        node = self.generic_visit(node)
        node.body = _strip_leading_docstring(node.body)
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        # Удаляем Protocol-классы (они только для типов).
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return None

        # В web-рантайме важнее совместимость парсера, чем типовые “интерфейсы”.
        # Поэтому убираем все не-критичные базовые классы (Protocol/SceneNavigator и т.п.).
        # Если когда-нибудь появится реальная иерархия, сюда можно добавить allowlist.
        allowed_bases = {"Exception", "BaseException"}
        kept_bases = []
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in allowed_bases:
                kept_bases.append(base)
        node.bases = kept_bases

        node = self.generic_visit(node)
        node.body = _strip_leading_docstring(node.body)
        return node

    def visit_Module(self, node: ast.Module):
        node = self.generic_visit(node)
        node.body = _strip_leading_docstring(node.body)
        return node


def _strip_leading_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if not body:
        return body
    first = body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
        if isinstance(first.value.value, str):
            return body[1:]
    return body


def _keep_tic80_header(lines: list[str]) -> tuple[str, str]:
    """Отделяет TIC-80 header-комментарии в начале файла.

    В `.py` картриджах header (title/author/script) часто лежит в комментариях.
    Его лучше сохранить как есть, а остальное можно переписать.
    """
    i = 0
    while i < len(lines):
        s = lines[i]
        if s.strip() == "":
            i += 1
            continue
        if s.lstrip().startswith("#"):
            i += 1
            continue
        break
    return "".join(lines[:i]), "".join(lines[i:])


def _remove_trailing_commas(code: str) -> str:
    """Убирает “висячие” запятые перед закрывающими скобками.

    В PocketPy встречались случаи, когда trailing comma ломает парсер.
    Делает это токен-ориентировано: если `,` перед `)`/`]`/`}` (с игнором NL),
    запятая удаляется.
    """
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    out = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == tokenize.OP and tok.string == ",":
            j = i + 1
            while j < len(tokens):
                t = tokens[j]
                if t.type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
                    j += 1
                    continue
                break
            if j < len(tokens):
                t = tokens[j]
                if t.type == tokenize.OP and t.string in (")", "]", "}"):
                    i += 1
                    continue
        out.append(tok)
        i += 1
    return tokenize.untokenize(out)


def _normalize_exponent_plus(code: str) -> str:
    """Нормализует числовые литералы `1e+30` -> `1e30`.

    В некоторых сборках TIC-80/PocketPy (особенно в экспортированных) парсер не
    принимает `e+` в числе и падает с `SyntaxError: invalid number literal`.
    """
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    out = []
    for tok in tokens:
        if tok.type == tokenize.NUMBER and "e+" in tok.string:
            out.append(tok._replace(string=tok.string.replace("e+", "e")))
        else:
            out.append(tok)
    return tokenize.untokenize(out)


def _postprocess(source: str) -> str:
    header, code = _keep_tic80_header(source.splitlines(keepends=True))
    tree = ast.parse(code)
    tree = Tic80WebTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    out = ast.unparse(tree)
    out = _normalize_exponent_plus(out)
    out = _remove_trailing_commas(out)
    if not out.endswith("\n"):
        out += "\n"
    return header + out


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python tools/tic80_safe_postprocess.py <in.py> <out.py>")
        return 2
    in_path = argv[1]
    out_path = argv[2]

    with open(in_path, "r", encoding="utf-8") as f:
        src = f.read()
    out = _postprocess(src)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
