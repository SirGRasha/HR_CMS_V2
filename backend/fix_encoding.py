from pathlib import Path

ROOT = Path("apps")

for path in ROOT.rglob("*.py"):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    try:
        fixed = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        continue

    if fixed != text:
        backup = path.with_suffix(path.suffix + ".bak")
        backup.write_text(text, encoding="utf-8")
        path.write_text(fixed, encoding="utf-8")
        print(f"FIXED: {path}")
