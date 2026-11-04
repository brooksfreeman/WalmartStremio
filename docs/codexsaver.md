# CodexSaver for this project

## Current restriction — owner clarification, November 2

Do not use affected live delegation paths until the reported issues are
demonstrably fixed. The owner reviewed the installed implementation and reports:

- Direct delegate_task verification can execute worker-suggested commands with
  shell=True in the real workspace before Codex review.
- Work-packet copying does not exclude .private, .env or .tv_auth.
- Pi's tools-disabled configuration does not protect these separate paths.

No repair or safe live route has been demonstrated in the Home clarification
pass. This status supersedes live-call examples below. Do not treat a request
for “no commands”, gitignore, forbidden patch paths, dry runs or a sandbox label
as context/command isolation. Continue in Codex; tooling repair is separate from
TV investigation. Keep native/security/device/service/architecture work in Codex
regardless of worker availability. These are owner-reported findings, not a new
implementation audit in this pass.

## Historical installation and setup record

CodexSaver 0.3.6 is installed from
<https://github.com/fendouai/CodexSaver> at commit
`fe44dc105070c1f40eef29d9be76438edeab9987` in
`~/.local/share/codexsaver`, using an isolated Python environment. The
`codexsaver` command is linked into `~/.local/bin`. Pi Agent 1.5.0 is installed
from `@earendil-works/pi-coding-agent` and linked as `~/.local/bin/pi`.

The project-local MCP entry is in `.codex/config.toml`. It uses absolute paths
to the installed Python and server, so there is no dependency on a `python`
command or a server file in this project. That machine-specific file is ignored
by git. Other Codex projects do not acquire this server from this setup.
Codex supports project MCP configuration for trusted projects; see the
[official MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Finish DeepSeek authentication

Run this from a terminal in the project directory:

```bash
python3 scripts/setup_codexsaver.py
```

Enter your DeepSeek API key at the hidden prompt. The helper saves it to
`~/.codexsaver/config.json` and `~/.pi/agent/auth.json`, both with mode `0600`.
It does not put the key in shell history, process arguments, project files,
or terminal output. It does not validate the key or make a paid model call.
DeepSeek API usage is billed separately from a ChatGPT subscription.

After saving the key, restart the CodexSaver MCP server in Settings → MCP
servers, or reopen Codex. Check `/mcp` for `codexsaver`.

## Use it in this project

`AGENTS.md` asks Codex to use CodexSaver for bounded routine work. For example:

> Use CodexSaver to explain web/launcher.html. Send only that file and review
> the result here.

Use a real existing public source file for the request. Every MCP call should
pass this project's absolute directory as `workspace` and a short, explicit
file list. Workers receive the selected file contents through CodexSaver.
The project Agent Card disables Pi's tools, extensions, MCP servers, skills,
prompt templates, automatic context-file loading, and persistent sessions.
Pi can return explanations and proposed patches; Codex reviews and applies them.
`--offline` disables Pi startup network operations, not the requested model call.

Do not send `.private/`, credentials, private device captures, or personal
account configuration. The context packer does not enforce git ignore rules.
Live TV/device operations and the active native-installation investigation
remain with Codex.

## Check installation

Installation checks on November 2, 2026 passed: the Codex CLI recognized the
project MCP entry, a real stdio connection returned server version `0.3.6`, all
five tools were listed, the project Pi Agent Card was discovered, direct and
orchestration dry runs succeeded, and `pip check` found no broken requirements.
No live worker call was tested at installation because no DeepSeek key was saved.

```bash
codexsaver doctor --workspace .
codexsaver agents list --workspace .
codexsaver delegate "Explain the project layout briefly" --files README.md --workspace . --dry-run
```

The dry run makes no model call. After authentication, remove `--dry-run` for
a small live provider test. `delegate` uses CodexSaver's direct DeepSeek
provider; `orchestrate` and read-only specialists use Pi Agent.

The upstream `doctor` also checks for `codexsaver_mcp.py` in the workspace root
and may recommend running from the CodexSaver source checkout. This project
intentionally launches the separately installed server by absolute path;
`script_exists: false` alone does not mean that the MCP launch failed. Use
`codex mcp get codexsaver` and an MCP connection check to validate the configured
server. A successful dry run does not prove a key or paid worker call works.

## Update or remove

To update deliberately:

```bash
git -C ~/.local/share/codexsaver pull --ff-only
~/.local/share/codexsaver/.venv/bin/python3 -m pip install -e ~/.local/share/codexsaver
npm install -g @earendil-works/pi-coding-agent
```

Restart the MCP server afterward and recheck compatibility. The current project
Agent Card uses `deepseek-v4-flash`; direct provider calls use upstream's
`deepseek-chat` default.

To disable this project's integration, set `enabled = false` under
`[mcp_servers.codexsaver]` in `.codex/config.toml`, then restart the MCP server.
