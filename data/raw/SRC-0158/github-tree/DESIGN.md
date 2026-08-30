# AWS Study Design System

## 0. Research Log

- Concrete reference: `content-sources/aws-saa-sutdy-notes/system/{style.css,app.js,study.js}` —
  AWS-orange accent, navy surfaces, quiz controls, study sidebar, three-column reading layout.
- SAA SPA capture: Playwright evidence at `.omo/evidence/start-work/task-1-saa-design-contract/`
  with screenshots at 375/768/1280, getComputedStyle token extractions for home, quiz
  active/selected/feedback, study sidebar/prose/TOC states. All runtime values below are verified.
- Secondary: `content-sources/study-aif-site/src/index.css` — Markdown rhythm, responsive tables.
- Lazyweb/Imagen skipped: plan.md provides a concrete local implementation as the visual contract.

## 1. Atmosphere & Identity

A focused AWS operations notebook: dark navy surfaces, warm orange signals, dense calm information.
The interface feels like a dependable console, not generic marketing. All decorative icons use SVG
icon sets (Lucide preferred); emoji characters are forbidden in production UI.

## 2. Color

| Role | Token | Light | Dark | Usage |
|---|---|---|---|---|
| Canvas | `--bg` | `#f7f8fa` | `#0f1419` | Page background |
| Surface | `--surface` | `#ffffff` | `#161e2d` | Primary panels |
| Surface raised | `--surface-2` | `#f1f4f8` | `#1e2839` | Inputs, navigation |
| Surface strong | `--surface-3` | `#e6ecf2` | `#263148` | Active rows, checked |
| Text | `--text` | `#1a1f2e` | `#e8edf2` | Body and headings |
| Text dim | `--text-dim` | `#4a5566` | `#8fa0b8` | Secondary copy |
| Text muted | `--text-muted` | `#6d7787` | `#7f90a7` | Metadata, labels |
| Border | `--border` | `#e0e5ec` | `#2a374a` | Dividers and controls |
| Border strong | `--border-strong` | `#c4ccd6` | `#3a4a63` | Hover and focus edge |
| Accent | `--accent` | `#d9620b` | `#ff9900` | CTA, links, progress |
| Accent hover | `--accent-hover` | `#b94f05` | `#ffb340` | Hover state |
| Accent soft | `--accent-soft` | `#fff1e5` | `#332719` | Selected bg |
| Success | `--success` | `#15803d` | `#4ade80` | Correct answers |
| Success bg | `--success-bg` | `rgba(22,163,74,.10)` | `rgba(34,197,94,.12)` | Correct option bg |
| Error | `--error` | `#b91c1c` | `#f87171` | Wrong answers |
| Error bg | `--error-bg` | `rgba(220,38,38,.10)` | `rgba(239,68,68,.12)` | Wrong option bg |
| Info | `--info` | `#1d4ed8` | `#60a5fa` | Missed answers |
| Info bg | `--info-bg` | `rgba(37,99,235,.10)` | `rgba(59,130,246,.10)` | Missed option bg |

- Orange reserved for action, focus, progress, selected state.
- Body contrast targets WCAG 2.2 AA; muted text never for required instructions.
- Primary button text: `#1a0f00` dark / `#ffffff` light.

## 3. Typography

| Level | Size | Weight | LH | Tracking | Usage |
|---|---:|---:|---:|---:|---|
| H1 | `26px` | 700 | 1.6 | `-0.01em` | Page title (computed 41.6px LH) |
| Card H2 | `13px` | 600 | 1.4 | `0.06em` | Section label, uppercase |
| Prose H1 | `28px` | 800 | 1.3 | `-0.02em` | Study article title |
| Prose H2 | `20px` | 700 | — | `-0.01em` | Study section, bottom border |
| Prose H3 | `17px` | 600 | — | `0` | Study subsection |
| Prose H4 | `16px` | 600 | — | `0` | Study detail heading |
| Body | `16px` | 400 | 1.6 | `0` | Default (root computed) |
| Prose | `15px` | 400 | 1.8 | `0` | Study content |
| Small | `14px` | 500 | 1.4 | `0` | Buttons, subtitle, controls |
| Stat | `22px` | 700 | 1.0 | `-0.01em` | Metric values, tabular-nums |
| Label | `12px` | 600 | 1.5 | `0.06em` | Category counts, mono |
| Score | `56px` | 800 | 1.0 | `-0.02em` | Results score, tabular-nums |
| Question | `17px` | 400 | 1.75 | `0` | Quiz question text |

