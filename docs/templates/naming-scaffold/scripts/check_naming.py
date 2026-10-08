#!/usr/bin/env python3
"""
新项目命名静态检查（后端）。

检查：
1. Index("...") / UniqueConstraint(..., name="...") 前缀须为 ix_ / uq_ / fk_ / pk_ / ck_
   （兼容存量 idx_，但新项目建议只允许 ix_；用 --strict 关掉 idx_）
2. Field(..., serialization_alias="camelCase") 或 alias 指向 camelCase → 失败
3. SQLEnum(..., name="concatenated") 无下划线的多词类型名 → 警告/失败（--strict）

用法:
  python scripts/check_naming.py backend/app
  python scripts/check_naming.py backend/app --strict
  python scripts/check_naming.py backend/app --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

INDEX_NAME = re.compile(
    r"""(?:Index|UniqueConstraint)\s*\([^)]*?name\s*=\s*["']([^"']+)["']""",
    re.S,
)
INDEX_POS = re.compile(r"""Index\s*\(\s*["']([^"']+)["']""")
ALIAS = re.compile(
    r"""(?:serialization_alias|validation_alias|alias)\s*=\s*["']([^"']+)["']"""
)
SQLENUM_NAME = re.compile(r"""SQLEnum\s*\([^)]*?name\s*=\s*["']([^"']+)["']""", re.S)

ALLOWED_PREFIX_DEFAULT = ("ix_", "idx_", "uq_", "fk_", "pk_", "ck_")
ALLOWED_PREFIX_STRICT = ("ix_", "uq_", "fk_", "pk_", "ck_")


def is_camel(s: str) -> bool:
    return bool(re.search(r"[a-z][A-Z]", s))


def looks_concatenated_enum_type(name: str) -> bool:
    """celltype / lessonstatus — 多词却无下划线。"""
    if "_" in name:
        return False
    if name.isupper() or len(name) <= 6:
        return False
    # 简单启发：全小写且较长
    return name.islower() and len(name) >= 8


def check_file(path: Path, strict: bool) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    errors: list[str] = []
    allowed = ALLOWED_PREFIX_STRICT if strict else ALLOWED_PREFIX_DEFAULT

    names = [m.group(1) for m in INDEX_NAME.finditer(text)]
    names += [m.group(1) for m in INDEX_POS.finditer(text)]
    for name in names:
        if name.startswith(allowed):
            continue
        # UniqueConstraint 有时 name=unique_* —— 新项目不鼓励
        errors.append(f"{path}: bad index/constraint name {name!r} (want prefix {allowed})")

    for m in ALIAS.finditer(text):
        alias = m.group(1)
        if is_camel(alias):
            errors.append(f"{path}: camelCase serialization/alias {alias!r} is forbidden")

    for m in SQLENUM_NAME.finditer(text):
        en = m.group(1)
        if looks_concatenated_enum_type(en):
            msg = f"{path}: enum type name {en!r} should be snake_case (e.g. cell_type)"
            if strict:
                errors.append(msg)
            else:
                errors.append("WARN: " + msg)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="Directory to scan (e.g. backend/app)")
    ap.add_argument("--strict", action="store_true", help="Disallow idx_ and concatenated enum type names")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if not args.root.is_dir():
        print(f"Not a directory: {args.root}", file=sys.stderr)
        return 2

    all_errs: list[str] = []
    for path in sorted(args.root.rglob("*.py")):
        if path.name.startswith("test_"):
            continue
        all_errs.extend(check_file(path, args.strict))

    warns = [e for e in all_errs if e.startswith("WARN:")]
    errs = [e for e in all_errs if not e.startswith("WARN:")]

    if not args.quiet:
        for w in warns:
            print(w)
        for e in errs:
            print(e)

    if errs:
        print(f"\ncheck_naming: {len(errs)} error(s), {len(warns)} warning(s)", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"check_naming: OK ({len(warns)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
