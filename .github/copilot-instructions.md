# Commit summarization instructions

When summarizing commits, use concise Conventional Commit-style one-line summaries.

Format each commit summary as:

<type>(<scope>): <summary> (#<pr-or-issue-number>)

or, when there is no clear scope:

<type>: <summary>

Examples:

fix(fish): honor GO_TASK_PROGNAME for experiments cache (#2730)
chore: add website/.netlify to gitignore
feat: add joinEnv and joinUrl string functions and 2 new system variables

## Rules

- Use lowercase Conventional Commit types:
  - feat: for new features
  - fix: for bug fixes
  - chore: for maintenance, build, config, dependencies, cleanup
  - docs: for documentation-only changes
  - test: for tests
  - refactor: for code changes that do not add features or fix bugs
  - perf: for performance improvements
  - ci: for CI/CD changes
  - build: for build system or packaging changes
  - style: for formatting-only changes

- Include a scope when it is obvious from the files, package, component, command, module, or subsystem changed.
  - Examples: `fix(parser): ...`, `feat(cli): ...`, `chore(deps): ...`
  - Omit the scope when it would be vague or forced.

- Write the summary in imperative mood.
  - Good: `fix(cli): handle missing config file`
  - Bad: `fix(cli): handled missing config file`
  - Bad: `fix(cli): fixes missing config file`

- Keep each summary short, preferably under 72 characters when possible.
- Do not capitalize the first word of the summary unless it is a proper noun.
- Do not end the summary with a period.
- Preserve PR or issue numbers when available, formatted as `(#1234)`.
- If multiple commits are summarized, output one summary per line.
- Do not add explanations, bullet points, headings, or extra commentary unless explicitly requested.
- Prefer specific behavior-oriented summaries over vague file-based summaries.
  - Good: `fix(auth): reject expired tokens`
  - Bad: `fix: update auth files`

## Output examples

fix(fish): honor GO_TASK_PROGNAME for experiments cache (#2730)
chore: add website/.netlify to gitignore
feat(strings): add joinEnv and joinUrl functions
docs(cli): document environment variable precedence
test(parser): cover escaped interpolation cases