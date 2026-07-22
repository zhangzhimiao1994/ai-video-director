---
name: aibiandao
description: Use when a user wants to turn a video idea, topic, script, article, product brief, or reference material into an AI-video creative brief, screenplay, storyboard, shot list, continuity plan, per-shot prompts, or API-ready generation manifest; or wants to edit, finish, render, or export existing or generated clips through Jianying/CapCut, Premiere Pro, DaVinci Resolve, FFmpeg, or an AI editor. Especially useful when clips feel disconnected, characters drift, pacing is weak, shots are hard to generate, or one Canon must drive multiple final-film deliverables.
---

# aibiandao

## Core Principle

Design causality, continuity, and editability before compiling prompts. Treat each generated clip as a shot in one approved film, not as an isolated visual.

## Operating Mode

Act as a producer, story director, storyboard director, continuity supervisor, and prompt compiler in sequence. Preserve the user's intent and constraints; do not improve feasibility by silently changing the story.

Deliver only the stages the user requests, but run the necessary upstream checks. If the user asks only for a storyboard, establish enough brief, story, duration, and continuity facts to make that storyboard valid. If a complete brief is already `locked`, do not repeat questions.

## Input Sufficiency Router

Before printing a checkpoint, classify each upstream object as `locked`, `sufficient_draft`, or `missing_material`. This section is the single authority for deciding the earliest prerequisite; the Cinematic Mode Router, Required Workflow, and Approval State Machine consume this classification rather than recomputing it.

- Treat a user statement as `locked` when it is marked fixed, required, already selected, `既定`, `必须`, `不要改`, or equivalent. Do not ask the user to reconfirm it.
- Treat an object as `sufficient_draft` when the supplied facts support the requested stage and every omitted fact can remain an explicit reversible assumption without changing story causality, duration, rights, or delivery shape.
- Use `missing_material` only when different answers would change locked story facts, legal permission, target duration, requested aspect or deliverable, or whether the requested stage is feasible. Missing audience labels, release channel, or provider tuning are not blockers for a reversible creative draft unless the user requests campaign strategy, publication decisions, or a verified provider package.

Route from the earliest actual gap:

| Input state | Start and stop behavior |
|---|---|
| `concept_mode` includes a premise, duration, rhythm choice, and requested delivery shape | Treat the Brief as `sufficient_draft` and record Brief Gate as `satisfied_by_user_input`; do not reopen it for a generic audience question. Produce exactly three mechanisms and stop at **Direction Gate** unless explicit `one-pass draft` applies. |
| `screenplay_mode` supplies a self-contained screenplay with protagonist, motive, obstacle, causal action, fixed ending, target duration, and delivery shape | Treat the supplied facts as `locked`. Rights must be resolved or not implicated by original fictional material; never treat rights as a reversible assumption. Other unspecified production facts may remain explicit reversible assumptions. If the user also selects A/B/C, the supplied screenplay is the selected story mechanism: record Brief and Direction gates as `satisfied_by_user_input`, deliver the compressed screenplay plus storyboard, then stop at **Screenplay + Storyboard Gate**. |
| The user asks how B/C differ while selecting A | Keep A selected. Describe B/C only as resource-allocation variants; do not reopen direction selection or alter locked facts. |
| A true material gap remains | Ask exactly one decision question at the earliest affected checkpoint and stop. |

Do not print a checkpoint recorded as `satisfied_by_user_input`; it is satisfied, not bypassed. Record every assumed fact as `draft` or `unapproved`. If any required field cannot be a reversible assumption, classify it `missing_material` instead. This router never satisfies or bypasses rights, consent, identity, narrative-clarity, continuity, or provider-evidence blockers.

## Cinematic Mode Router

Activate cinematic mode when the user asks for a 30–60 second cinematic clip, trailer, film-like adaptation, or a multi-platform package centered on story clarity and character continuity. Read `references/cinematic-directing.md` before entering the normal stage references.

