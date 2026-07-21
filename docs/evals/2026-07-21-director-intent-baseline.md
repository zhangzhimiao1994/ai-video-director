# Director Intent Baseline

Date: 2026-07-21
Eval mode: dry_run
Skill version: pre-`intent_contract`, pre-`scene_directing_plan`, pre-`series_handoff`

This baseline freezes the failure mode reported by the user: a cinematic request can receive decorative shots, mechanical coverage, and unsupported series claims even when the intended meaning is narrow. No provider API or video generation was run. The current Skill text was inspected directly and did not yet define the new hard contract fields used by P13-P15.

External references considered for future repair, not copied:

- `xhongc/ai_story`: useful workflow pattern of theme/script -> storyboard -> image -> camera movement -> video/export, plus stage retry/rollback and prompt/model management.
- `XiakeMan777/seedance2.0_XYQ_APi`: useful API delivery pattern of task submission, status polling, retry/cancel, model/ratio/duration parameters, and truthful warnings about credits, cookies, and changing internal APIs.

## P13 Raw-Style Baseline

Prompt summary: "Protection means choosing to bear the cost; do not add romance, revenge, chosen-one mythology, or unrelated worldbuilding."

Observed dry-run failure:

The old routing can produce an exciting fantasy short with a ruined city, glowing symbols, a heroic shield moment, and a final skyline. It preserves the mood of sacrifice but does not first lock a non-reversible meaning contract. Several shots exist for scale rather than proof of the voluntary choice and cost, and the prompt layer has no required `intent_refs` tying each active shot back to the user's message.

## P14 Raw-Style Baseline

Prompt summary: "Mother knows the son is lying; the son does not know she knows. Do not use mechanical shot/reverse-shot."

Observed dry-run failure:

The old routing can return a conventional dialogue plan: medium two-shot, mother's close-up, son's close-up, insert of hand, return to two-shot. It may sound cinematic, but it does not force blocking before camera selection, playable subtext actions, or a per-shot reason for why the camera exists. The result risks being a well-described coverage list rather than directed drama.

## Score Table

| Check | P13 | P14 |
|---|---:|---:|
| Locks the user's core message before expansion | 0/1 | N/A |
| Every active shot traces to the message | 0/1 | N/A |
| Rejects unrelated spectacle | 0/1 | N/A |
| Blocks scene before choosing camera | N/A | 0/1 |
| Uses playable actions and power changes | N/A | 0/1 |
| Rejects mechanical coverage | N/A | 0/1 |

## Failure Notes

- P13 needs a first-class `project_brief.intent_contract` with must-show claims, must-not-imply boundaries, and direct-evidence-first metaphor policy.
- P14 needs `scene_directing_plan` before any shot list, then per-shot deltas, `camera_necessity`, and `shot_relation`.
- P15 needs a truthful series boundary: current single-episode output may prepare a draft handoff, but cannot claim persistent cross-episode state without an external series controller.
