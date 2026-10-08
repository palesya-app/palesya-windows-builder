# Native Windows AI QA: cold-start priority wait

## Observed failure

- Run: `37734139171`, private source `7a51ec6116b99b07350c84ca950c12bd792e4f38`.
- Installer build, installed-app smoke, official license fixture preflight and
  native RTF printing passed.
- Before downloading or chatting with Qwen, the native AI test saw `BUSY` with
  `backup` and `update` owners. Its startup wait allowed only `backup` and failed.
- Installer upload/publication was skipped. No stable feed was promoted.

## Narrow correction

Only the public builder's cold-start wait accepts the two known background
owners, `backup` and `update`, until they finish. The existing 330-second deadline,
one-second polling, final non-BUSY assertion, resource gates, real-Qwen PASS
requirement, read-only checks and native printing checks remain mandatory.
Unknown owners, restores, imports, maintenance and ownerless BUSY still fail.
No private product code, release tag, license validation, runtime resource
guard, customer data or hardware configuration is changed.

## Regression proof

The focused public-workflow contracts reproduced the exact observed
`backup` + `update` failure on builder baseline
`a6fecb71ec95e55f3e71f328689f0e3d612d8fc3`. They also distinguish a real deadline
failure from an immediate allowlist rejection. A guard-removal mutation is
observable; permanent BUSY must fail at the original deadline.

The real installed Windows/Qwen journey must be rerun successfully before the
Windows installer can be uploaded or promoted. These workflow tests do not
claim native or physical acceptance.
