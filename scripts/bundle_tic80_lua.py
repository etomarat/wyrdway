import argparse
import re
from pathlib import Path

META_KEYS = [
    "-- title:",
    "-- author:",
    "-- desc:",
    "-- site:",
    "-- license:",
    "-- version:",
    "-- script:"
]

REQUIRE_RE = re.compile(
    r'^\s*require\s*\(?\s*["\']([^"\']+)["\']\s*\)?\s*$'
)


def extract_metadata_header(lines: list[str]) -> tuple[list[str], int]:
    header: list[str] = []
    index = 0
    count = len(lines)
    while index < count:
        line = lines[index]
        stripped = line.strip()
        if stripped == "":
            index += 1
            continue
        if not line.lstrip().startswith("--"):
            break
        lowered = line.lstrip().lower()
        keep = False
        for key in META_KEYS:
            if lowered.startswith(key):
                keep = True
                break
        if not keep:
            break
        header.append(line if line.endswith("\n") else line + "\n")
        index += 1
    return header, index


class LuaBundler:
    def __init__(self, entry_path: Path) -> None:
        self.entry_path = entry_path.resolve()
        self.root_dir = self.entry_path.parent
        self.seen: set[Path] = set()

    def bundle(self) -> str:
        lines = self.entry_path.read_text(encoding="utf-8").splitlines(
            keepends=True
        )
        header, start_index = extract_metadata_header(lines)
        body = self._bundle_lines(self.entry_path, lines[start_index:], True)

        output: list[str] = []
        output.extend(header)
        if header and body and body[0].strip() != "":
            output.append("\n")
        output.extend(body)
        text = "".join(output)
        if not text.endswith("\n"):
            text += "\n"
        return text

    def _bundle_lines(
        self,
        source_path: Path,
        lines: list[str],
        is_entry: bool
    ) -> list[str]:
        out: list[str] = []
        if not is_entry:
            resolved = source_path.resolve()
            if resolved in self.seen:
                return out
            self.seen.add(resolved)
            out.append(f"-- BEGIN {self._display_path(resolved)}\n")

        for line in lines:
            match = REQUIRE_RE.match(line)
            if match is None:
                out.append(line if line.endswith("\n") else line + "\n")
                continue

            required_path = self._resolve_module(match.group(1))
            required_lines = required_path.read_text(
                encoding="utf-8"
            ).splitlines(keepends=True)
            out.extend(self._bundle_lines(required_path, required_lines, False))

        if not is_entry:
            out.append(f"-- END {self._display_path(source_path.resolve())}\n")
            out.append("\n")
        return out

    def _resolve_module(self, module_name: str) -> Path:
        relative = Path(*module_name.split("/")).with_suffix(".lua")
        candidate = (self.root_dir / relative).resolve()
        if candidate.exists():
            return candidate
        raise FileNotFoundError("Lua module not found: " + module_name)

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir))
        except ValueError:
            return str(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    args = parser.parse_args()

    src_path = Path(args.src)
    dst_path = Path(args.dst)

    bundler = LuaBundler(src_path)
    bundled = bundler.bundle()

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(bundled, encoding="utf-8")

    src_bytes = len(src_path.read_bytes())
    dst_bytes = len(bundled.encode("utf-8"))
    print(f"[lua-bundle] entry: {src_path}")
    print(f"[lua-bundle] output: {dst_path}")
    print(f"[lua-bundle] size: {src_bytes} -> {dst_bytes} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
