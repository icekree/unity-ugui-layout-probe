# Release fixes

## v0.1.1 — final experimental revision

A post-publication review of fixed v0.1.0 commit `6814b63f59e8077cedc0ae1378220cabb479e962` identified three reproducible input/output issues, confirmed locally and covered by regression tests:

- Reject JSON/PNG output symlinks and hard links before writing; check input bytes after the final JSON write. v0.1.0 could overwrite an aliased input while reporting it unchanged.
- Put each analysis in `<output>/<report_id>/` so a smaller report cannot inherit stale images from a larger one. Preserve previous reports and unrelated files.
- Require object/array structure explicitly and reject empty `cases`. Valid `nodes: []` remains supported; `{}` and `""` are structural errors rather than silently accepted empty node lists.

The geometry scope, default analytical results and native Unity parity limitations are unchanged. v0.1.0 history and tag are retained; use v0.1.1 for the corrected input/output behavior. This remains a frozen research snapshot, with no ongoing-development commitment.