- Primary: `-apple-system`, `system-ui`, `Pretendard Variable`, `Noto Sans KR`, sans-serif.
- Mono: `SF Mono`, `ui-monospace`, `Menlo`, monospace — question IDs, category codes, hints.
- `word-break: keep-all` on question and prose text for Korean line breaks.

## 4. Spacing & Layout

Base unit: **4px**. Tokens: `--space-{1..20}` at 4px increments (×1,2,3,4,5,6,8,10,12,16,20).

- Quiz/home: `max-width: 840px` centered, padding `24px 20px`.
- Study: `260px minmax(0,1fr) 220px` grid, `32px` col gap, `max-width: 1400px`.
- ≤1100px: `240px minmax(0,1fr)`, TOC column hidden.
- ≤900px: single-column block; sidebar → fixed 280px drawer with overlay.
- ≤640px: quiz padding `16px 14px`, stats-grid → single column, submit-bar → column-reverse.
- ≤480px: nav-link text hidden, icon only.
- At 375px all content single column, no horizontal overflow.

## 5. Components

### App shell
- Header: title + subtitle (14px/dim), header-actions with nav-link (SVG book icon, 40px height)
  and theme-toggle (SVG sun/moon, 40×40px, surface bg, border, 8px radius).
- Mobile: nav-link text hidden ≤480px. Focus-visible: 2px accent outline offset 2px.

### Button
- Variants: primary (accent bg, box-shadow `0 2px 6px rgba(255,153,0,.25)`), ghost (transparent,
  border), danger-ghost (error text, error-bg hover), btn-sm `6px 12px`/13px, btn-lg `14px 24px`/16px/600w.
- Hover: `translateY(-1px)`. Active: `translateY(0)`. Disabled: `opacity:0.5`. Default: `10px 18px`/14px/500w.

### Stats grid
- 3-column grid, 20px gap. Cell: stat-num (22px/700/accent/tabular-nums), stat-label (12px/dim),
  progress-bar (4px height, accent fill, cubic-bezier transition). Mobile: single column.
- Summary actions: export-wrong (ghost btn-sm), reset-progress (danger-ghost btn-sm).

### Segment controls
- Flex-wrap labels with radio/checkbox inputs. Default: `9px 14px`, surface-2 bg, border, 8px radius.
- Checked: accent bg, dark text, 600 weight. Custom limit: 68px number input inline.

### Category list
- Vertical label rows: checkbox 16×16, cat-num (mono 12px), label (14px), count (mono 12px/dim),
  progress bar 4px. Checked: accent-soft bg. Mobile: bar hidden, grid `22px 32px 1fr auto`.
- Section head: count label + toggle-all ghost btn-sm.

### Start bar
- `position: sticky; bottom: 12px`, gradient fade from `--bg`, full-width primary btn-lg.
- Label: dynamic eligible/session count. Disabled when matched = 0.

### Quiz route flow
- `/[cert]/quiz` opens on the lobby; a question must never render before explicit start or resume.
- Lobby controls persist per user and certification: all/unseen/wrong, random/sequential, question limit,
  and multi-category selection. A resumable active session is a separate primary action.
- The server returns only the current unanswered question. Refresh resumes from persisted queue position;
  answers and explanations remain server-only until submission.
- Export wrong notes produces Markdown from the user's current last-wrong records. Reset requires explicit
  confirmation and clears only the current certification's progress.
- Results include overall and category scores, same-settings restart, and a return-to-lobby action.

