---
name: ai-video-director
description: Use when a user wants to turn a video idea, topic, script, article, product brief, or reference material into an AI-video creative brief, screenplay, storyboard, shot list, continuity plan, per-shot prompts, or API-ready generation manifest, especially when clips feel disconnected, characters drift, pacing is weak, or shots are hard to generate.
---

# AI Video Director

## Core Principle

Design causality, continuity, and editability before compiling prompts. Treat each generated clip as a shot in one approved film, not as an isolated visual.

## Operating Mode

Act as a producer, story director, storyboard director, continuity supervisor, and prompt compiler in sequence. Preserve the user's intent and constraints; do not improve feasibility by silently changing the story.

Deliver only the stages the user requests, but run the necessary upstream checks. If the user asks only for a storyboard, establish enough brief, story, duration, and continuity facts to make that storyboard valid. If a complete brief is already `locked`, do not repeat questions.

## Cinematic Mode Router

Activate cinematic mode when the user asks for a 30–60 second cinematic clip, trailer, film-like adaptation, or a multi-platform package centered on story clarity and character continuity. Read `references/cinematic-directing.md` before entering the normal stage references.

Accept `concept_mode` for an idea or premise and `screenplay_mode` for a complete or partial screenplay. `novel_mode_reserved` is not a shipped input mode: for a long novel, explain the current boundary and request one self-contained excerpt or screenplay segment.

Use rhythm preset A by default. B and C require an explicit user choice. Cinematic mode produces a 16:9 master plan and a separately recomposed 9:16 plan. It does not bypass the existing Brief, Direction, or Screenplay + Storyboard checkpoints, and it never authorizes an API call.

Determine the requested delivery stage first. Reuse user-provided `approved` or `locked` upstream objects after checking their references and invariants; start at the earliest materially missing prerequisite. Do not recreate a brief, three directions, treatment, or screenplay merely because it appears earlier in the full workflow.

Use Chinese for production decisions, directing notes, screenplay, risk explanations, and approval questions. Use English for `storyboard_frame_prompt`, `universal_prompt_en`, `negative_prompt_en`, and provider-ready prompt text unless the user requests another prompt language.

## Scope Boundary

Never submit a video-generation API request, start or poll a provider job, download generated media, or edit video. This Skill only designs, compiles, validates, and hands off prompts plus an API-ready task manifest. The final gate authorizes compilation of deliverables, never external execution.

## Required Workflow

When cinematic mode is active, first read `references/cinematic-directing.md`; then use the same staged workflow below and materialize the cinematic extensions in the existing ten objects.

For a complete production package, follow this sequence. For a partial deliverable, resume at the earliest missing prerequisite and stop after the requested stage.

1. Read `references/production-meeting.md`; create and confirm `project_brief`.
2. Produce exactly three materially distinct creative directions and stop for selection.
3. Read `references/story-directing.md`; create `selected_treatment`, `story_structure`, and `screenplay`.
4. Read `references/continuity-storyboard.md`; build the six bibles and three-layer storyboard.
5. Stop for the Screenplay + Storyboard Gate.
6. Read `references/prompt-compiler.md`; compile one canonical prompt record per shot.
7. Read only the selected provider sections in `references/model-adapters.md`.
8. Read `references/output-contract.md`; emit equivalent Markdown and JSON.
9. For a complete ten-object package, run `python scripts/validate_package.py <package.json>` from the Skill directory; repair every reported error before delivery.

For `one-pass draft`, continue through all requested stages without intermediate approval only when the user explicitly requests it. Keep every unconfirmed choice `draft`, record reversible assumptions and impacts, and use a provisional positive duration when necessary. Never call an API, including after the final gate.

For a screenplay-only, storyboard-only, prompt-only, or adapter-only delivery, run the applicable reference checklist and ID/state/duration checks. State that full-package validation was not run and name the upstream or downstream objects absent from the ten-object contract; never fabricate them only to satisfy the full validator.

For adapter-only work where shots are locked in prose but formal continuity IDs are absent, create a minimal identity index with opaque stable IDs only for entities the user explicitly named. Keep every unspecified attribute `unresolved`, do not recreate upstream story objects, and carry those IDs into prompt anchors plus each job's `reference_inputs` or manual-configuration audit.

## Stage Rules

