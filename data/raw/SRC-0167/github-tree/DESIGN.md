# Terraform Associate 004 Study Design System

## 0. Research Log
- Embedded refs: shortlisted HashiCorp, Mintlify, and Notion; picked Minimalist + HashiCorp because this is a long-form technical learning product that must retain Terraform identity without copying HashiCorp assets.
- Lazyweb: skipped because no dedicated lazyweb token/browser workflow was available in this session; the official HashiCorp Developer pages were inspected directly instead.
- Imagen drafts: skipped because image generation was unavailable and a documentation shell benefits more from typography and navigation than decorative imagery.

## 1. Atmosphere & Identity
An infrastructure field manual: precise, calm, and dense only when the learner asks for detail. The signature is a dark Terraform-purple masthead transitioning into a warm editorial reading surface, with Korean explanations and English canonical terms kept adjacent.

## 2. Color
| Role | Token | Light | Dark | Usage |
|---|---|---|---|---|
| Canvas | `--sl-color-black` | `#fbfaf8` | `#0d0e12` | Page background |
| Surface | `--sl-color-gray-6` | `#f3f3f5` | `#1d2026` | Secondary panels |
| Text | `--sl-color-white` | `#17191f` | `#f1f1f3` | Primary text |
| Muted | `--sl-color-gray-2` | `#555a65` | `#aeb2bb` | Secondary text |
| Border | `--sl-color-gray-5` | `#e2e3e7` | `#2b2e35` | Structural separation |
| Terraform | `--sl-color-accent` | `#6f3caf` | `#b78be2` | Links, focus, active state |

Accent is interactive or instructional, never decorative. Raw colors belong only in this token table and the corresponding CSS declarations.

## 3. Typography
| Level | Size | Weight | Line height | Usage |
|---|---|---|---|---|
| Display | `clamp(2.5rem, 6vw, 4.5rem)` | 700 | 1.1 | Landing title |
| H1 | Starlight default | 700 | 1.2 | Page title |
| H2 | Starlight default | 700 | 1.3 | Major concept |
| H3 | Starlight default | 650 | 1.4 | Subconcept |
| Body | `1rem` | 400 | 1.68 | Korean and English prose |
| Code | Starlight default | 400 | 1.6 | HCL and CLI |

Primary: Avenir Next, Avenir, Noto Sans KR, system UI. Mono: SFMono-Regular, Consolas, Liberation Mono.

Korean prose uses word-level wrapping (`word-break: keep-all`) with `overflow-wrap` as the long-token fallback, preventing particles and connective endings from being orphaned by syllable-level line breaks.

## 4. Spacing & Layout
Base unit is 4px. Use Starlight spacing tokens for the shell. Reading width is 52rem, sidebar is 19rem, and bilingual comparison blocks collapse from two columns to one at 768px.

## 5. Components
### Learning Card
- Structure: semantic link card with heading, description, and domain identifier.
- States: default, hover, active, 3px focus outline, visited.
- Accessibility: descriptive link text; no icon-only navigation.
- Motion: color and transform only, reduced-motion safe.

### Bilingual Block
- Structure: `.ko-en` grid containing Korean and English `<section>` elements.
- States: static reading surface.
- Accessibility: language headings identify each column; source order is Korean then English.
- Layout: two columns on tablet/desktop and one column on mobile.

### Source Callout
- Structure: Starlight aside followed by named official links.
- States: links expose hover, focus, active, and visited states.
- Accessibility: source purpose appears in link text.

### Navigation Shell
- Structure: Starlight header, local Pagefind search, nested sidebar, table of contents, and footer navigation.
- States: expanded/collapsed groups, mobile drawer, search dialog, focus and active route.
- Accessibility: framework-native keyboard and landmark behavior is preserved.

### Practice Question
- Structure: progress dashboard followed by semantic question cards, selectable answer rows, an answer disclosure, and per-question actions.
- States: unanswered, selected, reviewed, and reset. Single-answer questions behave as radio groups; multiple-answer questions behave as checkbox groups.
- Accessibility: answer rows expose `radio` or `checkbox` roles, `aria-checked`, keyboard activation, and a visible focus ring. Progress uses the native `<progress>` element and a live text summary.
- Progressive enhancement: source Markdown and `<details>` remain readable without JavaScript. The client enhancement never contains or infers the correct answer.
- Motion: selected-state and focus changes use color and transform only; next-question navigation uses native scrolling and respects reduced motion.

## 6. Motion & Interaction
Micro interactions use 100-150ms ease-out. Panel transitions use 200-300ms ease-in-out. Only opacity and transform animate. `prefers-reduced-motion` removes nonessential duration.

## 7. Depth & Surface
Use borders plus whisper shadows. Cards use two 5%-opacity shadow layers; content blocks default to borders. Radius is 4-8px, never oversized pills.

## 8. Accessibility Constraints & Accepted Debt
Target WCAG 2.2 AA, 4.5:1 body contrast, 3:1 large-text contrast, full keyboard reachability, visible focus, semantic landmarks, and reduced-motion support.

| Item | Location | Why accepted | Owner / Exit |
|---|---|---|---|
| Existing archived Markdown contains emoji status markers and uneven heading depth | `src/content/docs/archive/` generated output | Preserving all prior study content without destructive edits takes precedence in this migration | Remove during a later editorial normalization pass |
| English coverage is concise on new core pages while legacy detail remains Korean-first | Archive routes | Full human-quality translation of 59 long documents requires a dedicated editorial pass | Expand per-domain translations using the official source map |