### Quiz header
- Grid areas: `back meta / bar bar`. Back: ghost btn. Meta: index `N/M` (600w/tabular-nums).
- Progress bar: 3px height, accent fill, `width 0.35s cubic-bezier(0.22,0.61,0.36,1)`.

### Quiz option
- Grid `auto 30px 1fr auto`: native input, key (15px/700/dim), text (keep-all), hint (10px/mono/hidden mobile).
- Border 2px solid, 8px radius, `13px 16px` padding. States (getComputedStyle-verified):
  - Idle: `--border`, surface bg. Hover: accent border.
  - Selected: accent border, accent-soft bg. Key: accent.
  - Correct: success border (solid), success-bg. Key: success.
  - Wrong: error border (solid), error-bg. Key: error.
  - Missed: info border (**dashed**), info-bg. Key: info.
- Keyboard: A–E / 1–5 toggle; Enter submit/advance; Escape quit with confirm dialog.
- Multiple badge: accent bg, 11px/700, `999px` radius pill.

### Explanation panel
- After submit: fadeIn 250ms ease-out (`translateY(4px)`→0). Surface-2 bg, 12px radius,
  3px left border accent. Answer row: submitted vs correct (mono/700). Body: 15px/1.8.

### Result badge
- Correct: success-bg, success color, SVG checkmark icon. Wrong: error-bg, error color, SVG x icon.
- `12px 18px` padding, 700 weight, 15px, 8px radius, inline-flex with 6px gap.

### Score card (results)
- Center card: score-big (56px/800/accent/tabular-nums, mobile 44px), score-pct (22px/dim).
- Category table: headers `#/카테고리/정답/정답률` (11px/600/uppercase), body 14px, right-aligned numerics.
- Result actions: restart (primary btn-lg) + home (ghost btn-lg). Mobile: column layout.

### Resource curriculum (replaces service map)
- Progressive list of canonical AWS resources: foundation → advanced → applied bands.
- Each resource: title, summary, cert-relevance tags, prerequisite links, official URL.
- Article pages: TOC, prev/next, official links. No cert-specific prose duplication.
- Filterable/searchable index. Graph view: prerequisite and operational-relation edges.

### Study navigation
- Sidebar: 260px sticky full-height, border-right, scrollbar-thin. Inner: home link (13px/500/dim),
  section headings (11px/700/muted/uppercase), links (13px/dim, 8px radius). Collapsible resource
  section with arrow toggle. Active: accent text, accent-soft bg, 600 weight.
- Mobile ≤900px: fixed 280px drawer `translateX(-100%)`→0, overlay `rgba(0,0,0,0.45)`, hamburger.

### Prose
- 15px/1.8/keep-all. H1 28px/800, H2 20px/700 (bottom border), H3 17px/600. Tables: block + overflow-x.
- Code: mono 0.88em, surface-2 bg. Blockquote: accent left 3px, accent-soft bg.
- Mobile ≤900px: prose 14px, h1 22px, h2 18px, pre 12px.

### Breadcrumb & study actions
- Breadcrumb: 13px/muted, `›` separator, current in text color.
- Actions bar: category quiz link (primary btn, SVG icon), PDF download (ghost btn, SVG icon).

### TOC
- Sticky right column, 2px left border, 16px padding-left. Title 11px/700/muted/uppercase.
- Links 12px/dim; H1–H4 mirror the article hierarchy with progressively deeper indentation.
  Hidden ≤1100px.

### Dashboard
- Per-cert detail at `/dashboard/{cert}`: coverage, unseen/wrong/correct, accuracy, category
  breakdown, recent sessions, trend, weak categories, bookmarks. Zero states for all metrics.
- Uses stats-grid and category-table primitives. Cert switcher navigation.

### Certification switcher
- Ordered cert links: code, title, access marker, summary. Active: orange rule, accent-soft bg.

### Form field
- Visible label, input, hint or error. States: default, focus, invalid, disabled, autofill.
- Error announced with `aria-live`. Focus: accent border.

