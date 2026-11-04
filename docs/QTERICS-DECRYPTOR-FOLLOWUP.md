# Qterics implementation and key trial — November 2, 2026

## Outcome

A concrete open-source Qterics UTV extractor implementation was found and reviewed:
[unixtract](https://github.com/theubusu/unixtract), pinned commit
`aadba866ea47ed9506ffe130a8558bb9147ee968`. This advances the format question beyond
the original research's JWT wrapper description. Its21 published, distinct RSA
private keys were tested locally against the supplied MG1352 UTV. **None matched.**
No Home files/plaintext recovered; no TV operations, service changes, native writes,
new dependency installs or upstream binary builds/execution.

Actual unwrapping keys remain missing. Do not repeat this exact21-key trial or
describe source-code availability as successful firmware decryption.
Decrypting an image would not grant its signing key or establish that a modified
image can be installed. Native modification, update verification and recovery
would still require separate evidence.

## Reviewed implementation

[Pinned Qterics source](https://github.com/theubusu/unixtract/blob/aadba866ea47ed9506ffe130a8558bb9147ee968/src/formats/utv_qterics/mod.rs)
defines RSA-OAEP with SHA1 to recover44bytes, split into16-byte AES key,16-byte
associated data and12-byte nonce base. Blocks use AES128-GCM with a16-byte trailing
tag. The nonce begins with the big-endian block index and retains the last8bytes
of the nonce base. This is consistent with the observed102×16-byte size difference
in the supplied firmware. It is a source-defined recipe, not authenticated
plaintext evidence from this owner artifact because no key matched.

The original research's32-byte header interpretation is not used. No code or
evidence supports treating that description as a verified MG1352 framing rule.

The full upstream extractor was not run. Review noted that it uses the JWT's
output filename to construct a write path and does not perform our JWT signature
or whole-plaintext hash checks in the reviewed function. A small local Python
trial was used with fixed output/report paths and no decrypted file output.
No filename, command or URL from the firmware was followed.

## Reproducible local trial

`scripts/check_qterics_keys.py` parses only the explicit UTV_QTERICS collection
from a caller-selected local UKF file. It validates framing arithmetic, tests
source-defined RSA-OAEP, and would authenticate only the first GCM block after a
successful44-byte unwrap. It never exports private keys or content secrets.
Signed metadata verification was completed separately in `inspect_utv.py`.

Results:

- All21 collection entries parsed;21 distinct public-key fingerprints.
- All21 unwrap attempts rejected; no first-block decryption attempted on the
  actual firmware and no content key saved.
- A temporary, locally generated matching RSA/UTV fixture successfully unwrapped
  and authenticated. One-bit GCM tag corruption was rejected. Fixtures removed.
- Input identity stillSHA256
  `5eccf0374f7d89fb8f33ed763338095a7d58ccd202dde95abb198d9f78b1e9a1`.

Reports: `research/reviews/unixtract-key-trial-verified.json` (reproducible trial)
and `unixtract-qterics-review.json` (provenance/source identities). Initial bounded
trial remains in `unixtract-key-trial.json`. Upstream public key collection stays
local in `.private/unixtract/keys.ukf`, SHA256
`9371ed11ffed8ea82fbb9f612036ba1f09e31c6e851da2ea56721013a34b48af`.
Pinned reviewed source/license and identities are retained privately alongside it.
These are published upstream keys, not recovered owner-device credentials.

No match establishes only failure for this collection and recipe. It does not
prove the key is unique per TV, absent elsewhere, hardware-backed, or obtainable
through an unlocked console. Keys added in October cover MG3xx families, not an
established MG1352 family entry.

## Maintainer's acquisition note and its limits

[Maintainer comment in issue5](https://github.com/theubusu/unixtract/issues/5#issuecomment-5142392330)
identifies `id.json` and `idpwe` as needed key-related files, obtained from internal
storage in their example. Their path is under `com.nvt.idtv` on another platform.
That path is **not** verified on this owner's MediaTek TV and was not requested
or guessed through HTTP. No one was contacted or issue/comment posted.

GitHub searches returned this one relevant Qterics/Vizio issue. Its July statement
about available keys predates the October key additions; the actual tested
collection is the current pinned21-key file, not the older3-key issue snapshot.
A forks API lookup was rejected as an unsupported connector endpoint and was not
retried or treated as a completed fork survey.

Seven previously completed archive indexes (outer, ViziOS, firmware OSS and four
SDK archives) were queried for `id.json`, `idpwe`, `x509_pub.bin` and explicit
Qterics/UpdateLogic/UpdateTV component names. Only an unrelated JSON-Schema test
`id.json` was found. No corresponding key/provisioning artifact or named updater
component identified. This is a filename-scope result, not a content-wide proof;
archives were not reinventoried or rebuilt.

## Separate asset-encryption clarification

Further review of manufacturer `unpacker/src/data_flow/crypt_utils.cpp` shows
`PEM_read_PUBKEY`: despite earlier certificate shorthand, `x509_pub.bin` is consumed
as a **PEM public key**. The asset decryptor hashes the exact file bytes and splits
SHA256 into IV/key; AES128-CBC is separate from the Qterics UTV recipe. File-byte
formatting therefore matters. Its verifier hashes the already-computed payload
digest again through EVP_DigestVerify. No matching public-key artifact has been
acquired; the source tests require an externally supplied PUBLIC_KEY_FILE and
skip when absent. Do not substitute the UTV signing certificate or guess keys.

## Next useful work and limits

We need an evidenced owner-relevant native file read/export, matching key material,
or an already-unpacked Home package. Browser-sandbox persistence is not that access.
No current software-only acquisition method is established by this pass.

An internal mainboard assessment could identify whether a read-only acquisition
route exists, but no board part number, UART pins, voltage, enabled shell, eMMC
readout procedure or recovery fixture is known. The owner has no serial adapter.
Owner confirmed relevant mains-electronics experience. Next is an unplugged visual
mainboard assessment only; see [photo scope](MAINBOARD-IDENTIFICATION.md). This is
not authorization for probing, soldering, bootloader changes or writes.
Do not advise a generic TTL
adapter connection or claim that UART guarantees keys.

All progress is saved locally. No TV rollback is needed because the pass made no
TV changes. Checkpoint is code/docs/provenance, not a flash backup/recovery image.