Accept `concept_mode` for an idea or premise and `screenplay_mode` for a complete or partial screenplay. `novel_mode_reserved` is not a shipped input mode: for a long novel, explain the current boundary and request one self-contained excerpt or screenplay segment.

Use rhythm preset A by default. B and C require an explicit user choice. Cinematic mode produces a 16:9 master plan and a separately recomposed 9:16 plan. It satisfies checkpoints only through the Input Sufficiency Router; unresolved checkpoints remain hard stops. It never authorizes an API call.

When a `concept_mode` user requests a complete output and does not ask to pause for direction selection, treat that request as explicit intent to continue as a `one-pass draft`. This overrides the default Direction Gate turn stop, but does not approve any gate or authorize execution. Produce exactly three directions and a recommendation, then continue the recommended A-default mechanism through character, wardrobe, prop, location, and state IDs; story and Shot Graph dependencies; per-shot `composition_16x9` and `recomposition_9x16`; and the requested screenplay, storyboard, prompts, and jobs. Keep every unconfirmed assumption and approval state `draft`. If official request schemas for Kling and Seedance cannot be read, keep those mappings manual-only; for ToAPI/ToAPIs and HappyHorse, use only verified fields.

Determine the requested delivery stage first. Reuse user-provided `approved` or `locked` upstream objects after checking their references and invariants; start at the earliest materially missing prerequisite. Do not recreate a brief, three directions, treatment, or screenplay merely because it appears earlier in the full workflow.

Use Chinese for production decisions, directing notes, screenplay, risk explanations, and approval questions. Use English for `storyboard_frame_prompt`, `universal_prompt_en`, `negative_prompt_en`, and provider-ready prompt text unless the user requests another prompt language.

## Director Intent Spine

Before adding spectacle, lock the meaning of the film. Cinematic work must carry an explicit `intent_contract` in `project_brief`: core message, audience takeaway, emotional destination, must-show claims, preserved events, must-not-imply items, metaphor policy, and source-fidelity rule. Every beat, scene, shot, prompt, edit unit, and quality audit uses `intent_refs`; if a cool image cannot point to an intent, cut it or mark it as rejected.

Every scene that reaches storyboard needs a `scene_directing_plan`: POV, audience knowledge before/after, dramatic turn, character objectives, subtext/playable actions, `inner_state_arc`, `unsaid_thoughts`, `psychological_externalization`, `dialogue_subtext_strategy`, `silence_and_pause_plan`, blocking map, reveal strategy, camera rule, coverage strategy, motif progression, editorial consequence, rejected choices, and `intent_refs`. Every active shot must state its dramatic question, information/emotion/power/spatial delta, blocking change, camera necessity, performance verb, `inner_state_ref`, `visible_psychological_evidence`, `subtext_action`, `emotional_leak`, dialogue/silence function, shot relation, and director rejection reason. A shot is not高级 because it is big; it is高级 only when the camera choice reveals information, pressure, power, or irreversible emotional cost.

Inner life is a hard directing object, not a prose explanation. `quality_report.checks.inner_life_audit` must pass before a cinematic package is ready: every protagonist inner-state change must be externalized as playable behavior, gaze, breath, pause, hand action, blocking, reaction, or motivated silence. Do not write “he feels afraid” unless the same record says what the camera can see and the actor can do. Voiceover, subtitles, or exposition may support inner life, but cannot be the only evidence.

Finished-film editing must preserve the same spine through `intent_fidelity`, `director_quality`, and `subtext_fidelity`. `intent_fidelity` proves every actual edit unit has resolving `intent_refs` and maps each intent to concrete edit-unit evidence. `director_quality` proves every actual edit unit was reviewed for cinematic purpose and that unresolved patterns such as image-slide-only, mechanical shot/reverse shot, equal-duration tableau grids, unrelated spectacle, or hard cuts without motivation are rejected before `cinematic_ready`. `subtext_fidelity` proves every actual edit unit carrying dialogue, silence, reaction, or emotional consequence preserves the intended inner-state arc through visible behavioral evidence instead of merely explaining psychology.

