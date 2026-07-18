# Cinematic Director Mode Final Fix Report

Date: 2026-07-18

## Outcome

All final-review Important issues and the actionable schema/test Minor issue were fixed on the opt-in cinematic path. Legacy packages remain on the original validation path, and no provider execution, HTTP client, SDK, polling, download, or credential-handling code was added.

## TDD evidence

Tests were added before production changes and run against the prior validator/docs/catalog.

- Validator RED: 70 tests ran with 36 failures covering explicit null, composition types, state objects and handoff, forward/cyclic dependencies, direction variants, aspect-matched prompt sources, and precompile approval gates.
- Documentation RED: 6 tests ran with 20 failing subtests for the missing DAG, handoff, direction-variant, and approval-state contract tokens.
- Catalog RED: 3 tests ran with 1 failure for the missing P7 draft/blocked and blocked/non_executable expectation.
- Self-review RED: the added merge-safe handoff test failed because the first implementation required whole-object equality; GREEN changed the rule so dependent `state_before` must contain every upstream `state_after` field with the same value while allowing additional non-conflicting state.

## Implemented fixes

- Distinguished a missing `project_brief.cinematic_mode` from explicit `null`; only absence preserves legacy behavior.
- Required cinematic `state_before`/`state_after` non-empty objects, upstream-only dependencies, an acyclic dependency graph, and auditable dependency handoff matching.
- Added cinematic prompt/job `approval_status` validation and enforced hard gates before final compilation.
- Kept one canonical prompt record and shared `global_lock_block` per shot while requiring explicit `16:9` and `9:16` `direction_variants`.
- Required each job to reference the direction variant matching its aspect; independent generation rejects copied directions, and the portrait direction must contain `recomposition_9x16.composition`.
- Tightened `composition_16x9`, portrait composition, and `safe_areas` item types.
- Renamed prompt tests to describe catalog-contract assertions rather than executed Skill behavior, and updated P7 consistently.

## Changed files

- `scripts/validate_package.py`
- `tests/test_validate_package.py`
- `tests/test_cinematic_mode_docs.py`
- `tests/test_test_prompts.py`
- `references/cinematic-directing.md`
- `references/continuity-storyboard.md`
- `references/prompt-compiler.md`
- `references/output-contract.md`
- `test-prompts.json`
- `.superpowers/sdd/final-fix-report.md`

## Verification

- `python -m unittest discover -s tests -p "test_validate_package.py" -v` — 73 passed.
- `python -m unittest discover -s tests -p "test_cinematic_mode_docs.py" -v` — 6 passed.
- `python -m unittest discover -s tests -p "test_test_prompts.py" -v` — 3 passed.
- `python -m unittest discover -s tests -v` — 82 passed.
- `python -m json.tool test-prompts.json | Out-Null` — passed.
- `python -m py_compile scripts/validate_package.py tests/test_validate_package.py tests/test_cinematic_mode_docs.py tests/test_test_prompts.py` — passed.
- `git diff --check` — passed.
- `git diff --check a01efb8..HEAD` — run after commit; passed as recorded in the final handoff.
- Static inspection of `scripts/validate_package.py` found no HTTP/SDK/subprocess/provider execution, polling, download, or credential handling.

## Commit

Commit SHA: the commit containing this report (`HEAD`); its exact resolved SHA is reported in the final handoff. A Git commit cannot embed its own content-addressed SHA without changing that SHA.

## Remaining risk

- State handoff validation compares declared machine-readable values; it does not infer semantic equivalence between differently worded values.
- The portrait composition audit uses exact string inclusion, intentionally favoring deterministic validation over semantic inference.
- Canon/global-lock semantic completeness remains a human review responsibility beyond the structural presence and single-record checks.
