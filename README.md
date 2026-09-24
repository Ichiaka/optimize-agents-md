# optimize-agents-md

**English** · [Español](README.es.md)

A skill for coding agents (Claude Code and compatible) that reviews the project's instruction
file —`AGENTS.md` or `CLAUDE.md`— and proposes a version that costs fewer tokens per session
**without losing or changing any rule**.

## Why

Coding agents read `AGENTS.md` in full at the start of every session. Everything in it takes up
working memory for the whole session, whether it is used or not. Over time, the file
accumulates history, explanations and examples that are not always needed.

## What it does

It moves, it does not delete. Content is split into three kinds:

- **Always needed** (rules, prohibitions, security, deployment): stays, word for word.
- **Needed only for certain tasks**: moves to `docs/agents/`, with a line saying when to read it.
- **History and reasons**: replaced by a reference to the document where it already lives.

A checker looks for every rule from the original in the proposal and **fails if any has disappeared**.
Nothing is applied until the user says "apply it".

## Installation (Claude Code)

```bash
# from your project root
mkdir -p .claude/skills .claude/commands
cp -r path/to/this/repo/skill/optimize-agents-md .claude/skills/
cp path/to/this/repo/commands/optimize-agents.md .claude/commands/
```

Open a new session so the agent picks up the skill and the command.

## Usage

- `/optimize-agents` — reviews only `AGENTS.md`.
- `/optimize-agents all` — also reviews the other instruction files. For record documents
  (ADRs, changelogs, logs) the content is not changed: it only adds indexes so less has to be read.
- `/optimize-agents check` — only measures and says whether a review is worthwhile.
- `/optimize-agents path/to/file.md` — reviews only that file.

The agent measures, writes the proposal to a copy, runs the checker, and shows you the savings
and what was moved. Once you have reviewed it, say "apply it" or ask for changes.

## Automatic notice

The periodic check spends no tokens: it is the script in quick mode, and it never modifies anything.

```bash
python3 .claude/skills/optimize-agents-md/scripts/audit_agents.py AGENTS.md --check
```

It exits with 2 if `AGENTS.md` exceeds 4,000 tokens or has grown more than 20 % since the last
approved optimization (stored in `.agents-baseline.json`), and with 0 otherwise. Schedule it with cron,
systemd, your CI or a git hook, and have it notify you when it exits with 2. Example with cron, on Mondays:

```cron
0 9 * * 1  cd /path/to/project && python3 .claude/skills/optimize-agents-md/scripts/audit_agents.py AGENTS.md --check || echo "review AGENTS.md" | mail -s agents you@example.com
```

The optimization never runs on its own: the notice only suggests running `/optimize-agents`.
You can also check by hand with `/optimize-agents check`.

## Try it safely

```bash
cd skill/optimize-agents-md/scripts
python3 audit_agents.py ../../../example/AGENTS.md
python3 check_rules.py ../../../example/AGENTS.md ../../../example/AGENTS.proposed.md
```

The example proposal deliberately drops one rule: the checker must flag it and exit with code 1.

## Limits

- The checker recognizes rules by keywords (never, always, must, do not, forbidden, nunca, siempre…).
  A rule written without them could slip through; that is why it also flags rules whose wording
  changed. Human review is the final filter.
- If the savings are below 15 %, it does not propose changes.
- It does not add rules or touch code. The scripts only read files; they do not write, delete or use the network.
  The only file written, `.agents-baseline.json`, is updated by the agent when applying an approved optimization.
- Instructions are in English; the checker's keywords cover English and Spanish.

## License

MIT. See `LICENSE`.
