# Project guidance

Read `README.md` and `docs/RESUME-HERE.md` before continuing TV work.

<!-- CODEXSAVER:BEGIN -->
## CodexSaver

Use the project's `codexsaver` MCP server for bounded, low-risk code explanation,
documentation, code review drafts, and small patches when its worker is configured.
Use `delegate_task` for explanations, `run_specialist` for one specialist, and
`delegate_work_packet` for a patch with explicit allowed files and checks.
Always pass this project's absolute path as `workspace` and an explicit `files`
list. Send only the minimum public source or documentation needed for the task.

Never include `.private/`, `.env`, `.tv_auth`, credentials, pairing data, private
TV responses, personal account/add-on configuration, or raw device captures in
worker context. Git ignore rules are not a context access-control boundary.
Do not delegate pairing/authentication, security, native installation or firmware
changes, device/network operations, service management, deployment, or final
architecture and patch decisions. Keep the active TV investigation in Codex;
delegate only clearly separate routine source/documentation work.

Workers propose results for Codex to review. Review every patch and suggested
command before applying or running it. Set explicit `allowed_files`,
`forbidden_paths`, and local-only `allowed_commands` for work packets; include
`.private/**`, `.env`, and `.tv_auth` among forbidden paths. If the MCP server or
API key is unavailable, or the result is `needs_codex`, continue directly in Codex.

See `docs/codexsaver.md` for installation, local key setup, and validation.
<!-- CODEXSAVER:END -->
