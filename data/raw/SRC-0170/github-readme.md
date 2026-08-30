# cmg — AI-powered Commit Message Generator

[![Go Version](https://img.shields.io/badge/go-1.25+-blue.svg)](https://go.dev)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)

Generate high-quality git commit messages from staged changes using AI. `cmg` analyzes your diffs and uses Claude, ChatGPT, or any LLM to produce clear, convention-compliant messages.

## Features

- **Multiple LLM providers**: Claude (via CLI or API), OpenAI API, or any custom CLI tool
- **Project-specific rules**: Define commit conventions in a simple Markdown file per project
- **Smart diff handling**: Analyzes staged changes with size warnings for large diffs
- **Interactive commit flow**: After generation, choose to commit, edit, or cancel — no extra flags needed
- **Interactive setup**: `cmg init` guides you through configuration
- **Secure config**: API keys stored locally with file permissions (0600), easily ignored in git

## Installation

### From Source

```bash
go install github.com/kokoa-tools/commit-message-generator@latest
```

Requires Go 1.25 or later.

## Quick Start

### 1. Initialize your project

```bash
cd your-git-repo
cmg init
```

This creates `.commit-generator/config.json` with your LLM provider settings. You'll be prompted to:
- Choose an LLM provider (Claude CLI, custom CLI, Anthropic API, or OpenAI API)
- Set diff size thresholds
- Optionally create project-specific commit rules

### 2. Generate a commit message

Stage your changes and run:

```bash
git add .
cmg
```

`cmg` analyzes the diff, calls your LLM, and displays the generated message. You are then prompted to act:

```
────────────────────────────────────────────────────────────
feat: add interactive commit prompt with edit and regenerate

- Replace -c flag with automatic post-generation prompt
- Support Y/e/r/n choices for commit, edit, regenerate, cancel
- Open $EDITOR for in-place message editing
────────────────────────────────────────────────────────────

Commit with this message? [Y]es / [e]dit / [r]egenerate / [n]o:
```

| Key | Action |
|-----|--------|
| `Y` / Enter | Run `git commit` with the message |
| `e` | Open `$EDITOR` to edit the message, then re-prompt |
| `r` | Exit (re-run `cmg` to regenerate) |
| `n` | Cancel without committing |

### 3. (Optional) Set up project rules

```bash
cmg rules init
```

Create `.commit-generator/message-rules.md` to enforce conventions like "feat:" prefixes or emoji usage.

## Commands

### `cmg` / `cmg generate` / `cmg gen` / `cmg g`

Generate a commit message from staged changes.

**Flags:**
- `-f, --force` — Skip size warnings and proceed anyway
- `-y, --yes` — Auto-commit without prompting (useful in scripts)
- `-d, --dry-run` — Print the generated message only, skip the prompt

**Examples:**

```bash
# Generate and use interactive prompt (default)
cmg

# Skip size warnings
cmg --force

# Auto-commit without any prompts (scripting/CI)
cmg --yes

# Just print the message, no interaction
cmg --dry-run

# Combine: skip warnings and auto-commit
cmg -fy
```

### `cmg init`

Initialize `.commit-generator/` in your git repository.

Creates:
- `.commit-generator/config.json` with LLM provider configuration
- (Optional) `.commit-generator/message-rules.md` with project-specific conventions

**Recommended:** Add `.commit-generator/config.json` to `.gitignore` to avoid committing API keys.

### `cmg config`

View current configuration (API keys are masked).

```bash
cmg config
```

### `cmg config set <key> <value>`

Modify configuration values without reinitializing.

**Valid keys:**
- `provider` — `claude-cli`, `cli`, `openai`, or `anthropic`
- `cli_command` — Command name (for `cli` or `claude-cli`)
- `cli_args` — Arguments before the prompt (space-separated)
- `api_key` — API key for `openai` or `anthropic`
- `model` — Model name (e.g., `gpt-4o`, `claude-opus-4-6`)
- `max_diff_bytes` — Threshold for byte size warning (default: 51200)
- `max_diff_lines` — Threshold for line count warning (default: 1000)

**Examples:**

```bash
# Switch to OpenAI
cmg config set provider openai
cmg config set api_key sk-...
cmg config set model gpt-4o

# Update diff thresholds
cmg config set max_diff_bytes 102400
cmg config set max_diff_lines 2000
```

### `cmg rules` / `cmg rules show`

Display current project-specific commit rules.

```bash
cmg rules
```

### `cmg rules init`

Create `.commit-generator/message-rules.md` interactively.

You'll be prompted for:
- Commit message format (e.g., `feat: description`)
- Allowed types/prefixes
- Maximum subject line length
- Whether to include emoji
- Language for messages
- Additional rules or examples

Generated file is safe to commit to the repository.

### `cmg rules edit`

Open `message-rules.md` in your default editor (`$EDITOR` or `$VISUAL`).

```bash
cmg rules edit
```

## LLM Provider Configuration

Choose a provider during `cmg init` or update it later with `cmg config set provider <name>`.

| Provider | Setup | Use Case | Cost |
|----------|-------|----------|------|
| **claude-cli** | Install [claude](https://github.com/anthropics/anthropic-cli) CLI | Free/included in CLI plan | No direct cost |
| **cli** | Any LLM CLI tool (e.g., `kiro`, `ollama`) | Custom/local models | Varies |
| **openai** | Get API key from [OpenAI](https://platform.openai.com) | ChatGPT models | Pay-per-use |
| **anthropic** | Get API key from [Anthropic](https://console.anthropic.com) | Claude models | Pay-per-use |

### Provider-Specific Configuration

#### Claude CLI (Recommended)

```bash
cmg init
# Choose option 1: claude-cli
# It will verify `claude` is available in PATH
```

No API key needed. Uses your existing Claude CLI setup.

#### Custom CLI (e.g., kiro, ollama)

```bash
cmg config set provider cli
cmg config set cli_command kiro
cmg config set cli_args "-p"
```

Your command will be invoked as:
```
<cli_command> <cli_args> <prompt_text>
```

The prompt is piped as stdin.

#### OpenAI API

```bash
cmg config set provider openai
cmg config set api_key sk-...
cmg config set model gpt-4o
```

#### Anthropic API

```bash
cmg config set provider anthropic
cmg config set api_key sk-ant-...
cmg config set model claude-opus-4-6
```

## Project-Specific Rules (message-rules.md)

Create `.commit-generator/message-rules.md` to enforce project conventions. The AI generator reads this file and follows all specified rules.

### Format

A simple Markdown file with sections:

```markdown
# Commit Message Rules

These rules are enforced by the AI when generating commit messages for this project.

## Format

feat: short description
fix: short description
docs: short description

## Allowed Types

feat, fix, docs, style, refactor, perf, test, chore

## Subject Line

- Maximum 72 characters
- Use imperative mood ("Add" not "Added")
- Do not end with a period

## Language

Write commit messages in English.

## Examples

feat: add user authentication system
fix: resolve race condition in worker pool
docs: update README with new API endpoints
```

### Creating Rules

Use the interactive prompt:

```bash
cmg rules init
```

Or edit directly:

```bash
cmg rules edit
```

### Tips

- Keep rules concise and clear
- Focus on format, conventions, and language
- Include 2-3 examples
- All sections are optional; the AI uses sensible defaults if rules aren't set

## Configuration Storage

Configuration is stored at `.commit-generator/config.json` in your git repository.

### File Structure

```json
{
  "provider": "claude-cli",
  "cli_command": "claude",
  "cli_args": ["-p"],
  "api_key": "",
  "model": "",
  "max_diff_bytes": 51200,
  "max_diff_lines": 1000
}
```

### Security Note

API keys are stored in plaintext in `config.json`. **Add it to `.gitignore`:**

```bash
echo ".commit-generator/config.json" >> .gitignore
```

File permissions are set to 0600 (readable only by the owner). To verify:

```bash
ls -la .commit-generator/config.json
# -rw------- user group ...
```

The `message-rules.md` file is safe to commit — it contains no secrets.

## Workflow Examples

### Using with Claude CLI

```bash
# Initialize
cmg init
# → Choose option 1: claude-cli

# Stage and generate
git add src/auth.go
cmg
# → Review message
# → Press Y to commit, e to edit in $EDITOR, n to cancel
```

### Using with OpenAI

```bash
# Initialize
cmg init
# → Choose option 4: openai
# → Enter your API key and model (gpt-4o)

# Skip warnings and auto-commit without prompts
cmg -fy
```

### Using with Anthropic API

```bash
# Initialize
cmg init
# → Choose option 3: anthropic
# → Enter your API key and model (claude-opus-4-6)

# Generate, then edit message before committing
cmg
# → Press e to open $EDITOR, tweak the message, save and exit
# → Press Y to commit with the edited message
```

### Using with Custom CLI (kiro)

```bash
# Initialize
cmg init
# → Choose option 2: cli
# → Enter command: kiro
# → Enter args: (leave blank or enter custom flags)

# Generate with dry-run to preview only
cmg --dry-run
```

## Troubleshooting

### "no config found — Run `cmg init` to set up"

You're not in a git repository or `.commit-generator/config.json` doesn't exist.

```bash
cd your-repo
cmg init
```

### "no staged changes found"

You haven't staged any files yet.

```bash
git add your-changes
cmg
```

### API key errors (OpenAI / Anthropic)

Check that:
1. Your API key is correct: `cmg config` (it will be masked)
2. Your API key has sufficient quota/permissions
3. You're online

### Claude CLI not found

The `claude` command isn't in your PATH.

```bash
which claude
# If empty, install: https://github.com/anthropics/anthropic-cli

# Or use a custom CLI provider:
cmg config set provider cli
cmg config set cli_command /path/to/your/llm-tool
```

### Large diff warnings

If your diff is very large, the AI may generate lower-quality messages. Either:
- Use `--force` to skip the warning
- Split into smaller commits (recommended)
- Increase thresholds:
  ```bash
  cmg config set max_diff_bytes 204800
  cmg config set max_diff_lines 5000
  ```

## Development

Clone and build:

```bash
git clone https://github.com/koajs/commit-message-generator.git
cd commit-message-generator
go build -o cmg main.go
./cmg --help
```

Run tests:

```bash
go test ./...
```

## License

MIT

## Contributing

Contributions welcome. Submit issues and PRs to the [GitHub repository](https://github.com/koajs/commit-message-generator).