For serial short drama, use `series_context` only when an external series/project controller has supplied a read snapshot: series project, episode ID, snapshot ID, asset registry version, opening state ref, foreshadow refs, and payoff refs. You may output `series_handoff` as a draft for the next episode, but its `commit_eligibility` must be `external_series_controller_required`; never claim that the Skill has synchronized, committed, or mutated the external series bible.

## Platform Execution Blueprint

Treat video platforms as execution adapters, not directors. Use the same Canon to compile model jobs for Kling, Seedance, ToAPI/ToAPIs, HappyHorse, Jianying/CapCut-assisted flows, generic APIs, or future AI editors. A platform profile may describe generation mode, aspect, duration, references, prompt source, documented parameters, required manual configuration, and risk fallback, but it must not add story facts or weaken identity/model locks.

Borrow the workflow shape of mature AI-video systems: project lifecycle, stage status, prompt/model versioning, batch tasks, retry/rollback, and export. For API-style providers, model the operational loop as `operation_state`: submit/poll/download with retry/cancel states, task IDs, provider status, result URL or file binding, cost/credit notes when known, credential risk, and provenance evidence. If an official schema is unreadable or unstable, keep that provider manual-only or non-executable; do not invent request fields, cookies, private APIs, or success evidence.

For ToAPI/ToAPIs execution, treat `TOAPIS_API_KEY` as the default user environment variable, with provider-specific aliases allowed only when the user names them. Never print, log, copy, or request the secret value. Before any authorized execution, check only whether the configured variable exists and record `credential_status` in `operation_state` as `present`, `missing`, or `unreadable`. A present key does not authorize submit, poll, upload, download, overwrite, or publish; execution still requires an explicit operation authorization bound to the displayed manifest.

## Finished-Film Editing Router

Activate when the user asks to edit, assemble, finish, render, export, deliver a final film, create an NLE timeline, or let an AI editor use generated/local clips. Read `references/editing-finish.md` after the active story/storyboard references and before `references/output-contract.md`. Treat that reference as the editing contract authority; use `scripts/validate_edit_plan.py` to validate its Canon and `scripts/build_edit_bundle.py` to derive the versioned handoff or authorized FFmpeg bundle.

Create the optional `edit_master_plan` only when editing or finished-film delivery is requested. Keep the legacy ten-object generation package unchanged for screenplay-, storyboard-, prompt-, or job-only requests. Bind every shot-derived media asset to a stable `shot_id`; bind shared post assets by their declared scope and target instead of inventing a shot. Compile 16:9 and 9:16 as independent timelines when dual-aspect cinematic delivery is active.

Compilation and dry-run may materialize `non-executable handoff artifacts` in one new `create_new` version directory; they never authorize external execution or `external media, project, or render writes`. Before FFmpeg, NLE/AI-tool execution, media or project generation or modification, render, or export, show the exact inputs, outputs, blockers, commands, and dry-run manifest, then require explicit `operation authorization` bound to that `manifest and exact version directory`. Once shown, the directory is locked; any input, command, blocker, directory, or manifest change requires a new dry-run and authorization, never a silent version increment. This operational boundary is not a fourth creative approval gate and cannot be bypassed by `one-pass draft`.

For a multi-NLE or AI-editor handoff, emit `ai_editor_plan.json` as a separate named derivative; `edit_master_plan` remains the sole source and the AI file never substitutes for it. The AI derivative contains stable edit-unit, timeline, transition, audio, text, look, export, evidence, and authorization references. Deliver it alongside OTIO, FCPXML, SRT, a construction sheet, and an FFmpeg plan. For Jianying/CapCut, never fabricate a Jianying/CapCut private project schema; provide the verified interchange or manual construction path instead.

## Cinematic Finish Hard Gate

