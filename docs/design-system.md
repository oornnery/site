# Design System

## Design Direction

The UI follows a dark, developer-focused visual language:

- High-contrast typography
- Neutral surfaces with accent highlights
- Compact cards and rounded controls
- Motion feedback for navigation and section transitions

## Design Foundations

Foundations are split across:

- `app/static/css/tokens.css` (semantic tokens + theme variants)
- `tailwind.config.cjs` (utility palette and type families)
- `app/static/css/style.css` (component and layout styling)
- `app/static/css/motion.css` (animation utilities)

## Component Inventory

Core UI components in `app/templates/ui`, organized by subfolder:

**`ui/form/`**

- `button.jinja` — variants: default, primary, secondary, ghost, link,
  accent, danger, outline
- `input.jinja` — text/textarea, size and variant support; error and hint slots

**`ui/card/`**

- `card.jinja` — variants: default, elevated, outlined, ghost, glass, gradient;
  idle border uses `border-accent/20`, hover `border-accent/40`
- `card/heading.jinja` — title, date, featured badge

**`ui/nav/`**

- `navbar.jinja` — top navigation with theme/palette switcher
  (checkmark on active palette)
- `footer.jinja`, `breadcrumb.jinja`, `pagination.jinja`, `scroll.jinja`,
  `section.jinja`, `social.jinja`

**`ui/layout/`**

- `row.jinja`, `stack.jinja`, `grid.jinja`, `center.jinja`, `section.jinja`

**`ui/content/`**

- `header.jinja`, `meta.jinja`, `shell.jinja`

**`ui/feedback/`**

- `alert.jinja`, `empty.jinja`

**`ui/` root atoms**

- `tag.jinja` — variants: default, outline, accent, secondary, success, warning,
  danger; hover applies `hover:bg-surface-2/80` on all variants
- `avatar.jinja`, `icon.jinja`, `seo.jinja`

## Page Design Patterns

- Home uses full-screen snap sections, guided scroll indicator, and a
  spotlight effect (radial accent glow that tracks the cursor on each section).
- Public pages share a centered container with fixed top navigation.
- Public list/index pages use a shared intro rhythm:
  breadcrumb first, `8px-16px` gap, then title/subtitle.
- Contact page uses two-column layout on medium+ breakpoints.
- Detail pages use a shared header rhythm:
  breadcrumb first, `8px-16px` gap to metadata, `16px-24px` gap to title,
  then subtitle/tags/actions.
- Blog and project detail pages use the same right-side `On this page` minimap
  when rendered markdown includes headings.
- About uses the same minimap shell, but with authored section headings instead
  of markdown-generated headings.
- Project detail uses prose block plus metadata chips/actions.
- About combines a compact profile hero, highlighted timeline cards for
  experience, stacked resume entries for education/certificates, and grouped
  skill chips.

## Motion Principles

From `motion.css`:

- Entrance animations (`fade-up`, `fade-in`, `slide-in-*`, `scale-in`)
- Hover effects (`hover-lift`, `hover-scale`, `hover-glow`)
- Loading states (`pulse`, `bounce`, `spin`)
- Tokenized timing (`--dur-*`) and easing (`--ease-out`)

### Spotlight Effect

The home page snap-sections use a CSS `::before` pseudo-element with a radial
gradient that follows the cursor. JS sets `--spotlight-x`, `--spotlight-y`, and
`--spotlight-opacity` on the active section. The gradient uses
`rgb(var(--accent-rgb) / 0.15)` so it adapts to the active palette. The effect
is disabled when `prefers-reduced-motion` is set.

## Responsive Principles

- Navigation collapses to toggle menu on mobile.
- Home snap behavior adapts by viewport size and height.
- Containers and spacing scale down at mobile breakpoints.

## CSS Methodology

Custom styles are split across three layers that load in order:

- `tokens.css` — semantic design tokens: color channels, spacing, radius,
  and theme/palette variants. This is the single source of truth for all
  design values.
- `motion.css` — animation utilities with a `prefers-reduced-motion` guard
  so all entrance/hover/loading animations are disabled for users who opt out.
- `style.css` — app-specific component and layout rules that build on top of
  the tokens.

Tailwind utilities reference the token variables via `tailwind.config.cjs`;
never hardcode raw color values in templates or style rules.

**Adding a palette**: define a `:root[data-palette="name"]` block in
`tokens.css`. It must appear **after** the `data-theme` blocks in the file so
palette overrides win the cascade correctly.

## Notes on Token Consistency

`tokens.css` is the single source of truth for semantic tokens (`--bg`, `--surface`,
`--accent`, `--border`, `--radius-*`). All colors expose RGB channel variants
(`--accent-rgb`, `--warn-rgb`, `--danger-rgb`, `--accent-2-rgb`) so Tailwind opacity
modifiers (`bg-accent/10`, `border-accent/20`) work correctly. `tailwind.config.cjs`
maps these as `rgb(var(--accent-rgb) / <alpha-value>)` — never use plain `var(--accent)`
for colors that need opacity modifiers.

### Palette system

Six palettes: `default`, `ocean`, `sunset`, `rose`, `forest`, `mono`. Active
palette is stored in `localStorage` and applied as `data-palette` on `<html>`.
Palette overrides in `tokens.css` use `:root[data-palette="..."]` blocks that
must come **after** the `data-theme` block in the cascade.

All visual accent uses (borders, timeline dots, featured badges, minimap dots,
spotlight glow) must reference `--accent-rgb` or `--accent`. Use `--interactive`
only for text link hover colors.

For detailed handoff values, see [Figma Tokens and Handoff](figma-tokens.md).
