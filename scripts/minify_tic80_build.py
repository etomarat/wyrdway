import argparse
import ast
import inspect
import re
from pathlib import Path


META_KEYS = [
    "# title:",
    "# author:",
    "# desc:",
    "# site:",
    "# license:",
    "# version:",
    "# script:"
]

TYPING_NAMES = {
    "Literal",
    "TypeAlias",
    "Callable",
    "Protocol",
    "overload"
}


def extract_metadata_header(lines: list[str]) -> list[str]:
    header: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped == "":
            i += 1
            continue
        if not line.lstrip().startswith("#"):
            break
        low = line.lstrip().lower()
        keep = False
        for key in META_KEYS:
            if low.startswith(key):
                keep = True
                break
        if keep:
            header.append(line if line.endswith("\n") else line + "\n")
        i += 1
    return header


def is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def is_type_checking_test(node: ast.AST) -> bool:
    return is_name(node, "TYPE_CHECKING")


def has_typing_name(node: ast.AST) -> bool:
    for item in ast.walk(node):
        if isinstance(item, ast.Name) and item.id in TYPING_NAMES:
            return True
    return False


def strip_docstring_from_body(body: list[ast.stmt]) -> list[ast.stmt]:
    if not body:
        return body
    first = body[0]
    if isinstance(first, ast.Expr):
        v = first.value
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            return body[1:]
    return body


def strip_slots_from_class_body(body: list[ast.stmt]) -> list[ast.stmt]:
    out: list[ast.stmt] = []
    for stmt in body:
        if isinstance(stmt, ast.Assign):
            drop = False
            for t in stmt.targets:
                if is_name(t, "__slots__"):
                    drop = True
                    break
            if drop:
                continue
        if isinstance(stmt, ast.AnnAssign) and is_name(stmt.target, "__slots__"):
            continue
        out.append(stmt)
    return out


def strip_annotations_from_args(args: ast.arguments) -> None:
    for a in args.posonlyargs:
        a.annotation = None
    for a in args.args:
        a.annotation = None
    for a in args.kwonlyargs:
        a.annotation = None
    if args.vararg is not None:
        args.vararg.annotation = None
    if args.kwarg is not None:
        args.kwarg.annotation = None


class BundleStripper(ast.NodeTransformer):
    def visit_If(self, node: ast.If):  # type: ignore[override]
        self.generic_visit(node)
        if is_type_checking_test(node.test):
            return node.orelse
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):  # type: ignore[override]
        if node.module == "typing":
            return None
        return node

    def visit_Assign(self, node: ast.Assign):  # type: ignore[override]
        self.generic_visit(node)
        if has_typing_name(node.value):
            return None
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign):  # type: ignore[override]
        self.generic_visit(node)
        if node.value is None:
            return None
        return ast.Assign(targets=[node.target], value=node.value)

    def visit_FunctionDef(self, node: ast.FunctionDef):  # type: ignore[override]
        has_overload = False
        for deco in node.decorator_list:
            if is_name(deco, "overload"):
                has_overload = True
                break
        if has_overload:
            return None

        self.generic_visit(node)
        node.returns = None
        strip_annotations_from_args(node.args)
        node.decorator_list = [d for d in node.decorator_list if not is_name(d, "overload")]
        node.body = strip_docstring_from_body(node.body)
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):  # type: ignore[override]
        has_overload = False
        for deco in node.decorator_list:
            if is_name(deco, "overload"):
                has_overload = True
                break
        if has_overload:
            return None

        self.generic_visit(node)
        node.returns = None
        strip_annotations_from_args(node.args)
        node.decorator_list = [d for d in node.decorator_list if not is_name(d, "overload")]
        node.body = strip_docstring_from_body(node.body)
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_ClassDef(self, node: ast.ClassDef):  # type: ignore[override]
        self.generic_visit(node)
        # Keep protocol-like runtime stubs, but drop Protocol base so runtime
        # does not require typing.Protocol.
        node.bases = [b for b in node.bases if not is_name(b, "Protocol")]
        node.body = strip_docstring_from_body(node.body)
        node.body = strip_slots_from_class_body(node.body)
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_Module(self, node: ast.Module):  # type: ignore[override]
        self.generic_visit(node)
        node.body = strip_docstring_from_body(node.body)
        return node


def remove_blank_lines(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.strip() == "":
            continue
        out.append(line)
    return "".join(out)


def compress_indent(text: str, per_level: int) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.strip() == "":
            continue
        stripped = line.lstrip(" ")
        leading = len(line) - len(stripped)
        if leading % 4 == 0:
            level = leading // 4
            out.append((" " * (level * per_level)) + stripped)
        else:
            out.append(line)
    return "".join(out)


def parse_or_die(text: str, label: str) -> None:
    try:
        ast.parse(text)
    except SyntaxError as exc:
        raise RuntimeError(label + ": invalid python after minify") from exc


def run_python_minifier(text: str) -> tuple[str, str]:
    try:
        import python_minifier  # type: ignore
    except Exception as exc:
        raise RuntimeError("python_minifier unavailable: " + type(exc).__name__) from exc

    try:
        safe_kwargs = {
            # Never rename identifiers in our runtime code.
            "rename_locals": False,
            "rename_globals": False,
            # Keep behavior predictable for PocketPy.
            "hoist_literals": False,
            "remove_literal_statements": False,
            "remove_pass": False,
            "remove_object_base": False,
            "combine_imports": False,
            "convert_posargs_to_args": False
        }
        sig = inspect.signature(python_minifier.minify)
        filtered = {}
        for k, v in safe_kwargs.items():
            if k in sig.parameters:
                filtered[k] = v
        minimized = python_minifier.minify(text, **filtered)
        return (minimized, "python_minifier applied")
    except Exception as exc:
        raise RuntimeError("python_minifier failed: " + type(exc).__name__) from exc


def pocketpy_compat_after_pymin(text: str) -> str:
    # python-minifier can emit `for(i,x)in ...`, which PocketPy parser rejects.
    text = re.sub(r"\bfor\s*\(([^)\n]+)\)\s*in\b", r"for \1 in", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    args = parser.parse_args()

    src_path = Path(args.src)
    dst_path = Path(args.dst)

    source = src_path.read_text(encoding="utf-8")
    original_bytes = len(source.encode("utf-8"))

    header = extract_metadata_header(source.splitlines(keepends=True))

    mod = ast.parse(source)
    mod = BundleStripper().visit(mod)  # type: ignore[assignment]
    ast.fix_missing_locations(mod)
    body = ast.unparse(mod) + "\n"
    parse_or_die(body, "after ast strip")

    body, pymin_msg = run_python_minifier(body)
    body = pocketpy_compat_after_pymin(body)
    parse_or_die(body, "after python_minifier")

    body = remove_blank_lines(body)
    body = compress_indent(body, 1)
    body = remove_blank_lines(body)
    parse_or_die(body, "after indent compression")

    result = "".join(header) + body
    parse_or_die(result, "final output")

    dst_path.write_text(result, encoding="utf-8", newline="\n")

    final_bytes = len(result.encode("utf-8"))
    saved = original_bytes - final_bytes
    pct = 0.0 if original_bytes == 0 else (saved / float(original_bytes)) * 100.0
    print("minify: bytes_before=" + str(original_bytes)
          + " bytes_after=" + str(final_bytes)
          + " saved=" + str(saved)
          + " saved_pct=" + str(round(pct, 2)))
    print("minify: " + pymin_msg + " used=yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
