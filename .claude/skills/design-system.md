---
name: design-system
description: >
  Generic design system conventions for Tailwind CSS projects inspired by shadcn/ui and Basecoat UI.
  Use this skill when styling components, choosing colors, spacing, border radius, shadows, typography,
  dark mode tokens, or defining interaction patterns. Reusable across any project using Tailwind CSS +
  HTMX + Alpine.js. Triggers include design tokens, color palette, spacing, dark mode, component styling,
  UI consistency, visual patterns, shadcn, or Basecoat.
---

# Design System Conventions

Generic, portable design system for Tailwind CSS projects. Inspired by [shadcn/ui](https://ui.shadcn.com/docs/components), [Basecoat UI](https://basecoatui.com/), [Preline](https://preline.co/), [Tailblocks](https://tailblocks.cc/), and [Common Webpage Layouts with TailwindCSS (Grid & Flexbox)](https://gist.github.com/devinschumacher/95ed32c383a8cc91c0e80e5e502b6afa).

Stack: [Tailwind CSS](https://tailwindcss.com/) + [HTMX](https://htmx.org/) + [Alpine.js](https://alpinejs.dev/) + [Idiomorph](https://github.com/bigskysoftware/idiomorph)

---

## Quick Reference

```
NEUTRALS:    Single scale (zinc recommended). Never mix gray/slate/stone.
SEMANTIC:    Emerald (success), Rose (danger), Amber (warning), Blue (info)
RADIUS:      md (interactive) → lg (container) → xl (card/panel) → full (pill/dot)
SHADOWS:     sm (card) → md (floating) → xl (overlay)
SPACING:     4px base grid. Padding: px-4/px-5. Gaps: gap-2/gap-4/gap-6.
BORDERS:     Always 1px. Neutral-200 light / Neutral-800 dark. No exceptions.
TEXT:         xs=12 sm=14 base=16 lg=18 xl=20 2xl=24. Weights: medium/semibold/bold.
Z-INDEX:     10 (dropdown) → 30 (sticky) → 40 (navbar) → 50 (modal/toast)
TRANSITIONS: 100-200ms. ease-out (enter), ease-in (leave).
DARK MODE:   class-based. localStorage. Invert primary button. Surfaces → neutral-950.
```

---

## 1. Color Strategy

### Neutral Scale

Pick ONE neutral and use it everywhere. Recommended: **Zinc**.

| Role              | Light tokens             | Dark tokens              |
|-------------------|--------------------------|--------------------------|
| Page background   | `{neutral}-50`           | `{neutral}-950`          |
| Surface (card)    | `white`                  | `{neutral}-950`          |
| Elevated surface  | `white/80` (translucent) | `{neutral}-950/80`       |
| Primary text      | `{neutral}-900`          | `{neutral}-50` or `100`  |
| Secondary text    | `{neutral}-600`          | `{neutral}-300` or `400` |
| Muted text        | `{neutral}-500`          | `{neutral}-400`          |
| Borders           | `{neutral}-200`          | `{neutral}-800`          |
| Dividers          | `{neutral}-200`          | `{neutral}-800`          |
| Hover bg          | `{neutral}-100`          | `{neutral}-900`          |
| Disabled          | `opacity-50`             | `opacity-50`             |

### Semantic Colors

Each semantic color follows the same pattern:

| Tone      | Color   | Light bg        | Light text      | Light ring      | Dark bg              | Dark text       | Dark ring       |
|-----------|---------|-----------------|-----------------|-----------------|----------------------|-----------------|-----------------|
| Success   | Emerald | `emerald-50`    | `emerald-800`   | `emerald-200`   | `emerald-900/30`     | `emerald-200`   | `emerald-800`   |
| Danger    | Rose    | `rose-50`       | `rose-800`      | `rose-200`      | `rose-900/30`        | `rose-200`      | `rose-800`      |
| Warning   | Amber   | `amber-50`      | `amber-800`     | `amber-200`     | `amber-900/30`       | `amber-200`     | `amber-800`     |
| Info      | Blue    | `blue-50`       | `blue-800`      | `blue-200`      | `blue-900/30`        | `blue-200`      | `blue-800`      |
| Neutral   | Zinc    | `zinc-50`       | `zinc-700`      | `zinc-200`      | `zinc-900`           | `zinc-200`      | `zinc-700`      |

**Pattern**: Dark backgrounds use `{color}-900/30` (30% opacity) for subtlety.

### Status Indicators

| State   | Light           | Dark            |
|---------|-----------------|-----------------|
| OK/Up   | `emerald-500`   | `emerald-400`   |
| Down    | `rose-500`      | `rose-400`      |
| Warning | `amber-500`     | `amber-400`     |

---

## 2. Typography

### Scale

Use system fonts (Tailwind `sans`). No custom fonts unless branding requires it.

| Token      | Size  | Typical use                     |
|------------|-------|---------------------------------|
| `text-xs`  | 12px  | Badges, captions, footnotes     |
| `text-sm`  | 14px  | Body, nav links, buttons, input |
| `text-base`| 16px  | Card titles, modal titles       |
| `text-lg`  | 18px  | Section headings                |
| `text-xl`  | 20px  | Sub-page titles                 |
| `text-2xl` | 24px  | Page titles (h1)                |
| `text-4xl` | 36px  | Hero headings                   |
| `text-6xl` | 60px  | Display / decorative numbers    |

### Weights

| Token          | Weight | Use                         |
|----------------|--------|-----------------------------|
| `font-normal`  | 400    | Long-form body text         |
| `font-medium`  | 500    | Nav, buttons, badges, labels|
| `font-semibold`| 600    | Card/section titles         |
| `font-bold`    | 700    | Page h1, hero, brand        |

### Extras

| Token            | Use                     |
|------------------|--------------------------|
| `tracking-tight` | Headings, brand name     |
| `leading-relaxed`| Body text, descriptions  |
| `font-mono`      | Code blocks, log viewers |

---

## 3. Spacing System

### Base Grid: 4px

All spacing values are multiples of 4px via Tailwind's default scale.

### Container Pattern

```txt
max-w-{size} mx-auto w-full px-4
```

| Container    | Width  | Use                     |
|--------------|--------|--------------------------|
| `max-w-sm`   | 384px  | Auth forms, small dialogs|
| `max-w-md`   | 448px  | Centered error cards     |
| `max-w-lg`   | 512px  | Modals                   |
| `max-w-2xl`  | 672px  | Blog content             |
| `max-w-4xl`  | 896px  | Dashboard content        |
| `max-w-6xl`  | 1152px | Full-width app layouts   |

### Padding Conventions

| Context          | Token   | Value |
|------------------|---------|-------|
| Page horizontal  | `px-4`  | 16px  |
| Card body        | `px-5 py-4` | 20/16px |
| Button sm        | `px-3`  | 12px  |
| Button md        | `px-4`  | 16px  |
| Button lg        | `px-5`  | 20px  |
| Badge            | `px-2 py-0.5` | 8/2px |
| Navbar           | `py-3`  | 12px  |
| Footer           | `py-4`  | 16px  |
| Content area     | `py-6`  | 24px  |

### Gap Conventions

| Token   | Value | Use                              |
|---------|-------|----------------------------------|
| `gap-1` | 4px   | Inline items (nav, icon+text)    |
| `gap-2` | 8px   | Button groups, breadcrumbs       |
| `gap-3` | 12px  | Logo+brand, form fields          |
| `gap-4` | 16px  | Card grid items                  |
| `gap-6` | 24px  | Page sections                    |
| `gap-8` | 32px  | Major layout sections            |

---

## 4. Border Radius

| Token          | Value  | Use                                   |
|----------------|--------|----------------------------------------|
| `rounded-md`   | 6px    | Buttons, inputs, nav links, toggles   |
| `rounded-lg`   | 8px    | Avatars, toasts, log containers       |
| `rounded-xl`   | 12px   | Cards, modals, panels, accordions     |
| `rounded-full` | 9999px | Badges (pill), dots, avatar circles   |

### Decision Tree

```txt
Interactive element? → rounded-md
Inner container?     → rounded-lg
Card / panel?        → rounded-xl
Pill / circle?       → rounded-full
```

---

## 5. Shadows

| Token       | Use                    | Elevation  |
|-------------|------------------------|------------|
| (none)      | Flat elements          | Ground     |
| `shadow-sm` | Cards, panels          | Surface    |
| `shadow-md` | Toasts, floating menus | Floating   |
| `shadow-lg` | Dropdowns, popovers    | Raised     |
| `shadow-xl` | Modals, overlays       | Overlay    |

```txt
Ground → Surface (sm) → Floating (md) → Raised (lg) → Overlay (xl)
```

---

## 6. Borders & Dividers

### Rule: Always 1px, always `{neutral}-200` / `dark:{neutral}-800`.

```html
<!-- Border -->
<div class="border border-zinc-200 dark:border-zinc-800">

<!-- Divider between items -->
<div class="divide-y divide-zinc-200 dark:divide-zinc-800">

<!-- Separator line -->
<hr class="border-zinc-200 dark:border-zinc-800">
```

### Rings (Badges, focus)

```txt
ring-1 ring-inset ring-{color}-200 dark:ring-{color}-700
```

---

## 7. Z-Index Layers

| Layer     | Z-Index | Elements                |
|-----------|---------|--------------------------|
| Base      | auto    | Page content             |
| Dropdown  | `z-10`  | Dropdowns, popovers      |
| Sticky    | `z-30`  | Sticky sidebars          |
| Navbar    | `z-40`  | Fixed/sticky navbar      |
| Overlay   | `z-50`  | Modals, toasts, drawers  |

---

## 8. Transitions & Animations

### CSS Transitions

| Token                  | Duration | Use                        |
|------------------------|----------|----------------------------|
| `transition`           | 150ms    | Buttons, links, toggles    |
| `transition-colors`    | 150ms    | Hover color changes only   |
| `transition-transform` | 150ms    | Rotations, scale           |
| `transition-all`       | 150ms    | Multi-property (use rarely)|

### Alpine.js Transitions

**Enter** (appearing): `ease-out`, 150-200ms
**Leave** (disappearing): `ease-in`, 100-150ms

```txt
Slide up:   translate-y-2 → translate-y-0  (toast, dropdown)
Slide down: -translate-y-1 → translate-y-0 (accordion, panel)
Fade:       opacity-0 → opacity-100
Scale:      scale-95 → scale-100           (modal)
```

### Tailwind Animations

| Class            | Animation                      | Use                                  |
|------------------|--------------------------------|--------------------------------------|
| `animate-spin`   | `spin 1s linear infinite`      | Loading spinners, processing states  |
| `animate-ping`   | `ping 1s cubic-bezier infinite`| Notification dots, live indicators   |
| `animate-pulse`  | `pulse 2s cubic-bezier infinite`| Skeleton loaders, placeholder UI   |
| `animate-bounce` | `bounce 1s infinite`           | Scroll cues, attention arrows        |
| `animate-none`   | `animation: none`              | Remove animation (responsive/state)  |

#### Spinner (loading state)

```html
<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24">
  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
</svg>
```

#### Ping (live indicator dot)

```html
<span class="relative flex h-3 w-3">
  <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
  <span class="relative inline-flex h-3 w-3 rounded-full bg-emerald-500"></span>
</span>
```

#### Pulse (skeleton loader)

```html
<div class="flex animate-pulse space-x-4">
  <div class="h-10 w-10 rounded-full bg-zinc-200 dark:bg-zinc-800"></div>
  <div class="flex-1 space-y-3 py-1">
    <div class="h-2 rounded bg-zinc-200 dark:bg-zinc-800"></div>
    <div class="h-2 w-3/4 rounded bg-zinc-200 dark:bg-zinc-800"></div>
  </div>
</div>
```

#### Bounce (scroll cue)

```html
<svg class="h-6 w-6 animate-bounce text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7-7-7"/>
</svg>
```

#### Custom animation (arbitrary value)

```html
<div class="animate-[wiggle_1s_ease-in-out_infinite]">...</div>
```

```css
@theme {
  --animate-wiggle: wiggle 1s ease-in-out infinite;
  @keyframes wiggle {
    0%, 100% { transform: rotate(-3deg); }
    50% { transform: rotate(3deg); }
  }
}
```

#### Accessibility: Reduced Motion

```html
<svg class="motion-safe:animate-spin">...</svg>
<div class="motion-reduce:animate-none">...</div>
```

---

## 9. Dark Mode

### Implementation

```txt
Method:   Tailwind class-based (darkMode: 'class')
Storage:  localStorage key "theme" → "dark" | "light"
Default:  prefers-color-scheme media query fallback
Toggle:   Alpine.js x-data on <body>, $watch syncs to <html>
```

### Inversion Rules

| Element          | Light → Dark transformation              |
|------------------|------------------------------------------|
| Page bg          | `{neutral}-50` → `{neutral}-950`        |
| Surface bg       | `white` → `{neutral}-950`               |
| Translucent bg   | `white/80` → `{neutral}-950/80`         |
| Primary button   | `{neutral}-900` bg → `{neutral}-50` bg  |
| Semantic bg      | `{color}-50` → `{color}-900/30`         |
| Borders          | `{neutral}-200` → `{neutral}-800`       |
| Primary text     | `{neutral}-900` → `{neutral}-50`        |
| Hover bg         | `{neutral}-100` → `{neutral}-900`       |

---

## 10. Component Conventions

### Button

```txt
Variants:  primary, secondary, ghost, danger
Sizes:     sm (h-9 px-3 text-sm), md (h-10 px-4 text-sm), lg (h-11 px-5 text-base)
Radius:    rounded-md
States:    focus:ring-2 ring-offset-2, disabled:opacity-50 pointer-events-none
Renders:   <a> if href, <button> otherwise
```

### Badge

```txt
Tones:     neutral, success, danger, warning, info
Shape:     rounded-full (pill)
Size:      px-2 py-0.5 text-xs font-medium
Ring:      ring-1 ring-inset
```

### Card

```txt
Shape:     rounded-xl border shadow-sm
Sections:  header (border-b, optional), body, footer (slot, optional)
Padding:   px-5 py-4 per section
```

### Modal

```txt
Shape:     rounded-xl border shadow-xl
Overlay:   {neutral}-950/60
Z-index:   z-50
Close:     Escape key, backdrop click, close button
Container: max-w-lg
Sections:  header (border-b), body, footer (border-t, actions slot)
```

### Toast

```txt
Position:  fixed right-4 top-4 z-50
Duration:  3s auto-dismiss
Delivery:  hx-swap-oob="true" targeting a portal div
Shape:     rounded-lg border shadow-md
Tones:     success, danger, neutral
```

### Accordion

```txt
Container: rounded-xl border, divide-y between items
Toggle:    Alpine x-data with open/close state
Animation: slide-down (enter), fade-out (leave)
Chevron:   rotate-180 on open
```

### StatusDot

```txt
Shape:     rounded-full, h-2.5 w-2.5
Colors:    emerald (ok), rose (down), amber (warning)
```

### Breadcrumb

```txt
Separator: "/" in muted text color
Active:    last item, no link, stronger text color
Size:      text-sm
```

### ThemeToggle

```txt
Icons:     Sun (dark mode visible) / Moon (light mode visible)
Size:      h-9 w-9 button, h-5 w-5 icon
Visibility: dark:block / dark:hidden CSS toggle
```

---

## 11. Layout Patterns

### Page Grid

```bash
┌──────────────────────────────────────┐
│ Navbar (sticky, z-40, backdrop-blur) │
├──────────────────────────────────────┤
│ Content (flex-1, max-w-{size} px-4)  │
│  ┌──────────────────────────────┐    │
│  │  Breadcrumb (optional)       │    │
│  │  Page section (grid gap-6)   │    │
│  │    ┌──────────────────┐      │    │
│  │    │ Card / Content   │      │    │
│  │    └──────────────────┘      │    │
│  └──────────────────────────────┘    │
├──────────────────────────────────────┤
│ Footer (border-t)                    │
└──────────────────────────────────────┘
```

### Navbar

```
sticky top-0 z-40 border-b bg-{surface}/80 backdrop-blur-lg
  └─ max-w-{size} mx-auto px-4
       ├─ Brand (logo/initial + name)
       ├─ Nav links (gap-1, rounded-md hover)
       └─ Actions (theme toggle, user menu)
```

### Body Structure

```html
<body class="flex min-h-screen flex-col bg-{neutral}-50 dark:bg-{neutral}-950">
  <header>Navbar</header>
  <main class="w-full flex-1">Content</main>
  <footer>Footer</footer>
  <div id="modal-portal"></div>
  <div id="toast-portal"></div>
</body>
```

### Common Responsive Layouts

Use **CSS Grid** for page-level layout, **Flexbox** for component-level alignment.

#### One-Column (Header + Content + Footer)

```html
<div class="flex min-h-screen flex-col">
  <header class="bg-blue-500 p-4">Header</header>
  <main class="flex-grow p-4">Content</main>
  <footer class="bg-gray-300 p-4">Footer</footer>
</div>
```

#### Two-Column (Content + Right Sidebar)

```html
<div class="flex min-h-screen flex-col">
  <header class="bg-blue-500 p-4">Header</header>
  <div class="flex flex-grow flex-col md:flex-row">
    <main class="order-2 flex-grow p-4 md:order-1">Content</main>
    <aside class="order-1 w-full bg-gray-200 p-4 md:order-2 md:w-64">Sidebar</aside>
  </div>
  <footer class="bg-gray-300 p-4">Footer</footer>
</div>
```

#### Two-Column (Left Sidebar + Content)

```html
<div class="flex min-h-screen flex-col">
  <header class="bg-blue-500 p-4">Header</header>
  <div class="flex flex-grow flex-row">
    <aside class="hidden w-64 bg-gray-200 p-4 sm:block">Sidebar</aside>
    <main class="flex-grow p-4">Content</main>
  </div>
  <footer class="bg-gray-300 p-4">Footer</footer>
</div>
```

#### Three-Column (Left Sidebar + Content + Right Sidebar)

```html
<div class="grid min-h-screen grid-cols-1 grid-rows-[auto,1fr,auto] md:grid-cols-[200px,1fr] lg:grid-cols-[200px,1fr,200px]">
  <header class="col-span-full bg-blue-500 p-4">Header</header>
  <aside class="hidden bg-gray-200 p-4 md:row-start-2 md:block">Left Sidebar</aside>
  <main class="row-start-2 bg-white p-4 md:col-start-2">Content</main>
  <aside class="hidden bg-gray-200 p-4 lg:row-start-2 lg:block">Right Sidebar</aside>
  <footer class="col-span-full bg-gray-300 p-4">Footer</footer>
</div>
```

#### Dashboard (Collapsible Sidebar)

```css
grid-template-areas:
  'nav header header'
  'nav content sidebar'
  'nav footer footer';
```

Ideal for admin panels. Sidebar collapses on mobile via responsive grid columns.

### Layout Decision Tree

```txt
Single content column?          → Flexbox (flex-col min-h-screen)
Content + sidebar?              → Flexbox (flex-row on md+, stacked on mobile)
Content + 2 sidebars?           → CSS Grid (grid-cols responsive breakpoints)
Dashboard with collapsible nav? → CSS Grid (grid-template-areas)
```

---

## 12. HTMX Interaction Patterns

| Pattern           | Trigger           | Swap                  | Notes                        |
|-------------------|-------------------|-----------------------|------------------------------|
| Polling           | `load, every Ns`  | `morph:innerHTML`     | Stable IDs for morph match   |
| Click refresh     | `click`           | `innerHTML`           | Target specific container    |
| OOB toast         | Server-sent       | `hx-swap-oob="true"` | Target portal div by ID      |
| Infinite scroll   | `revealed`        | `beforeend`           | Append items                 |
| Search            | `keyup changed`   | `innerHTML`           | Debounce with `delay:300ms`  |
| Form submit       | `submit`          | `innerHTML`           | Swap form response area      |

### Morph + Alpine Rule

When using `morph:innerHTML` with Alpine components:

1. Add stable `id` to every Alpine-managed element
2. Skip `Alpine.initTree()` on morph swaps (Idiomorph preserves state)
3. Only call `Alpine.initTree()` on plain `innerHTML` swaps

---

## 13. Alpine.js State Patterns

| Pattern    | x-data               | Behavior                               |
|------------|-----------------------|-----------------------------------------|
| Dark mode  | `{ dark: false }`    | $watch syncs to html class + localStorage |
| Modal      | `{ open: true }`     | Escape/backdrop close, x-effect remove |
| Toast      | `{ show: true }`     | setTimeout auto-dismiss                |
| Accordion  | `{ open: false }`    | Toggle content, cleanup on close       |
| Dropdown   | `{ open: false }`    | Click-away close via @click.outside    |
| Tabs       | `{ tab: 'first' }`  | Show/hide panels, :class binding       |

### SSE Lifecycle Pattern

```
User action  → connect()    → new EventSource(url)
                              → onmessage: update state
                              → onerror: disconnect()
User action  → disconnect() → es.close(), es = null
Page leaving → disconnect() → cleanup before DOM replace
```

---

## 14. Accessibility Conventions

| Pattern            | Implementation                            |
|--------------------|-------------------------------------------|
| Skip navigation    | `<a href="#main" class="sr-only focus:not-sr-only">` |
| Landmark regions   | `<nav>`, `<main>`, `<footer>` with `role` |
| Button labels      | `aria-label` on icon-only buttons         |
| Modal              | `role="dialog" aria-modal="true"`         |
| Expanded state     | `:aria-expanded="open"` via Alpine        |
| Hidden decorative  | `aria-hidden="true"` on icons/dots        |
| Focus ring         | `focus:ring-2 ring-offset-2`              |
| Disabled state     | `disabled:opacity-50 pointer-events-none` |
