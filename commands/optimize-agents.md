---
description: Review AGENTS.md (or all the agent's files) with the optimize-agents-md skill and show the proposal without applying anything
argument-hint: [empty = AGENTS.md | all | check | path to a file]
---
Use the optimize-agents-md skill according to what is given here: "$ARGUMENTS".
- If empty: review only AGENTS.md (or CLAUDE.md if that is the one the project uses).
- If it says "all": use the skill's "all" mode, starting with AGENTS.md.
- If it says "check": run only `audit_agents.py AGENTS.md --check`, tell me the result and do nothing else.
- If it is a path: review only that file.

Follow the skill's workflow: measure with audit_agents.py, classify, write the proposals to copies, run check_rules.py until it reports 0 missing rules for each instruction file, and measure again. For record files, only reading aids, with the body left identical.

Show me:
- tokens before and after per file, and the total savings per session;
- what stays, what moves and where, and why;
- the output of check_rules.py, including rules flagged as changed;
- any doubtful cases you left untouched.

Do not replace any file or commit until I say "apply it". I may approve individual files.