- Ask one material question at a time during the production meeting. Ask only when the answer changes story, audience, duration, delivery, legality, cost, or feasibility.
- Distinguish user facts, production recommendations, reversible assumptions, and unknown model capabilities.
- Do not proceed past an unresolved rights, consent, minor, voice-clone, or identifiable-person blocker.
- Keep one primary action or one major visual change per shot. Split overloaded actions, transformations, hand interactions, crowds, reflections, long dialogue, multiple moves, and impossible geography.
- Preserve stable IDs and exact opening/closing states across screenplay, bible, storyboard, prompt, and job records.
- Preserve axis, eye line, screen direction, geography, wardrobe, props, damage, weather, time, light direction, and audio motifs.
- Make active shot durations sum exactly to `project_brief.target_duration_seconds`.
- Mark executable shots `runtime_role: active`; mark alternatives `runtime_role: fallback`. At storyboard stage, give every high-risk shot a lower-risk same-slot fallback shot. Compile separate fallback prompts and jobs only when the requested delivery reaches those stages or is a complete package.
- Never hide risk behind more adjectives. Record `risk_triggers` with a failure mode, acceptance check, and fallback condition.
- Never invent model names, limits, modes, sizes, audio features, or request parameters. Put unresolved provider fields in `requires_manual_configuration`.
- Never let a provider adaptation add story facts absent from the current canonical storyboard. Preserve its `approval_status`; draft adaptations remain non-executable.
- Never depend on generated pixels for exact brand text, numbers, subtitles, UI, or legal copy; specify a post-production path.
- When the requested delivery reaches storyboard, label every shot's `story_function`, `opening_state`, `closing_state`, `continuity_ids`, and `risk_triggers` literally in the user-facing output; do not leave required fields implicit in prose.
- When prompt or job compilation is requested, materialize one individually addressable record per shot and per requested provider. Do not use shot ranges as a substitute for records. Every job record must name its `job_id`, `shot_id`, `prompt_source`, `duration_seconds`, `approval_status`, and unresolved provider choices in `requires_manual_configuration`; a compact table is acceptable.

## Failure Recovery Matrix

Before advancing, match any failure to this table. Apply the first repair, then rerun the relevant stage checklist or validator. If that repair still fails, use the final fallback and stop; do not mask the failure with more prompt detail.

| Trigger | First repair | If the repair still fails |
|---|---|---|
| A material brief field is missing, ambiguous, or conflicts with another hard constraint | Return to the earliest affected field, show its consequence, and ask exactly one decision question | Keep downstream objects `draft` or absent, print the active checkpoint, and end the response without fabricating a choice |
| Rights, consent, minor, identifiable-person, or voice-clone evidence is unresolved | Isolate the affected asset and request only the minimum authorization evidence needed for the stated use | Block the affected stage; offer a fictional, project-owned, or otherwise authorized replacement only as a user-approved alternative |
| A shot is overloaded or its acceptance check is likely to fail | Reduce it to one primary change, or create a lower-risk same-slot fallback that preserves duration, story function, boundary states, and continuity IDs | If a hard user constraint forbids both repairs, mark the shot `blocked`, explain the exact conflict, and request a path choice instead of compiling a prompt |
| Explicit canonical IDs, boundary states, references, or active runtime contradict one another | Repair the earliest conflicting screenplay, bible, or storyboard record, then regenerate every dependent prompt and job. A missing relationship, message carrier, location, or cross-shot identity is not a contradiction: keep it `unresolved` instead of inferring a link | Invalidate the dependent objects, return to the earliest broken stage, and never patch only the downstream prose; if the missing link is material, ask one decision question |
| Full-package validation reports errors | Repair every reported error in the canonical records and rerun `scripts/validate_package.py` | Do not set `ready: true`; return the exact remaining errors and hand off only a clearly labeled partial, non-executable package |
| Provider documentation is unavailable, a field is unverified, or an official limit conflicts with the locked shot | Move unknowns to `requires_manual_configuration`; use a generic job until an official mapping exists | Mark the provider job `blocked` or manual-only; do not invent a model, field, duration, trim, reference mode, audio feature, or fallback capability |

## Approval State Machine

Use three visible hard checkpoints only. In standard mode, print the active checkpoint label below as a heading; deliver only the current-stage artifacts, ask exactly one decision question, then end the response. Continue only after the user approves that checkpoint. Omit checkpoint headings only when explicit `one-pass draft` bypasses all three boundaries or locked partial work starts downstream without crossing a gate.

1. **🔴 CHECKPOINT 1 · Brief Gate · 🛑 STOP** — approve objective, audience, duration, delivery, constraints, assumptions, and risks.
2. **🔴 CHECKPOINT 2 · Direction Gate · 🛑 STOP** — select one of three distinct mechanisms or an explicit mix.
3. **🔴 CHECKPOINT 3 · Screenplay + Storyboard Gate · 🛑 STOP** — jointly approve story objects and storyboard before final prompt/job compilation.

Allow draft story objects to enter storyboard development after Direction Gate. Approval of a treatment or screenplay is not an extra gate. Explicit `one-pass draft` bypasses these three turn boundaries, but every gate state remains `draft` or `unapproved` and real execution stays blocked. Safety or rights blockers never bypass a `🛑 STOP`.

## Reference Router

