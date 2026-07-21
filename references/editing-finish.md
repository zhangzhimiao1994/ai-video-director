# Finished-Film Editing

Use this reference only when the user requests editing, assembly, an NLE or AI-editor timeline, rendering, export, or finished-film delivery. It is an operational overlay on the active approved story and storyboard references. It does not change their facts, create a fourth creative approval gate, or make editing objects mandatory in the legacy ten-object generation package.

## Activation and Inputs

Create an optional `edit_master_plan` only for an editing or finished-film request. Before compiling it, identify the source package or project, target duration, locked event IDs, requested aspects, media locations or provider results, authorized audio and text assets, delivery specifications, and software targets. Derive requested stages only from `delivery_specs[].version_role`; do not maintain a parallel stage list. Reuse stable upstream IDs and approved story facts; do not rebuild or reinterpret the screenplay or storyboard.

When a generation package exists, `source_package_id` points to its stable ID. For a standalone local edit, use a stable `standalone project ID` in `source_package_id`; do not fabricate a generation package or generation-package fields.

Classify every required input as present, missing, ambiguous, offline, unprobed, or rights-blocked. Compilation may record unresolved items, and dry-run may inspect inputs without modifying them. A material gap must be reported at the earliest affected object: media gaps return to `media_bindings`, timing gaps to the affected timeline or edit unit, and unsupported delivery features to the relevant software target or delivery spec. Never let a later render hide an earlier blocker.

## Canonical edit_master_plan

`edit_master_plan` is the sole edit Canon for every finished-film derivative. It contains `edit_plan_id`, `plan_status`, `source_package_id`, `target_duration_seconds`, `locked_event_ids`, `media_bindings`, `timelines`, `audio_tracks`, `text_tracks`, `look_plan`, `delivery_specs`, `software_targets`, `execution`, and `edit_validation`. Use stable non-empty IDs and one of `draft`, `dry_run_passed`, `authorized`, `rendered`, or `blocked` for `plan_status`; `rendered` requires tool evidence and output probing.

Every construction sheet, Markdown view, CSV, SRT, OTIO, FCPXML, FFmpeg plan, AI-editor JSON, and NLE handoff must be derived from this same object. Do not maintain a second ordering, duration, asset selection, locked event, or cue list in a derivative. When a derivative cannot express a Canon feature, mark the target `blocked` or `manual_or_unverified`; never silently omit, approximate, or downgrade it.

Each requested stage/aspect is one normalized record in `delivery_specs`, selected through `delivery_specs[].version_role`. Every record contains at least `delivery_id`, `version_role` (`rough_cut`, `fine_cut`, or `final_master`), `version_id`, `timeline_id`, `status`, `ready`, `artifact_refs`, `validation_refs`, and `change_summary`, plus the applicable technical export fields: `aspect_ratio`, `resolution`, `frame_rate`, `codec`, `bitrate`, `audio_sample_rate`, `audio_channels`, `filename`, and `destination`. Delivery `status` uses `draft`, `dry_run_passed`, `authorized`, `rendered`, or `blocked`; `ready` is a boolean acceptance result, not a synonym for status. `timeline_id` binds the delivery to its timeline, and that timeline's `export_refs` must point back to the same `delivery_id`.

Every `execution.rendered_outputs` record and every per-delivery result in `edit_validation` references `delivery_id`. Compute aggregate `plan_status` in this order: `blocked` when any requested delivery or shared dependency has an unresolved blocker; otherwise `rendered` only when every requested delivery simultaneously has `status: rendered`, `ready: true`, successful tool evidence, and successful output probe evidence. Partial completion never makes the aggregate `rendered`. Otherwise keep the aggregate `authorized` when operation authorization for the current dry-run manifest and locked version directory is valid and any requested external delivery has an execution step that is pending or running, including when another delivery has completed; otherwise use `dry_run_passed` when all requested deliveries pass dry-run with no active authorization, and `draft` for all earlier states. A failed external operation becomes `blocked`, not stale `authorized`.

## Media Binding

Bind every shot-derived asset to a stable `shot_id`, `asset_id`, and take identity before placing it on a timeline. Every `media_bindings` record requires `asset_id`, `binding_scope`, `target_id`, `source_type`, `path_or_uri`, `file_status`, `rights_status`, `probe_status`, `selection_reason`, and `acceptance_status`. Shot-derived records also require `shot_id`, `take_id`, `runtime_role`, `duration_seconds`, `frame_rate`, `resolution`, `audio_channels`, `source_in_seconds`, `source_out_seconds`, and `fallback_asset_id`; technical fields that do not apply to a scoped post asset may be null or omitted.

