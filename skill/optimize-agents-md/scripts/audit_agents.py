#!/usr/bin/env python3
"""Measures AGENTS.md: estimated tokens, sections by size, repeated lines and hard rules.

usage:
  audit_agents.py AGENTS.md
      full report.
  audit_agents.py AGENTS.md --check [--max-tokens 4000] [--max-growth 20] [--baseline .agents-baseline.json]
      quick check meant to run on a schedule. Writes nothing.
      Exit 0: no review needed. Exit 2: review recommended. Exit 1: error.
"""
import argparse
import json
import re
import sys
from collections import Counter

# Keywords in English and Spanish, so instruction files in either language are covered.
HARD = re.compile(
    r"\b(never|always|must|must not|shall|do not|don't|forbidden|prohibited|mandatory|"
    r"invariant|nunca|siempre|jam[aá]s|prohibid[oa]s?|no se toca|no toques|obligatori[oa]|"
    r"invariante|debe[n]?)\b",
    re.IGNORECASE,
)


def tokens(text: str) -> int:
    # Approximation: ~3.6 characters per token in technical prose.
    return round(len(text) / 3.6)


def sections(text: str):
    cur, buf, out = "(start)", [], []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s", line):
            out.append((cur, "\n".join(buf)))
            cur, buf = line.strip(), []
        else:
            buf.append(line)
    out.append((cur, "\n".join(buf)))
    return [(t, b) for t, b in out if b.strip() or t != "(start)"]


def report(path: str) -> None:
    text = open(path, encoding="utf-8").read()
    total = tokens(text)
    print(f"{path}: {len(text):,} characters, ~{total:,} tokens per session\n")

    print("Sections by size:")
    for title, body in sorted(sections(text), key=lambda s: -len(s[1])):
        t = tokens(body)
        hard = sum(1 for l in body.splitlines() if HARD.search(l))
        print(f"  ~{t:>5} tok  {100 * t / max(total, 1):5.1f} %  hard rules: {hard:>3}  {title}")

    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 30]
    dup = [(l, n) for l, n in Counter(lines).items() if n > 1]
    print(f"\nLines repeated verbatim: {len(dup)}")
    for l, n in sorted(dup, key=lambda x: -x[1])[:15]:
        print(f"  x{n}  {l[:100]}")

    hard_lines = [l for l in text.splitlines() if HARD.search(l)]
    print(f"\nLines with hard rules (kept verbatim): {len(hard_lines)}")


def check(path: str, max_tokens: int, max_growth: float, baseline: str) -> int:
    now = tokens(open(path, encoding="utf-8").read())
    reasons = []
    if now > max_tokens:
        reasons.append(f"~{now:,} tokens, above the limit of {max_tokens:,}")
    base = None
    try:
        base = json.load(open(baseline, encoding="utf-8"))
    except FileNotFoundError:
        pass
    if base and base.get("tokens"):
        growth = 100 * (now - base["tokens"]) / base["tokens"]
        if growth > max_growth:
            date = base.get("date") or base.get("fecha") or "unknown date"
            reasons.append(
                f"has grown {growth:.0f} % since the last optimization "
                f"({base['tokens']:,} tokens, {date})"
            )
    if reasons:
        print(f"{path}: review recommended: " + "; ".join(reasons) + ". Run /optimize-agents.")
        return 2
    ref = f", baseline {base['tokens']:,}" if base and base.get("tokens") else ", no baseline recorded"
    print(f"{path}: OK (~{now:,} tokens{ref}).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=4000)
    ap.add_argument("--max-growth", type=float, default=20.0)
    ap.add_argument("--baseline", default=".agents-baseline.json")
    a = ap.parse_args()
    try:
        if a.check:
            return check(a.file, a.max_tokens, a.max_growth, a.baseline)
        report(a.file)
        return 0
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
