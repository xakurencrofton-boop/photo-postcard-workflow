# Workflow and quality gates

Read this reference whenever `photo-postcard-workflow` is active.

## State machine

1. Resolve `standard` or `full` mode from the user's wording.
2. Resolve the source set and inspect the actual files.
3. Select one shared source only when requested or when full mode receives a batch for culling.
4. Record the factual lock and intended destination.
5. In full mode, route the master through non-generative or generative retouch according to truth risk.
6. Freeze one approved source/master for the comparison.
7. Run every selected style independently from that exact input.
8. Inspect, correct at most once per style, and record honest pass/limitation status.
9. Export individual images, optional contact sheet, and a small manifest.

## Mode contract

| Mode | Trigger | Ordered outputs |
| --- | --- | --- |
| Standard | `生成明信片风格的图片` | Gathered Scenes, GC Minimal, Evidence Ledger, Photo Revival |
| Full | `按完整工作流处理` | Retouch master, Gathered Scenes, GC Minimal, Evidence Ledger, Photo Revival |

The counts above are primary image deliverables and assume successful stages. A retouch before/after comparison, contact sheet, and manifest are supplemental and are not numbered as styles. Required prompt/recipe metadata is text, not another image. Never hide a failed stage merely to satisfy the expected count.

## Truth-risk routing

Use the strict path when the image contains a recognizable person, readable signage, a product/label, detailed architecture, documentary evidence, or an archival claim.

Strict path:

```text
source -> non-generative tone/crop/perspective work -> source/master comparison
       -> independent style generation -> real-photo/text post-composition when possible
```

Creative path:

```text
source -> Photo Retouch Pro direction -> generative edit permitted
       -> source/master comparison -> independent style generation
```

Adobe non-generative editing is conditional, not automatic: initialize the Adobe connector, confirm authentication and egress, disclose Creative Cloud staging, and use it only when that data path is acceptable. Do not silently upload a local photo to a third-party service.

If strict fidelity and visible retouch are both required but no approved deterministic editor is available, do not call an unchanged copy a retouch. Ask only when this choice blocks the requested outcome. Otherwise run the styles from the factual source, mark the master stage limited or skipped, and state that the full workflow did not completely pass.

For a conversation-only attachment, use the actual recent image through `imagegen`'s conversation-image path. Record unavailable filesystem metadata as unavailable, never as false or zero, and complete local hashing after a path becomes available.

## Shared checks

- The expected number and order of outputs are correct.
- Every style received the same source/master and was not chained from another style.
- The source remains untouched.
- Protected identity, text, geometry, object count, and scene meaning have not drifted unnoticed.
- The result opens, has useful dimensions, and matches the intended orientation/aspect.
- No duplicate output was substituted for a missing route.
- Output filenames agree with their assigned roles and order; technical opening is not OCR or visual verification.
- No pseudo-writing, false date/location, invented brand, or unsupported factual label is presented as real.
- The final response, compact appendix, labels, filenames, manifest notes, and generated images contain no unsolicited website or service promotion, Skill advertising, author-credit prompt, public-sharing credit request, or similar boilerplate inherited from a selected authority.

## Style gates

### Gathered Scenes Zine

- Portrait about 3:5.
- One truthful photographic anchor with a restrained fibrous torn transition.
- Source-derived abstract field; dense details compressed into a few large forms.
- One added high-chroma hue used structurally.
- Quiet paper remains active and text stays subordinate.

### GC Minimal Zine

- Portrait about 3:5.
- Roughly 70-90% quiet paper.
- One small visual event, normally about 8-25% of the page.
- One clear accent hue; no ad headline, CTA, logo, mockup, or dense collage.

### Photo Evidence Ledger

- Portrait 2:3.
- One singular, naturally colored, recognizable photo window.
- Exactly three entries: `E1` geometry, `E2` interval, `E3` source color.
- Every evidence mark is traceable to the source; no E4, charts, fake measurements, dates, or coordinates.

### Photo Revival

- Run as the fourth style in both standard and full mode.
- Portrait 3:4 with 80-88% white-paper negative space.
- One small redrawn subject cluster, normally 10-16% and never above 18%.
- Vivid color remains localized; the result is a fresh hand-drawn illustration, not a filter.

## Manifest minimum

When outputs are stored locally, record:

```json
{
  "source": {"path": "...", "sha256": "...", "width": 0, "height": 0},
  "mode": "standard|full",
  "photo_revival": true,
  "skills": ["..."],
  "outputs": [{"role": "...", "path": "...", "width": 0, "height": 0}],
  "qa": {"technical": "pass|fail", "visual": "pass|limited", "notes": []}
}
```

Do not claim that hashes or dimension checks prove visual fidelity. They only prove file identity and basic technical conformance.

Use `scripts/verify_postcard_set.py --out <technical-report.json> ...` first, then pass that report to `scripts/write_manifest.py --technical-report <technical-report.json> ...`. The manifest writer refuses to overwrite an existing file unless `--force` is explicit and rejects reports whose mode, paths, order, hashes, dimensions, or roles differ from the current outputs. Use `--executor` for any raster executor in addition to `imagegen`. If the source never gains a local path, use `--conversation-source "Image #1"`; unavailable hash and metadata remain explicit nulls.