The source media and edit units are separate: `media_bindings` own source identity, rights, probe facts, take selection, and legal source bounds; timeline edit units own editorial placement, trims, transitions, continuity handoff, and story purpose. Reusing one source asset across versions or aspects does not merge those edit units, and changing an edit unit never mutates or overwrites the source.

`binding_scope` is one of `shot`, `edit_unit`, `timeline`, or `project`, and `target_id` is required. For `shot`, `target_id` equals the stable `shot_id`; for the other scopes it names the target `edit_unit_id`, `timeline_id`, or stable project ID. Shot clips, provider outputs, and placeholders require `binding_scope: shot` and a non-null `shot_id`. Project- or timeline-wide audio, LUTs, fonts, legal copy, and similar `post_asset` records bind through `binding_scope` and `target_id`; their `shot_id` is null or omitted unless the asset is genuinely shot-derived. Never fabricate a `shot_id` for a shared post asset.

Use `local_file` for local media, `provider_result` for a platform output already linked through its job and shot, `generated_placeholder` for a declared rough-cut placeholder, and `post_asset` for authorized audio, text, graphics, or other post-production media. Prefer exact `shot_id` and `take_id` filename matches for local files and existing job-to-shot references for platform outputs. A fuzzy match is only a suggestion until a person or validated rule confirms it.

Probe bounds and technical properties before accepting a binding. Missing, damaged, too-short, ambiguous, offline, or unauthorized media is blocked at `media_bindings`, before timeline construction for the affected stage. A placeholder must show its `shot_id`, missing reason, and target duration. Placeholders are permitted only in `rough_cut`; they block `fine_cut` and `final_master`. Never stretch or truncate a locked event to conceal missing media.

## Independent 16:9 and 9:16 Timelines

For dual-aspect cinematic delivery, compile one 16:9 timeline and one independently authored 9:16 timeline. They share locked story facts and media identities, but they may use different take selections, cut points, rhythm, reframing, and spatial arrangement. A mechanical center crop of the 16:9 master is not a 9:16 plan. Both timelines preserve locked-event order, dialogue meaning, causality, character identity, and ending.

Each timeline records `timeline_id`, `aspect_ratio`, `resolution`, `frame_rate`, `duration_seconds`, `video_tracks`, `audio_track_refs`, `text_track_refs`, and `export_refs`. Every edit unit records `edit_unit_id`, `sequence`, `shot_id`, `asset_id`, `timeline_in_seconds`, `timeline_out_seconds`, `duration_seconds`, `source_in_seconds`, `source_out_seconds`, `story_function`, `cut_reason`, `transition_in`, `transition_out`, `speed`, `freeze_frames`, `stabilization`, `reframe`, `safe_area`, `scale`, `position`, `opening_state`, `closing_state`, `continuity_ids`, `locked_event_ids`, `audio_cue_ids`, `text_cue_ids`, `look_instruction`, `risk_triggers`, and `approval_status`.

The machine field for event ownership is edit-unit `locked_event_ids`. Flatten it across each timeline in edit-unit sequence; the resulting ordered list must equal the top-level `locked_event_ids` exactly, with no missing, extra, duplicated, or reordered event. Count transition overlap, freeze frames, and speed changes in active duration. Validate legal source bounds, no unintended gaps or overlaps, and exact target duration for each aspect.

## Construction Sheet

Produce a human-executable construction sheet for each timeline, with one row per `edit_unit_id` in timeline order. Each row states the timeline in/out and duration; media path, `shot_id`, take, fallback, and source in/out; exact edit action and `cut_reason`; transition type, duration, visual precondition, and audio bridge; speed, freeze, stabilization, reframe, scale, and position; audio cues and target levels; text cues, timecodes, style, and safe area; look instruction and acceptance target; aspect-specific composition; risks, blockers, checks, and recovery point.

Append the track layout, media inventory and relink map, subtitle table, audio cue sheet, look/color sheet, export matrix, and acceptance checklist. Instructions must name measurable actions and values. Phrases such as “cut faster,” “add cinematic music,” or “apply a consistent grade” are not executable without timing, source, parameter, and acceptance details.

For cinematic delivery, verify `transition_fulfillment` against every actual adjacent edit-unit pair. Each boundary carries its declared type, story reason, visual precondition, audio bridge cue or explicit none, fallback, fulfillment status, and evidence. A supported hard cut may pass when motivated and evidenced; if an adapter drops a storyboard transition, declare and review its fallback and create a new dry-run rather than silently turning every boundary into a hard cut.