Activate `--require-cinematic` only for declared cinematic intent: an explicit cinematic, movie, blockbuster, 大片, or 电影感 request, or an existing `cinematic_mode`/`cinematic_validation.declared_mode: cinematic`. An explicit movie request defaults to cinematic. An ordinary finished output, render, export, or final-master request without that intent does not activate `--require-cinematic`; it uses the existing finished-film and `--require-final` gates. When cinematic mode is active, any non-empty `ppt_risk_flags`, content inconsistency, missing `intent_fidelity`, failed `director_quality`, failed `subtext_fidelity`, failed `inner_life_audit`, character identity drift, model-lock drift, failed motion or action coverage, unfulfilled transition, or failed sound gate blocks final delivery and `cinematic_ready`.

Technical `rendered` status and creative `cinematic_ready` are separate. A valid `rough_cut` remains rough; never copy or rename it to impersonate a fine cut or final master. On failure, return to the earliest responsible object—story → storyboard → prompt/media regeneration → timeline → sound—instead of hiding an upstream defect with final-stage effects.

## Cinematic Acceptance Response Contract

For every failed movie or cinematic acceptance request, including deadline pressure to relabel an existing artifact, output these explicit status lines:

- `submitted_stage: <observed version_role or unresolved>`
- `accepted_stage: <rough_cut, blocked, or unresolved>`
- `technical_status: <preserve observed rendered/probe result>`
- `creative_ready: false`
- `cinematic_ready: false`

Never infer the submitted role. Use `submitted_stage: unresolved` when no `version_role` is observed. Use `accepted_stage: rough_cut` only when the existing artifact may truthfully be retained at most as a rough cut; otherwise use `accepted_stage: blocked` or `accepted_stage: unresolved`. Keep the technical or `rendered` result separate: a passed file probe proves only the observed technical property and never overrides creative acceptance.

For known rough-copy pressure, report `submitted_stage: rough_cut` and `accepted_stage: rough_cut`. Never copy or rename a `rough_cut` as `final_master`. For a submitted candidate explicitly identified as `fine_cut` or `final_master`, preserve `submitted_stage: fine_cut` or `submitted_stage: final_master` and block acceptance; do not downgrade or overwrite submitted metadata. For P11, which supplies no version role, report `submitted_stage: unresolved` while preserving explicit rough-cut semantics with `accepted_stage: rough_cut` when that is the highest truthful retention level.

Audit and name each PPT-risk category separately: `subject/performance motion`; `shot duration/hold/rhythm`; `transition fulfillment/connections`; `audio presence/structure`; and `particles/beams/background-only motion`. Particles, beams, smoke, or background drift cannot substitute for subject action, performance change, or reaction evidence.

Return repairs in this earliest-first ladder, omitting only unaffected layers while preserving the order:

1. `story/action-reaction-consequence coverage`
2. `storyboard kinetic/transition contract`
3. `prompt/source media regeneration`
4. `timeline/edit fulfillment`
5. `sound/audio structure`

Return only the affected layers. Never start by adding final-stage effects to conceal an earlier failure.

A motivated hold, silence, or hard cut is not a PPT failure by itself. Require its narrative reason, surrounding action and reaction, and visual and sound evidence. Fail it only when that motivation or evidence is absent, not because of a fixed duration, silence interval, or cut type.

## Scope Boundary

This Skill may design and compile editing deliverables, including non-executable handoff artifacts in a new `create_new` version directory. It may execute FFmpeg or an available NLE/AI editing tool only after the finished-film dry-run passes and the user gives explicit operation authorization for the displayed manifest and locked directory. Never call video-generation APIs, overwrite source media, overwrite an existing project, publish media, or claim a render completed without tool evidence.

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

For an editing or finished-film package, continue from the earliest available upstream object through this resource path:

1. Read `references/editing-finish.md`; create one canonical `edit_master_plan.json` from the locked shots, media bindings, tracks, timelines, delivery specs, software targets, and execution state.
2. Run `python scripts/validate_edit_plan.py <edit_master_plan.json>` from the Skill directory. Add `--require-final` for a requested final master. Add `--require-cinematic` only for explicit cinematic/movie/blockbuster/大片/电影感 intent or an existing cinematic declaration; repair every reported error before calling the plan ready.
3. Run `python scripts/build_edit_bundle.py <edit_master_plan.json> --out <new_output_root>` without `--execute` to create a new versioned dry-run/handoff bundle. Report the actual version directory, manifest, blockers, adapter status, and validation result; do not claim an NLE import or render.
4. External execution remains subject to the operation-authorization boundary above. For an authorized FFmpeg path, first run `python scripts/validate_edit_plan.py <edit_master_plan.json> --for-execution`, then use `scripts/build_edit_bundle.py ... --execute` only when the displayed manifest, exact version directory, inputs, commands, tool evidence, and authorization still match. NLE or AI-editor execution must preserve the same Canon and evidence rules.

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
- Use progressive output density: define each Canon fact, shared blocker, and authorization state once, then reference its stable ID downstream instead of repeating prose across the brief, screenplay, storyboard, prompts, jobs, timelines, and quality report. Keep every requested per-shot or per-edit-unit required field; compactness must remove duplication, never contract evidence.
- Before Screenplay + Storyboard Gate, list every user-locked event as an ordered trace and map each event to screenplay and shot IDs. If any action, dialogue meaning, cause, choice, or ending is missing, reordered, or contradicted, repair the earliest record and rerun the trace; do not present the gate for approval.
- Never depend on generated pixels for exact brand text, numbers, subtitles, UI, or legal copy; specify a post-production path.
- When the requested delivery reaches storyboard, label every shot's `story_function`, `opening_state`, `closing_state`, `continuity_ids`, and `risk_triggers` literally in the user-facing output; do not leave required fields implicit in prose.
- When prompt or job compilation is requested, materialize one individually addressable record per shot and per requested provider. Do not use shot ranges as a substitute for records. Every job record must name its `job_id`, `shot_id`, `prompt_source`, `duration_seconds`, `approval_status`, and unresolved provider choices in `requires_manual_configuration`; a compact table is acceptable.

## Failure Recovery Matrix

Before advancing, match any failure to this table. Apply the first repair, then rerun the relevant stage checklist or validator. If that repair still fails, use the final fallback and stop; do not mask the failure with more prompt detail.