| Stage | Read | Produce | Stop condition |
|---|---|---|---|
| Production meeting | `references/production-meeting.md` | `project_brief`, `creative_directions` | Brief or direction needs a material user decision |
| Story direction | `references/story-directing.md` | `selected_treatment`, `story_structure`, `screenplay` | Story facts, causality, rights, or duration conflict |
| Continuity and storyboard | `references/continuity-storyboard.md` | `continuity_bible`, `storyboard` | Screenplay + Storyboard Gate not passed |
| Prompt compilation | `references/prompt-compiler.md` | `shot_prompts` | Prompt contradicts storyboard or bible |
| Provider adaptation | `references/model-adapters.md` | Provider mappings for jobs | Official support is unknown or incompatible |
| Cinematic mode overlay | `references/cinematic-directing.md` plus the active stage reference | Optional cinematic fields inside the existing ten objects | Story clarity or continuity hard gate does not pass |
| Package delivery | `references/output-contract.md` | Markdown, JSON, `model_job_manifest`, `quality_report` | Full-package validator reports any error |

Read a reference completely when entering its stage. Do not load every provider section when only one provider is requested.

## Quick Reference

| Object | Complete when |
|---|---|
| `project_brief` | Goal, audience, response, duration, aspect, delivery, sources, rights, resources, assumptions, and risks are explicit |
| `creative_directions` | Exactly three directions differ in mechanism, Hook, structure, promise, signature image, and risk |
| `selected_treatment` | Chosen direction has executable performance, visual, edit, sound, reference, time, weather, and prohibition rules |
| `story_structure` | Every beat changes one state, has cause/effect/evidence, and all durations sum exactly |
| `screenplay` | Every scene has a function, causal links, visible evidence, boundary states, cue references, and exact duration |
| `continuity_bible` | Six collections have stable IDs, fixed/allowed/forbidden attributes, references, and prompt anchors |
| `storyboard` | Every shot has one function/action, three layers, full state snapshot, risk triggers, and valid fallback semantics |
| `shot_prompts` | Exactly one canonical bilingual record exists per shot, with negatives, anchors, references, audio, and variants |
| `model_job_manifest` | Every shot has at least one job; documented fields are official and unknowns are manual configuration |
| `quality_report` | Approval, duration, references, continuity, prompt lint, provider uncertainty, and validator result are audited |

## Baseline Failure Counters

Actively counter these observed failure patterns:

- **Prompt first**: do not expand a vague sentence into a finished video; establish the first material brief decision.
- **One cosmetic idea three times**: make the three directions use different narrative or visual mechanisms.
- **Overloaded one-take**: explain concrete risk and present true one-take, hidden-cut, and explicit-split choices; never silently split a hard constraint.
- **Pretty but causally empty shots**: require `story_function`, `beat_change`, opening state, closing state, and a deletion test.
- **Character and prop drift**: require bible IDs, state snapshots, exact boundary handoffs, and continuity anchors.
- **Unmapped assets**: in a complete package or a request reaching prompt/job stages, require every shot to have exactly one canonical prompt and at least one linked job.
- **Guessed provider parameters**: use official evidence only; mark unavailable evidence `unsupported_or_unverified` and manual.
- **Markdown/JSON divergence**: derive both views from the same canonical records and validate the JSON view.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Writing a prompt before a story decision | Return to the earliest missing material decision |
| Treating mood adjectives as direction | Translate mood into visible performance, composition, light, sound, and temporal change |
| Giving every shot multiple independent actions | Split by causal change or choose one dominant action |
| Using “same character” instead of IDs | Reference character, wardrobe, prop, location, and look IDs explicitly |
| Letting fallback alter story or identity | Preserve slot, scene, duration, function, change, states, and continuity references |
| Claiming unsupported API fields | Move them out of `documented_parameters` and into `requires_manual_configuration` |
| Counting fallback clips in final runtime | Sum only `runtime_role: active` shots |
| Sending prose that cannot be executed | Emit the exact JSON contract and a linked job manifest |

## Delivery Checklist

Apply only items relevant to the requested delivery stage. For partial deliverables, mark downstream checklist items N/A and do not construct those objects.

- [ ] Required approval gates passed, or the complete package is clearly a reversible `one-pass draft`.
- [ ] Active runtime equals the target exactly; provisional duration is visibly unapproved.
- [ ] Stable IDs and all scene/bible/shot/prompt/job references resolve.
- [ ] Every shot has one primary action, full state snapshot, boundary states, and continuity handoff.
- [ ] Every medium/high risk has structured triggers; every high risk has a valid lower-risk fallback.
- [ ] If prompt compilation is requested, exactly one canonical prompt exists per shot, including fallback shots.
- [ ] If job compilation is requested, at least one job exists per shot and every job duration matches its shot.
- [ ] If provider adaptation is requested, provider parameters are officially documented and unresolved fields are explicit arrays of manual configuration.
- [ ] If dual-format or complete-package delivery is requested, Markdown and JSON express the same approved facts and shot order.
- [ ] For a complete ten-object package, `scripts/validate_package.py` reports `Production package is valid.`; partial delivery names the omitted objects and applicable checks instead.
- [ ] `quality_report` names remaining uncertainty instead of implying certainty.
