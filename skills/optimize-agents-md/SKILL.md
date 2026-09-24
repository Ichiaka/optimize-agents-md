---
name: optimize-agents-md
description: Reviews AGENTS.md (or CLAUDE.md) and the other files the agent reads often, and proposes versions that cost fewer tokens without losing any rule or any record. Use it when the operator asks to shrink or clean up AGENTS.md or the documentation, when the console runs out of context early, when AGENTS.md exceeds about 4,000 tokens, after adding many rules or ADRs in a row, or when the automatic check recommends a review. Never applies changes without the operator's approval.
---

# Optimize AGENTS.md

AGENTS.md is loaded in full at the start of every session. Every unnecessary line is paid
for in every session. The goal is to make it cheaper **without losing or changing any
rule**: content is moved and condensed, not deleted.

## Principles, non-negotiable

1. **No rule is lost.** Every rule in the original must end up either in the new
   AGENTS.md or in a file AGENTS.md points to. `scripts/check_rules.py` verifies this;
   if it fails, nothing is proposed.
2. **Hard rules stay in AGENTS.md, verbatim.** Invariants, production rules,
   prohibitions (NEVER, ALWAYS, forbidden, do not touch…), security, secrets,
   deployment discipline. They are not rewritten or summarized.
3. **Meaning does not change.** Condensing the wording of something explanatory, yes;
   softening or hardening a rule, no. When in doubt, leave it alone.
4. **Progressive disclosure.** Whatever is only needed for certain tasks moves to
   `docs/agents/<topic>.md`, and AGENTS.md keeps one line saying what is there and **when**
   to read it ("Before touching the database, read docs/agents/database.md").
5. **Reference instead of copying.** If a paragraph repeats what an ADR or a file in
   docs/ already says, it is replaced by the reference ("see ADR-012").
6. **No new rules are added** and no code is touched.

## What is usually superfluous in AGENTS.md

- History and reasons behind past decisions (that lives in the ADRs).
- Long examples, result listings, status or decision tables.
- Instructions for specific tasks that are not done in every session.
- Repetitions of the same rule across several sections.
- Explanations of why a rule exists (the rule stays; the why goes to the ADR).

## Workflow

1. **Measure.** `python3 scripts/audit_agents.py AGENTS.md` → estimated tokens,
   sections sorted by size, repeated lines and lines containing hard rules.
2. **Classify each section** into one of three:
   - *Always* — needed in any session: it stays.
   - *Sometimes* — only for certain tasks: moves to docs/agents/ with a pointer.
   - *Historical* — reasons, results, examples: replaced by a reference to the
     ADR or file where it already lives (if it lives nowhere, it is moved, not deleted).
3. **Write the proposal to a copy**, never over the original:
   `AGENTS.proposed.md` plus the new files in docs/agents/.
4. **Check that nothing is lost:**
   `python3 scripts/check_rules.py AGENTS.md AGENTS.proposed.md docs/agents/*.md docs/*.md`
   If it lists any missing rule, fix it and check again. Do not continue with failures.
5. **Measure the copy again** and compute the savings.
6. **Report to the operator** with:
   - tokens before and after, and the savings per session;
   - a table of sections: where they were, where they end up, and why;
   - the output of check_rules.py (it must say 0 missing rules);
   - any doubtful case you left untouched.
7. **Apply only with the operator's explicit approval:** replace AGENTS.md,
   add the docs/agents/ files, update `.agents-baseline.json` with the new token
   count and the UTC date (`{"file": "AGENTS.md", "tokens": N, "date": "..."}`),
   make a dedicated commit with a clear message, and
   publish it like any other documentation change.

## "all" mode

When the operator asks to review everything, the order and treatment depend on the file type:

1. **AGENTS.md first**, with the full workflow above. It is the most expensive one.
2. **Other instruction files**, one by one and with the same workflow: CLAUDE.md if it exists,
   docs/agents/*.md, .claude/skills/*/SKILL.md, .claude/commands/*.md and any other
   instruction file the agent reads at startup or when it receives a task.
   Each with its own proposed copy and its own check_rules.py run.
3. **Record files** (decision records or ADRs, changelogs, catalogs, logs,
   any document that keeps history or results): **their content is not rewritten or
   condensed**. They are the project's memory. Only reading aids are proposed:
   an index at the top listing the sections and their lines, uniform headings that can be
   searched with grep, and a note in AGENTS.md to search for the specific section
   instead of reading the whole file. Check with diff that the body stays identical.
4. To decide which record files deserve an index, measure their size with audit_agents.py
   and start with the largest and most frequently read.

Final report: one table per file with tokens before and after, type (instructions or
record), what was done and the check_rules.py result, plus the estimated total savings per
session and per batch. Everything as a proposal: nothing is applied without the operator's
"apply it", and the operator may approve individual files.

## Automatic mode (detects only, never modifies)

The periodic check does not use the agent and spends no tokens: it is the script, in quick mode.

    python3 scripts/audit_agents.py AGENTS.md --check

It recommends a review (exit code 2) if AGENTS.md exceeds 4,000 estimated tokens, or if it has
grown more than 20 % since the last approved optimization, recorded in `.agents-baseline.json`
at the project root. Otherwise it exits with 0. Thresholds are changed with --max-tokens and
--max-growth. It never writes anything.

Schedule it as a periodic system task (cron, a systemd timer, a CI step
or a git hook) and, when it exits with 2, notify the user through the project's usual channel.
**The notice only suggests running /optimize-agents: the optimization never runs on its own**,
because it rewrites the agent's instructions and requires human review.

## Limits

- If the savings are below 15 %, say so and do not propose changes: the risk is not worth it.
- If a section mixes hard rules and explanation, split it: the rule stays
  verbatim, the explanation moves.
- check_rules.py detects rules by keywords and approximate matching; it is not
  infallible. Also review by hand the rules it flags as "changed".