## Rough Cut, Fine Cut, and Final Master

Treat `rough_cut`, `fine_cut`, and `final_master` as distinct versioned deliverables, never the same output under three names.

- `rough_cut` proves story order and approximate timing. It may use clearly labeled placeholders and temporary audio, and its validation report lists every unresolved item.
- `fine_cut` uses confirmed takes and formal cut points, transitions, independent aspect recomposition, subtitles, and separated audio tracks. Any placeholder, offline media, or unsupported required effect blocks it.
- `final_master` removes all placeholders and offline media and passes final color, mix, rights, text, encoding, and export checks. It may be called rendered or ready only when the output exists and tool probes match the declaration.

Each layer has its own version record, status, artifact IDs, validation result, and change summary. Failure at a later layer leaves the latest valid earlier layer and construction package intact.

For human-facing review, a rough cut with unresolved creative work may be labeled `creative_ready: false`; this is an explanatory review annotation, not a fabricated field in the validated Canon. Preserve that rough cut and build a genuine fine/final version. Copying or renaming the rough output can never satisfy a later version role.

## Technical Render vs Cinematic Readiness

The optional `cinematic_validation` object is the creative-finish authority for movie/cinematic delivery. Validate it with `--require-cinematic`; its audits cover content consistency, character identity, action/reaction/consequence coverage, kinetic profiles, shot/composition variety, `transition_fulfillment`, `audio_presence_and_structure`, intentional holds, source motion, and `ppt_risk_flags`.

### Plan acceptance

Plan acceptance validates the declared Canon before it is called executable or ready for rendering. It checks timeline structure and duration math; action/reaction/consequence `coverage`; legal source bounds and `cut points`; declared `transitions`, visual preconditions, incoming matches, durations, audio bridges, and fallbacks; cleared `audio` structure and routing; and `prohibited items` such as placeholders in final, unresolved drift, unsupported dependencies, or PPT-risk patterns. Passing this layer proves that the timeline and acceptance targets are coherent. It does not prove that an output file contains the intended action, performance, cut, transition, or sound.

### Actual-film acceptance

Actual-film acceptance starts only after an output exists. Use `ffprobe` for container `streams`, codecs, dimensions, frame rate, channels, and `duration`; use an `FFmpeg or equivalent output probe` to sample boundary windows and verify each declared `cut/frame change`. Build an extracted-frame `contact sheet` and conduct `visual review` against the Canon to confirm `character action`, `performance change`, identity, repeated poses, source motion, composition, and `actual transitions`. Record tool/version, commands or review method, artifact references, and per-check results; never imply that merely planning or rendering performed these checks.

In motion review, `pixel change is not performance`: particles, light beams, and background motion cannot alone pass `source_motion_review`. They may support a shot only when the rendered subject path or performance response is also visible, or when a storyboard-authorized `intentional_hold` has its reason and acceptance evidence confirmed. Motivated hard cuts remain valid when the boundary probe and visual review match the declaration. Designed silence remains valid only through the existing audio/silent-form authorization rules.

If required probing, frame extraction, or visual-review tooling is unavailable, the actual-master result is `blocked` or `manual_review_required`: the plan/delivery remains blocked, while the applicable cinematic audit may carry `manual_review_required`; never claim actual-film acceptance or `cinematic_ready`. Preserve the plan-level result and name the missing evidence instead of fabricating tool output or treating a technical render as creative approval.

`rendered` does not equal cinematic readiness. `rendered` means the requested outputs have the required tool/probe evidence; `cinematic_ready` means every cinematic audit passed with evidence and `ppt_risk_flags` is empty. If cinematic validation fails, aggregate status, delivery readiness, and edit validation remain blocked even when a technical file exists. Static poster posing, subject-less particles/background motion, content mismatch, identity/model-lock drift, or unfulfilled transitions directly fail the cinematic master.

Movie sound is a hard gate. `audio_presence_and_structure` must prove an authorized and structured stream spanning the applicable dialogue, ambience, SFX, music, silence, and routing. Missing audio blocks cinematic readiness unless a specific `silent_form_authorization` exists and all visual audits pass; motivated silence inside an otherwise designed soundtrack is valid.

## Audio, Text, and Look Tracks

`audio_tracks` separately identify dialogue, narration, ambience, sound effects, music, silence, and lip-sync dependencies. Every cue states a stable ID, source and rights status, timeline bounds, channel or bus, target loudness/peak specification, fades or bridges, and acceptance method. Unlicensed music, unapproved voice cloning, or unresolved lip-sync blocks the affected final delivery.