### Admin moderation queue
- `/admin` is an admin-only document-scroll page. Each request row shows display name and a
  wrapping email address, followed by Approve (primary) and Reject (danger-ghost) actions.
- Rows use one bordered surface with dividers rather than independent cards. The queue supports
  loading, empty, mutation-busy, success, and error states; outcomes are announced with `aria-live`.
- At ≤640px each row becomes a single-column stack and its two 44px actions fill the available width.
- Header auth controls are server-seeded: anonymous sees Login; pending sees approval status and
  Logout; reader/admin see Dashboard and Logout; only admin sees the Admin link.

### Pending approval notice
- Pending users opening Dashboard or Quiz receive a centered status panel instead of an API error.
- The panel uses the hourglass status icon, a clear approval-pending heading, explanatory copy, and
  one secondary action back to public study content. It remains a single column at every breakpoint.

## 6. Motion & Interaction

| Type | Duration | Easing | Source |
|---|---:|---|---|
| Press | 100ms | ease | Button transform |
| Hover/focus | 150ms | ease | Border, bg, color |
| Cat row | 100ms | ease | Background |
| Progress | 350–400ms | `cubic-bezier(.22,.61,.36,1)` | Bar fill width |
| Drawer | 250ms | `cubic-bezier(.22,.61,.36,1)` | Sidebar translateX |
| Overlay | 250ms | ease | Overlay opacity |
| Explain | 250ms | ease-out | fadeIn translateY(4px)→0 |
| Theme | 200ms | ease | Body bg + color |

Only `transform`, `opacity`, color/border/background. `prefers-reduced-motion: reduce` suppresses
all transitions/animations to `0.01ms` (SAA source: `* { transition-duration: 0.01ms !important }`).

## 7. Depth & Surface

- Shadow-sm: `0 1px 2px rgba(0,0,0,.3)` dark / `rgba(15,20,25,.05)` light.
- Shadow: `0 2px 4px rgba(0,0,0,.35), 0 8px 24px rgba(0,0,0,.25)` dark /
  `0 1px 3px rgba(15,20,25,.08), 0 6px 18px rgba(15,20,25,.06)` light.
- Primary btn shadow: `0 2px 6px rgba(255,153,0,.25)`.
- Radius: 8px (`--radius-sm`) controls, 12px (`--radius`) cards, 16px (`--radius-lg`) panels, `999px` badge pills.

## 8. Auth & PDF Visibility

| Role | Nav shows | Quiz | Dashboard | Admin |
|---|---|---|---|---|
| Anonymous | Login, register, public study | No affordance | No | No |
| Pending | Status, logout | No affordance | No | No |
| Reader | Study, quiz, dashboard | `/quiz/{cert}` | `/dashboard/{cert}` | No |
| Admin | All + admin | Full | Full | User approval |

- Quiz URL: `/quiz/{cert}` shared workspace; cert switch navigates and remounts via key.
- 9 concept/resource PDFs: public (anonymous OK). 2 root question PDFs: protected (reader/admin;
  401 anonymous, 403 pending). No quiz/dashboard links in anonymous/pending HTML.

## 9. Accessibility Constraints & Accepted Debt

- WCAG 2.2 AA; 4.5:1 text, 3:1 UI. Full keyboard; 2px accent focus ring offset 2px; skip link.
- 44px touch targets; errors use text + SVG icon + color. Theme: system preference default.
- Quiz shortcuts (A–E, 1–5, Enter, Escape) only outside form inputs. `aria-live="polite"` feedback.

| Item | Why accepted | Exit |
|---|---|---|
| Content density testing | Needs production corpus | Before public launch |
| Authenticated Lighthouse | Needs seeded test user | CI storage state before deploy |

## 10. Primitive Showcase Requirement

Before product screens, a standalone showcase page renders every Section 5 component in all
documented states (idle, hover, focus, active, disabled, selected, correct, wrong, missed, loading,
empty, error) at 375/768/1280. This is the Design QA gate: must pass `/visual-qa` reference-fidelity
comparing against SAA evidence captures before product screens proceed.
