#!/usr/bin/env python3
"""Checks that no hard rule from the original AGENTS.md is lost in the proposal.

usage: check_rules.py ORIGINAL NEW [other files where content was moved...]
Exits with code 1 if any rule is missing.
"""
import difflib
import re
import sys

from audit_agents import HARD


def norm(s: str) -> str:
    s = re.sub(r"[`*_>#\-\u2022]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def rules(text: str):
    out = []
    for line in text.splitlines():
        if HARD.search(line) and len(line.strip()) > 15:
            out.append(line.strip())
    return out


def main(orig: str, targets: list[str]) -> int:
    original = rules(open(orig, encoding="utf-8").read())
    corpus_lines = []
    for p in targets:
        try:
            corpus_lines += [norm(l) for l in open(p, encoding="utf-8").read().splitlines() if l.strip()]
        except FileNotFoundError:
            print(f"warning: {p} does not exist")
    corpus = "\n".join(corpus_lines)

    missing, changed = [], []
    for r in original:
        n = norm(r)
        if n in corpus:
            continue
        best = difflib.get_close_matches(n, corpus_lines, n=1, cutoff=0.0)
        ratio = difflib.SequenceMatcher(None, n, best[0]).ratio() if best else 0.0
        (changed if ratio >= 0.85 else missing).append((r, ratio, best[0] if best else ""))

    print(f"Hard rules in the original: {len(original)}")
    print(f"Intact: {len(original) - len(missing) - len(changed)}")
    print(f"Changed (similar, review by hand): {len(changed)}")
    for r, ratio, b in changed:
        print(f"  ~{ratio:.2f}  ORIGINAL: {r[:110]}\n         NOW:      {b[:110]}")
    print(f"MISSING: {len(missing)}")
    for r, ratio, _ in missing:
        print(f"  {r[:140]}")
    return 1 if missing else 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2:]))