`text_tracks` cover subtitles, titles, CTA, and legal copy with stable cue IDs, exact text, language, timeline in/out, encoding, font and approved fallback, size, position, safe area, and readability check. Do not rewrite legal copy automatically. Generate SRT from these Canon cues rather than maintaining separate timings.

`look_plan` records input and output color spaces, exposure and white-balance corrections, shot matching, style intent, LUT or plugin dependencies, and measurable acceptance checks. Delivery validation also covers resolution, frame rate, codec, bitrate, audio sample rate, and channel layout. A required effect, font, plugin, codec, color transform, or mix operation that the selected path cannot represent must block that target; do not silently degrade it.

## Generic and AI-Editor Delivery

The generic package includes `edit_master_plan.json`, per-aspect construction sheets in Markdown and CSV, per-aspect SRT, relink and rename instructions, FFmpeg dry-run report and command plan, and edit quality reports. Emit OTIO or FCPXML as importable only when the generator implements the relevant public structure and verified fixtures pass; otherwise report `manual_or_unverified` and keep the Canon, construction sheets, and textual handoff. Never create a plausible-looking file with an unsupported exchange extension.

An AI editor consumes strict JSON from `edit_master_plan` and executes dependencies in order: probe, bind, build timelines, apply text, build audio, apply look, export, then validate. Jianying/CapCut, Premiere Pro, DaVinci Resolve, FFmpeg, current NLEs, and future AI editors all consume the same Canon and QC evidence; adapters may expose only verified public formats or a `manual_or_unverified` handoff and must not invent a private schema. Each step records `pending`, `running`, `passed`, `failed`, or `blocked`, including tool/version evidence and artifacts. Compilation produces this AI-ready plan but does not grant execution. A failed AI step returns the earliest repairable Canon object rather than patching only the rendered output.

## Premiere Pro Adapter

The Premiere target receives a verified XML or OTIO exchange only when current import support has evidence, plus video/audio track mapping, proxy strategy, font/LUT/plugin dependencies, relink instructions, and export settings. Record the Premiere version and import/probe result for any actual project operation. If importability or automation is not verified, set the adapter to `manual_or_unverified`, deliver the construction package, and do not claim that a project was imported or created.

## DaVinci Resolve Adapter

The Resolve target receives verified FCPXML or OTIO when supported, track and relink mapping, input/output color-space and grade-node instructions, Fairlight routing, dependencies, and export settings. Record the Resolve version and validation result for actual import, automation, or rendering. If a requested construct cannot be represented or current support is unverified, mark the target `blocked` or `manual_or_unverified` and preserve the generic handoff.

## Jianying / CapCut Adapter

The CapCut official help page <https://www.capcut.com/help/how-to-export-pro-project> reports that direct import of third-party projects is not supported. Therefore `jianying_capcut` always receives the construction sheet, ordered and renamed media list, SRT, track mapping, effect parameters, font/LUT/audio dependencies, and step-by-step assembly instructions.

Unless current official evidence or a verified runtime tool proves project support, the private-project-file status must be `manual_or_unverified`. Do not fabricate Jianying/CapCut private project JSON, reverse engineer a draft format, or label an unverified private file importable. A verified runtime automation tool may operate the application only after dry-run and explicit operation authorization, and its software version and result must be recorded.

## Dry Run and Operation Authorization

Dry-run is the default. Compilation and dry-run may build and validate the Canon, probe declared inputs and available tools read-only, prepare commands, and materialize `non-executable handoff artifacts` into one entirely new `create_new` version directory. Those artifacts are limited to Canon JSON, Markdown/CSV/SRT, verified OTIO/FCPXML, command JSON, adapter reports, and the dry-run manifest. This handoff-bundle write calls no external editing tool and creates or modifies no media, NLE project, or rendered output; compilation and dry-run never authorize `external media, project, or render writes`.

Before materializing the handoff bundle, select the next unused version directory. The dry-run report and manifest show the exact input files and directories, exact intended outputs, selected version directory, blockers and dependencies, complete commands or automation actions, overwrite policy, expected artifacts, and a stable manifest ID. Once that report is shown, the exact directory is locked.

Before FFmpeg, NLE/AI-editor execution, media or project generation or modification, render, or export, require explicit `operation authorization` bound to the displayed `manifest and exact version directory`. Authorization is operational, not a fourth creative approval gate, and `one-pass draft` cannot bypass it. If an input, output, command, blocker, software target, manifest, or version directory changes, or the locked directory conflicts, stop: create a new dry-run and request new authorization. Never silently increment the authorized directory. Never treat creative approval, handoff compilation, or prior authorization for another manifest or directory as execution permission.

