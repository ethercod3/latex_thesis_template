Generate a commit message for the current staged changes.

Use exactly one Conventional Commit summary line.

Format:
<type>(<scope>): <summary>

or, if there is no clear scope:
<type>: <summary>

Rules:
- Use one of: feat, fix, chore, docs, test, refactor, perf, ci, build, style.
- Use lowercase.
- Use imperative mood.
- Keep it under 72 characters when possible.
- Do not end with a period.
- Do not add explanations, bullets, markdown, or body text.
- Infer the scope from the changed files when obvious.
- Omit the scope if it would be vague or forced.

Examples:
fix(fish): honor GO_TASK_PROGNAME for experiments cache
chore: add website/.netlify to gitignore
feat(strings): add joinEnv and joinUrl functions