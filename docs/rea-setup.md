# REA installation and verification

Date: November 1, 2026. Host: Linux Mint 22.3, x86_64.

## Sources and reviewed versions

- Official repository: <https://github.com/morluto/rea>
- Current source inspected: `d3ab0faf52a02ff5a618f3ed7beb608b78752abd`.
- Published npm package installed: `rea-agents@6.8.0`.
- Official installation instructions still specify `npx rea-agents setup`.
  Their automation route supports `--client codex --dry-run --json` and
  applying that reviewed scope with `--yes`.
- Reviewed `docs/installation.md`, `docs/client-configuration.md`,
  `scripts/rea.mjs`, `src/cli/setupCommands.ts`, and configuration document,
  backup, ownership, and publication code under `src/application/`.
- Repository main and the npm release are separate artifacts. The shipped
  package and its own CLI output were used to verify installed behavior.

## Dependencies and installation

The preinstalled desktop Node runtime was 24.21.0, below REA 6.8.0's declared
supported minimum for the 24.x branch. Node/npm were absent from the initial
shell PATH. Installed official Node **24.22.2** with npm **11.19.1** under:

`/home/your-user/.local/lib/nodejs/node-v24.22.2-linux-x64`

The tarball's SHA-256 matched Node's HTTPS `SHASUMS256.txt`:
`48cc0e21e048790e54c0cf5749c2725005313d652651c40b7a21feb9697aaf75`.
User-local aliases are under `/home/your-user/.local/bin`.

The REA tarball matched npm's SHA-512 integrity value. Installed with:

```bash
PATH=/home/your-user/.local/bin:$PATH npm install --global --prefix /home/your-user/.local --ignore-scripts --omit=optional rea-agents@6.8.0
```

Optional Frida and native analysis engines were not installed. Existing
`/usr/bin/ps` is procps-ng 4.0.4, satisfying the Linux process-supervision
prerequisite. No Ghidra was needed for HTTP/JavaScript investigation.

## Configuration and backups

Independent pre-setup backup:

`/home/your-user/.codex/backups/before-rea-20261101T195527Z/config.toml`

REA also created its own backup at:

`/home/your-user/.codex/config.toml.rea.backup`

Applied only Codex's user registration and the bundled personal skill at:

`/home/your-user/.agents/skills/reverse-engineer-anything`

The released setup selected a `rea` executable alias. Its launcher was then
changed to absolute interpreter/script paths so desktop PATH differences
cannot hide Node:

```toml
[mcp_servers.rea]
command = "/home/your-user/.local/lib/nodejs/node-v24.22.2-linux-x64/bin/node"
args = ["/home/your-user/.local/lib/node_modules/rea-agents/scripts/rea.mjs", "mcp"]
startup_timeout_sec = 30
tool_timeout_sec = 450
```

Parsed TOML comparison confirmed all original settings, plugins, project
settings, and the `node_repl` MCP registration were preserved. No persistent
tool-approval overrides were added.

## Verification

- Scoped `rea doctor --client codex --skill --json`: healthy; registration
  and matching workflow skill aligned, including after the absolute-path edit.
- `rea mcp doctor --json`: production stdio initialized, 229 tools and six
  prompts matched, server identity matched, and `binary_session` succeeded.
- An ephemeral Codex CLI test found REA but its first call was rejected by
  that test client's approval policy. A second test allowed only
  `rea.binary_session` through a command-line override; it invoked the tool
  successfully and returned 6.8.0. No global approval policy was changed.
- REA tools subsequently appeared in this original chat. A direct
  `mcp__rea__binary_session({})` invocation succeeded here. Its identity is
  retained in `research/reviews/rea-live-session-identity.json`.
- **No restart is currently required:** actual invocation in this chat was
  verified. Future clients that do not discover the registration may need an
  MCP reconnect/restart, as upstream documents.
- REA statically inspected the three repository-supplied extracted bundles.
  The complete evidence is local in `.private`; its summary records partial
  graph coverage and semantic limits. These bundles were not extracted from
  the owner's TV, and static analysis does not verify their runtime claims.

Native diagnostics added later: Ubuntu's `ffmpeg` 7:6.1.1-3ubuntu5 package was
downloaded from the configured Ubuntu archive and extracted into
`.private/deps/ffmpeg` without a system install. `ffprobe` identified the sample
codecs. An optional baseline/stereo conversion was generated for diagnosis;
the original file played successfully over the LAN, so conversion was not
required for that successful test.