## Failure Recovery

Use `create_new` as the version strategy. Source media and existing projects are read-only. Before dry-run materialization, choose a new unused directory such as `edit/v003/`; non-executable handoff artifacts may be written there before operation authorization. After the manifest and report are shown, that directory is immutable for the operation: a conflict requires a new dry-run and new authorization, never automatic renumbering. Only explicit authorization permits external-tool media, project, render, or export writes into the locked directory. Never overwrite source media, an existing project, an earlier edit, or an existing master.

On failure, preserve the `edit_master_plan`, construction sheets, dry-run report, exact command/action log, stdout/stderr or tool report, partial-artifact inventory, validation results, and last successful step in the new version directory. Do not present a partial file as a completed render. Recover from the earliest failing object: repair binding/probe problems in `media_bindings`, timeline problems in the affected edit unit, cue problems in their track, and adapter problems in the adapter. Re-run dry-run after any material repair.

Creative failure follows the same earliest-responsibility rule: story inconsistency returns to story; missing action/reaction/consequence or transition intent returns to storyboard; unusable motion or identity evidence returns to prompt/media regeneration; editorial boundary errors return to timeline; missing or uncleared cues return to sound. Do not treat color, particles, speed ramps, or final effects as substitutes for those repairs.

If an NLE adapter fails, retain the generic FFmpeg/OTIO/SRT/construction path where it is genuinely supported; a proprietary target must never be required for the Canon to remain usable. Stop UI automation when the software version, language, plugin, or selector differs from verified evidence. Preserve valid earlier cut layers and never conceal a failure by renaming one as a later layer.

## Final Acceptance Checklist

A `final_master` is `ready` only when all applicable checks pass with evidence:

- Every locked event appears once, in order, on every requested timeline without changing story meaning or continuity.
- 16:9 and 9:16 are independently composed and each active duration exactly equals its target.
- There are no unintended timeline gaps or overlaps, illegal source bounds, offline or damaged media, or placeholders.
- Transitions, speed changes, reframes, stabilization, and effects match the Canon and are included in duration calculations.
- Subtitles and other text pass content, timing, encoding, font, readability, legal-copy, and safe-area checks.
- Dialogue, narration, ambience, effects, music, silence, and lip-sync have sources, rights, routing, and acceptance results; loudness and peaks meet numeric delivery specifications.
- Color space, exposure, white balance, shot match, and final look pass; no required effect or dependency was silently downgraded.
- Resolution, frame rate, codec, bitrate, sample rate, channel layout, aspect, filenames, and destination match `delivery_specs`.
- Rough cut, fine cut, final master, exchange files, construction sheets, logs, and quality reports have distinct version records.
- Every declared output exists, probes successfully, matches the report, and has tool/version evidence. Without that evidence, status is never `rendered` or `ready`.

## Common Mistakes

- Creating `edit_master_plan` for screenplay-, storyboard-, prompt-, or job-only requests and breaking legacy ten-object compatibility.
- Maintaining hand-edited CSV, SRT, FFmpeg, or NLE timing that diverges from the edit Canon.
- Binding shot-derived media by position or a fuzzy filename without stable `shot_id`, `asset_id`, and take identity.
- Inventing a `shot_id` for project- or timeline-scoped audio, LUT, font, or legal assets instead of using `binding_scope` and `target_id`.
- Treating 9:16 as a center crop of 16:9 or allowing the two versions to change locked story facts.
- Letting a placeholder, offline asset, unauthorized source, or unsupported effect enter `fine_cut` or `final_master`.
- Renaming one timeline as rough, fine, and final without layer-specific work and validation.
- Silently dropping audio, subtitle, color, dependency, or encoding requirements that an adapter cannot express.
- Claiming OTIO, FCPXML, Premiere, Resolve, or Jianying/CapCut import support without current verified evidence.
- Fabricating a Jianying/CapCut private project file.
- Running FFmpeg, making external media/project/render writes, automating an NLE or AI editor, or exporting before the displayed dry-run receives explicit operation authorization.
- Silently changing or incrementing the version directory after showing the dry-run manifest.
- Reusing `one-pass draft` or a creative gate approval as operation authorization.
- Overwriting source media, an existing project, an earlier version, or an existing master instead of using `create_new`.
- Claiming a render completed without an existing, probed output and tool evidence.
