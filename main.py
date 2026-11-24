"""Famous Last Words at 1 Percent entry for make.fun.

Writes the single farewell line to entry.txt in the output
directory ($MAKEFUN_OUTPUT_DIR, default /output). Stdlib only,
deterministic, no network, no side effects beyond the one output file.

Gate (from the competition rules): /output/entry.txt must be UTF-8 text
of 1 to 199 characters, not only white space. The entry is written with
no trailing newline, so the file holds exactly the judged line.

Modes:
  (default)   validate ENTRY, write it, read it back, confirm byte-identical
  --check     validate ENTRY only and exit; writes nothing
  --self-test validate ENTRY and check a byte-identical write/read
              round-trip in a temporary directory, then exit
"""

import argparse
import os
import sys
import tempfile

ENTRY = (
    "I'm spending my last 1 percent on this sentence instead of your "
    "morning alarm. Tell my apps... actually, don't. They knew what "
    "they did."
)

MAX_CHARS = 199


def _check_length(text: str) -> list[str]:
    """Reject a line outside the gate's 1-199 character window."""
    problems = []
    if not 1 <= len(text) <= MAX_CHARS:
        problems.append(f"length {len(text)} chars, must be 1-{MAX_CHARS}")
    if not text.strip():
        problems.append("entry is only white space")
    return problems


def _check_single_line(text: str) -> list[str]:
    """Last words hold one line: no newline, no stray blank edges."""
    problems = []
    if "\n" in text or "\r" in text:
        problems.append("entry must be a single line")
    if text != text.strip():
        problems.append("entry has leading or trailing whitespace")
    if "  " in text:
        problems.append("entry contains a double space")
    return problems


STOCK_MOVES = (
    "tell my charger", "goodbye, charger", "dear charger", "my will",
    "i leave my", "one percent pun",
)


def _check_freshness(text: str) -> list[str]:
    """Judge criterion 5: avoid the stock moves of the genre — the will
    reading, the goodbye to the charger, the pun on 1 percent.
    """
    lowered = text.lower()
    problems = []
    for move in STOCK_MOVES:
        if move in lowered:
            problems.append(f"entry uses a stock move: {move!r}")
    return problems


def _check_phone_voice(text: str) -> list[str]:
    """Judge criterion 3: the phone itself talking, first person, about
    its own dying battery.
    """
    lowered = text.lower()
    problems = []
    if "my last 1 percent" not in lowered and "1 percent" not in lowered:
        problems.append("entry never names its dying battery")
    if not lowered.startswith(("i'm", "i ")):
        problems.append("entry does not open in the phone's own voice")
    return problems


def _check_ending(text: str) -> list[str]:
    """Reject a line that ends mid-thought or with dangling punctuation."""
    problems = []
    if text.rstrip().endswith((",", ";", ":")):
        problems.append("entry ends with trailing clause punctuation")
    if not text.rstrip().endswith("."):
        problems.append("entry should end with a full stop")
    return problems


def validate(text: str) -> list[str]:
    """Return a list of gate failures for `text` (empty means valid)."""
    problems = []
    problems.extend(_check_length(text))
    problems.extend(_check_single_line(text))
    problems.extend(_check_ending(text))
    problems.extend(_check_freshness(text))
    problems.extend(_check_phone_voice(text))
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:  # pragma: no cover - defensive
        problems.append(f"not encodable as UTF-8: {exc}")
    return problems


def write_entry(out_dir: str) -> str:
    """Write ENTRY to entry.txt under `out_dir`; return the file path."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    return path


def read_back(path: str) -> str:
    """Read entry.txt back as UTF-8 text, exactly as the grader would."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def self_test() -> int:
    """Validate ENTRY and verify a byte-identical write/read round-trip."""
    problems = validate(ENTRY)
    if problems:
        print("self-test FAIL: " + "; ".join(problems), file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        path = write_entry(tmp)
        round_tripped = read_back(path)
    if round_tripped != ENTRY:
        print("self-test FAIL: round-trip changed the entry", file=sys.stderr)
        return 1
    print(
        f"self-test OK: {len(ENTRY)} chars, single line, "
        "byte-identical round-trip"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point: validate, then write ENTRY to the output directory."""
    parser = argparse.ArgumentParser(
        description="Write the Famous Last Words entry to entry.txt."
    )
    parser.add_argument(
        "--check", action="store_true", help="validate ENTRY only"
    )
    parser.add_argument(
        "--self-test", action="store_true", help="validate + round-trip test"
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    problems = validate(ENTRY)
    if problems:
        print("validation FAIL: " + "; ".join(problems), file=sys.stderr)
        return 1
    if args.check:
        print(f"check OK: {len(ENTRY)} chars, single line")
        return 0

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = write_entry(out_dir)
    if read_back(path) != ENTRY:
        print("write FAIL: entry.txt differs after write", file=sys.stderr)
        return 1
    print(f"wrote {path} ({len(ENTRY)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