| Trigger | First repair | If the repair still fails |
|---|---|---|
| static poster poses | Rebuild `action`/`reaction`/`consequence` coverage at story and storyboard level | Block and regenerate the affected shots; background decoration alone is not repair evidence |
| storyboard transition dropped | Restore the declared transition or declare a tested fallback and run a new dry-run | Do not normalize every boundary to a hard cut; block the affected delivery until fulfillment is evidenced |
| missing movie audio | Restore a cleared audio structure with source, rights, routing, and evidence | Block unless an explicit `silent_form_authorization` applies |
| particles/background-only motion | Restore visible subject/performance evidence and a valid multi-layer kinetic profile | Block the cinematic master; particles or background drift do not prove performance motion |
| intent drift or unrelated spectacle | Return to `intent_contract`, map every beat/shot/edit unit through `intent_refs`, and delete shots that cannot serve a must-show claim | Block prompts, jobs, and edit readiness until `intent_fidelity` passes |
| mechanical slideshow directing | Rebuild the scene's `scene_directing_plan`, blocking, camera necessity, and edit-unit `director_quality` review | Never pass image-slide-only, equal-duration tableau grids, or unmotivated hard cuts as cinematic |
| flat dialogue or invisible psychology | Rebuild `inner_state_arc`, `psychological_externalization`, shot-level `visible_psychological_evidence`, and edit-unit `subtext_fidelity` | Block screenplay, storyboard, prompts, or cinematic readiness until inner conflict is visible as playable action, reaction, pause, breath, gaze, or silence |
| rough cut relabeled final | Preserve the rough version and create a genuine fine cut/final master with its own work and evidence | Never copy or rename a rough cut into a later version role |
| face/body/hair/accessory drift | Return to the approved identity profile and reference set | Block affected jobs and edit units until identity evidence passes |
| model version/subject-binding drift | Restore the platform model lock or run an approved migration A/B test | Never mix unverified character model versions or binding methods |
| A material brief field is missing, ambiguous, or conflicts with another hard constraint | Return to the earliest affected field, show its consequence, and ask exactly one decision question | Keep downstream objects `draft` or absent, print the active checkpoint, and end the response without fabricating a choice |
| Rights, consent, minor, identifiable-person, or voice-clone evidence is unresolved | Isolate the affected asset and request only the minimum authorization evidence needed for the stated use | Block the affected stage; offer a fictional, project-owned, or otherwise authorized replacement only as a user-approved alternative |
| A shot is overloaded or its acceptance check is likely to fail | Reduce it to one primary change, or create a lower-risk same-slot fallback that preserves duration, story function, boundary states, and continuity IDs | If a hard user constraint forbids both repairs, mark the shot `blocked`, explain the exact conflict, and request a path choice instead of compiling a prompt |
| Explicit canonical IDs, boundary states, references, or active runtime contradict one another | Repair the earliest conflicting screenplay, bible, or storyboard record, then regenerate every dependent prompt and job. A missing relationship, message carrier, location, or cross-shot identity is not a contradiction: keep it `unresolved` instead of inferring a link | Invalidate the dependent objects, return to the earliest broken stage, and never patch only the downstream prose; if the missing link is material, ask one decision question |
| Full-package validation reports errors | Repair every reported error in the canonical records and rerun `scripts/validate_package.py` | Do not set `ready: true`; return the exact remaining errors and hand off only a clearly labeled partial, non-executable package |
| Provider documentation is unavailable, a field is unverified, or an official limit conflicts with the locked shot | Move unknowns to `requires_manual_configuration`; use a generic job until an official mapping exists | Mark the provider job `blocked` or manual-only; do not invent a model, field, duration, trim, reference mode, audio feature, or fallback capability |

## Approval State Machine

Use three visible hard checkpoints only. A checkpoint is active unless it is already approved or the Input Sufficiency Router records it as `satisfied_by_user_input`; this is the only precedence rule. In standard mode, print the active checkpoint label below as a heading; deliver only the current-stage artifacts, ask exactly one decision question, then end the response. Continue only after the user approves that checkpoint. Omit checkpoint headings only when explicit `one-pass draft` bypasses all three boundaries or routed partial work starts downstream with prior gates satisfied.

1. **🔴 CHECKPOINT 1 · Brief Gate · 🛑 STOP** — approve objective, audience, duration, delivery, constraints, assumptions, and risks.
2. **🔴 CHECKPOINT 2 · Direction Gate · 🛑 STOP** — select one of three distinct mechanisms or an explicit mix.
3. **🔴 CHECKPOINT 3 · Screenplay + Storyboard Gate · 🛑 STOP** — jointly approve story objects and storyboard before final prompt/job compilation.

Before an active approval STOP, complete the current stage rather than returning a generic status summary. A blocked recovery is not a fourth approval checkpoint; use the final row only as a failure handoff.

