# Medical Teaching Assets

Nephrology teaching media (infographics, vector diagrams, and self-contained interactive
HTML lessons) used by the Django-seeded `Lesson` records.

## Layout

| Path | Purpose |
| --- | --- |
| `raw/<chapter>/` | Untouched originals copied from the source folder. Do not edit. |
| `manifest.json` | Authoritative index: chapter, topic, lesson slug, variants, URLs. |
| `../../web/public/medical/<chapter>/` | Optimized, deployable copies served by GitHub Pages. |

`web/public/medical/` is the only folder the app serves. `raw/` is kept for re-export and
for producing future renders without going back to the source machine.

## Naming

- `slug.webp` — full-size image, ported to WebP
- `slug-thumb.webp` — 320 px wide card thumbnail
- `slug-alt.webp`, `slug-v2.webp` — alternate renders of the same slide, kept as spares
- `slug.html` — interactive lesson, no build step, no external JS dependencies

## How lessons reference assets

`Lesson` stores URLs only, never file contents:

- `image_url` / `thumbnail_url` → `https://zub165.github.io/nephro-challenge-ai/medical/<chapter>/<slug>.webp`
- `interactive_url` → `https://zub165.github.io/nephro-challenge-ai/medical/<chapter>/<slug>.html`
- `animation_url` → the step-based JSON animations under `web/public/animations/`

The web app rebases absolute media URLs onto its own base path with
`resolveMedicalAssetUrl()` (`web/src/lib/animationUtils.ts`), so the same URLs work on
GitHub Pages, on a custom domain, and in local development. The mobile app consumes the
same absolute URLs and opens `interactive_url` in the system browser.

Values live in `backend/api/data/chapter_seed.py` behind `MEDICAL_ASSET_BASE`. Adding a
new asset means: drop it into `raw/` and `web/public/medical/`, add the entry to
`manifest.json`, then add or update the `image_url`, `thumbnail_url`, or `interactive_url`
on the lesson in `chapter_seed.py` and reseed.

## Integrity check

`python3 manage.py seed_board_exam` validates that every referenced media URL resolves to a
file in `web/public/medical/` and reports any file that no lesson uses. Alternates and
superseded drafts are expected to be reported as unreferenced; a missing or misspelled
reference is a hard error.

## Current state

- 22 images, 1 vector diagram, 10 interactive lessons across 8 chapters.
- 17 lessons show an infographic, 9 open an interactive lesson.
- Unreferenced on purpose: `gi-causes-acid-base-v1.html` (superseded draft),
  `tumor-lysis-syndrome`, `vasoactive-drugs-potassium` (no matching lesson yet),
  and the `*-alt` / `*-v2` alternate renders.
- `urinary-casts-morphology.webp` is intentionally shared by the urinary-casts lesson and
  the intrinsic-AKI sediment lesson, since the muddy-brown granular casts slide is the
  sediment evidence both lessons describe.

## Adding images later

Originals are PNG, not JPG, and arrive as full-page slide renders. Keep the source in
`raw/`, produce the deployable WebP plus a thumbnail into `web/public/medical/`, and
prefer an explicit `null` lesson mapping in the manifest over attaching a slide to an
unrelated lesson.