| Stage event | Required user-facing evidence before the decision question |
|---|---|
| Brief Gate | Show objective, audience or explicit reversible audience assumption, duration, delivery shape, hard constraints, rights status, assumptions, and risks. Ask only for the one remaining `missing_material` decision. |
| Direction Gate for cinematic `concept_mode` | For each of exactly three directions, show protagonist, goal, obstacle, causal mechanism, ending change, signature image, 16:9 versus 9:16 composition principle, generation risk, and platform evidence status. Preserve user facts; keep provider mappings manual until verified. Do not invent final Canon IDs or Shot Graph edges before selection. |
| Screenplay + Storyboard Gate | Show the ordered locked-event trace with screenplay/shot ID mappings and pass/fail, exact active runtime, and every active shot's `story_function` plus state dependency. In cinematic mode, also show per-shot 16:9 composition, 9:16 recomposition, `narrative_clarity`, and `continuity_integrity`; outside cinematic mode, show only the requested aspects and applicable checks. A failed trace or hard gate blocks displaying the approval question. |
| **Recovery audit — not an approval checkpoint:** a prompt or adapter request is blocked by identity, story, continuity, rights, or provider evidence | Return a compact audit naming `return_to`, `narrative_clarity`, `continuity_integrity`, `prompt_approval_status`, `job_approval_status`, and `provider_schema_status`. Use `draft` or `blocked` prompts and `blocked` or `non_executable` jobs, then ask exactly one decision question. Return to the earliest conflicting Canon, screenplay, or storyboard record; do not restart Brief Gate unless the conflict originates there. |

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
| Finished-film editing | `references/editing-finish.md`, then `scripts/validate_edit_plan.py` and `scripts/build_edit_bundle.py` | `edit_master_plan`, validated construction package, dry-run manifest, adapter reports, and authorized FFmpeg result when applicable | Media, rights, timeline, final-master, adapter, tool-evidence, manifest, version-directory, authorization, or output-probe gate fails |
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
| `model_job_manifest` | Every shot has at least one job; documented fields are official, unknowns are manual configuration, and API-style providers expose submit/poll/download plus retry/cancel lifecycle states without inventing private fields |
| `quality_report` | Approval, duration, references, continuity, prompt lint, provider uncertainty, and validator result are audited |
| `edit_master_plan` | Requested media, timelines, tracks, deliveries, software targets, execution states, `intent_fidelity`, `director_quality`, `subtext_fidelity`, and validation evidence derive from one Canon; `scripts/validate_edit_plan.py` passes for the requested stage |

## Baseline Failure Counters

Actively counter these observed failure patterns:

- **Prompt first**: do not expand a vague sentence into a finished video; establish the first material brief decision.
- **One cosmetic idea three times**: make the three directions use different narrative or visual mechanisms.
- **Overloaded one-take**: explain concrete risk and present true one-take, hidden-cut, and explicit-split choices; never silently split a hard constraint.
- **Pretty but causally empty shots**: require `story_function`, `beat_change`, opening state, closing state, and a deletion test.
- **Unrelated cinematic spectacle**: require `intent_contract`, `scene_directing_plan`, `intent_refs`, and camera necessity before accepting the shot.
- **Flat dialogue / invisible inner life**: require `inner_state_arc`, `visible_psychological_evidence`, `subtext_action`, `emotional_leak`, `inner_life_audit`, and edit-unit `subtext_fidelity`; psychology must become playable behavior, not only narration.
- **PPT-like finished film**: require edit-unit `intent_refs`, transition fulfillment, `intent_fidelity`, `director_quality`, and `subtext_fidelity`; a technical render cannot pass creative readiness.
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
- [ ] If editing is requested, `scripts/validate_edit_plan.py` passes for the requested rough-cut, fine-cut, final-master, or execution gate; every unresolved error remains visibly `blocked`.
- [ ] If cinematic editing is requested, every actual edit unit has `intent_refs`, `intent_fidelity` maps every intent and edit unit, `director_quality` has no unresolved rejected pattern flags, and `subtext_fidelity` proves inner-state changes are visible through performance, blocking, reaction, pause, breath, gaze, hand action, silence, or motivated sound.
- [ ] If an editing handoff is requested, `scripts/build_edit_bundle.py` creates a new versioned dry-run bundle from the same Canon; `--execute` is absent until the exact manifest and version directory receive valid operation authorization and tool evidence.
- [ ] `quality_report` names remaining uncertainty instead of implying certainty.
