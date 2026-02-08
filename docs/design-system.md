# Design System

A comprehensive reference for the UX/UI design language used across all three apps (Portfolio, Blog, Admin). This document serves as a living Figma-style spec — defining every token, component, and interaction pattern extracted from the JX component catalog.

> **Tech stack**: [Tailwind CSS](https://tailwindcss.com/) (CDN) + [HTMX](https://htmx.org/) + [Alpine.js](https://alpinejs.dev/) + [JX](https://jx.scaletti.dev/) + [Idiomorph](https://github.com/bigskysoftware/idiomorph)
>
> **Design references**: [Basecoat UI](https://basecoatui.com/) | [shadcn/ui](https://ui.shadcn.com/docs/components) | [Preline Navbars](https://preline.co/examples/navigations-navbars.html) | [Tailblocks](https://tailblocks.cc/) | [Basic Components](https://github.com/basicmachines-co/basic-components/)

---

## Table of Contents

1. [Color Palette](#1-color-palette)
2. [Typography](#2-typography)
3. [Spacing & Layout](#3-spacing--layout)
4. [Border Radius](#4-border-radius)
5. [Shadows](#5-shadows)
6. [Borders & Dividers](#6-borders--dividers)
7. [Z-Index Layers](#7-z-index-layers)
8. [Transitions & Animations](#8-transitions--animations)
9. [Dark Mode Strategy](#9-dark-mode-strategy)
10. [Component Specifications](#10-component-specifications)
11. [Page Templates](#11-page-templates)
12. [Interaction Patterns](#12-interaction-patterns)
13. [User Flow Diagrams](#13-user-flow-diagrams)

---

## 1. Color Palette

### Primary Scale — Zinc

Zinc is the **sole neutral** used across all surfaces, text, and borders. No gray/slate/stone mixing.

| Token             | Light                   | Dark                     | Usage                           |
|-------------------|-------------------------|--------------------------|----------------------------------|
| `zinc-50`         | `#fafafa`               | —                        | Page background, badge bg        |
| `zinc-100`        | `#f4f4f5`               | —                        | Secondary button bg, hover bg    |
| `zinc-200`        | `#e4e4e7`               | —                        | Borders, ring insets, dividers   |
| `zinc-400`        | `#a1a1aa`               | —                        | Breadcrumb separator, chevrons   |
| `zinc-500`        | `#71717a`               | —                        | Muted text (footer, captions)    |
| `zinc-600`        | `#52525b`               | —                        | Body text, nav links             |
| `zinc-700`        | `#3f3f46`               | —                        | Badge text, breadcrumb active    |
| `zinc-800`        | —                        | `#27272a`               | Dark borders, dark dividers      |
| `zinc-900`        | `#18181b`               | `#18181b`               | Primary text, button bg, dark secondary bg |
| `zinc-950`        | —                        | `#09090b`               | Dark page background, dark card bg |
| `zinc-950/60`     | —                        | `rgba(9,9,11,0.6)`     | Modal overlay                    |
| `zinc-950/80`     | —                        | `rgba(9,9,11,0.8)`     | Dark navbar translucent bg       |
| `white/80`        | `rgba(255,255,255,0.8)` | —                        | Light navbar translucent bg      |

### Semantic Colors

| Semantic   | Light Bg               | Light Text       | Light Ring       | Dark Bg                    | Dark Text          | Dark Ring          |
|------------|------------------------|------------------|------------------|----------------------------|--------------------|--------------------|
| **Success** (emerald) | `emerald-50`   | `emerald-800`    | `emerald-200`    | `emerald-900/30`          | `emerald-200`      | `emerald-800`      |
| **Danger** (rose)     | `rose-50`      | `rose-800`       | `rose-200`       | `rose-900/30`             | `rose-200`         | `rose-800`         |
| **Neutral** (zinc)    | `zinc-50`      | `zinc-700`       | `zinc-200`       | `zinc-900`                | `zinc-200`         | `zinc-700`         |

### Status Indicators

| State    | Light               | Dark                |
|----------|---------------------|---------------------|
| OK       | `emerald-500`       | `emerald-400`       |
| DOWN     | `rose-500`          | `rose-400`          |

---

## 2. Typography

### Font Stack

```text
System default (Tailwind's sans) — no custom fonts loaded.
```

### Scale

| Class              | Size     | Usage                                    |
|--------------------|----------|------------------------------------------|
| `text-xs`          | 12px     | Badges, captions, footer, status codes, timestamps, log viewer |
| `text-sm`          | 14px     | Body text, nav links, buttons (sm/md), card descriptions, toasts |
| `text-base`        | 16px     | Card titles, modal titles, buttons (lg)  |
| `text-lg`          | 18px     | Error page heading                       |
| `text-2xl`         | 24px     | Page titles (h1)                         |
| `text-6xl`         | 60px     | 404 big number                           |

### Weight

| Class              | Weight | Usage                                       |
|--------------------|--------|---------------------------------------------|
| `font-medium`      | 500    | Nav links, buttons, badges, accordion labels |
| `font-semibold`    | 600    | Brand name, card titles, modal titles, page headings (via `font-bold` context) |
| `font-bold`        | 700    | Page h1, brand avatar letter, 404 number    |

### Tracking & Leading

| Class               | Usage                           |
|----------------------|---------------------------------|
| `tracking-tight`    | Brand name, page h1 headings   |
| `leading-relaxed`   | Body text in cards, log viewer  |

### Monospace

| Class         | Usage               |
|---------------|----------------------|
| `font-mono`   | Log viewer `<pre>`  |

---

## 3. Spacing & Layout

### Page Grid

```text
┌──────────────────────────────────────────────────────┐
│ Navbar: full-width, inner max-w-6xl px-4             │
├──────────────────────────────────────────────────────┤
│ Content: max-w-6xl px-4 py-6                         │
│  ┌──────────────────────────────────────────────┐    │
│  │  Breadcrumb (mb-4)                           │    │
│  │  Section (grid gap-6)                        │    │
│  │    ┌──────────────────────────────────────┐  │    │
│  │    │ Card (px-5 py-4)                     │  │    │
│  │    └──────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────┤
│ Footer: full-width, inner max-w-6xl px-4 py-4        │
└──────────────────────────────────────────────────────┘
```

### Container

| Token            | Value     | Usage                                |
|------------------|-----------|--------------------------------------|
| `max-w-6xl`      | 1152px    | All horizontal containers (navbar, content, footer) |
| `max-w-md`       | 448px     | Error page centered card             |
| `max-w-lg`       | 512px     | Modal dialog                         |
| `mx-auto`        | auto      | Center all containers                |
| `w-full`         | 100%      | All containers stretch to full width |

### Padding (Internal)

| Token      | Value | Usage                                          |
|------------|-------|-------------------------------------------------|
| `px-2`     | 8px   | Badge horizontal padding, theme toggle divider  |
| `px-3`     | 12px  | Button sm, nav links                            |
| `px-4`     | 16px  | Page container, modal sections, accordion items, footer, toast |
| `px-5`     | 20px  | Card body and header                            |
| `py-0.5`   | 2px   | Badge vertical padding                          |
| `py-1`     | 4px   | Accordion button inner                          |
| `py-2`     | 8px   | Nav links                                       |
| `py-2.5`   | 10px  | Toast                                           |
| `py-3`     | 12px  | Navbar, accordion items, modal header           |
| `py-4`     | 16px  | Card body/header, footer, modal body/footer     |
| `py-6`     | 24px  | Content area top/bottom                         |
| `p-3`      | 12px  | Log viewer container                            |
| `p-4`      | 16px  | Modal container (safety padding)                |

### Gap (Between Elements)

| Token      | Value | Usage                                          |
|------------|-------|-------------------------------------------------|
| `gap-1`    | 4px   | Nav links list, nav + theme toggle              |
| `gap-2`    | 8px   | Breadcrumb items, button groups, accordion status items, footer gap-y |
| `gap-3`    | 12px  | Brand logo + name, accordion label + dot, modal content spacing |
| `gap-4`    | 16px  | Footer nav links, accordion button sides        |
| `gap-6`    | 24px  | Page sections (`grid gap-6`)                    |

### Vertical Spacing

| Token          | Value | Usage                                 |
|----------------|-------|---------------------------------------|
| `space-y-3`    | 12px  | Modal content stacking                |
| `space-y-4`    | 16px  | Card content stacking                 |
| `mb-2`         | 8px   | Log viewer header                     |
| `mb-4`         | 16px  | Breadcrumb bottom margin              |
| `mb-6`         | 24px  | 404 big number bottom margin          |
| `mt-1`         | 4px   | Card subtitle                         |
| `mt-3`         | 12px  | Accordion expanded log panel          |
| `pt-2`         | 8px   | Error page button group               |

---

## 4. Border Radius

| Token          | Value  | Usage                                       |
|----------------|--------|----------------------------------------------|
| `rounded-full` | 9999px | Badge (pill), StatusDot (circle)             |
| `rounded-xl`   | 12px   | Card, Modal, HealthAccordion container       |
| `rounded-lg`   | 8px    | Brand avatar, logo image, toast, log container |
| `rounded-md`   | 6px    | Button, nav links, accordion hover, log `<pre>`, modal close button, theme toggle |

### Radius Decision Tree

```text
Is it a pill/dot?  → rounded-full
Is it a card/panel? → rounded-xl
Is it a container?  → rounded-lg
Is it interactive?  → rounded-md
```

---

## 5. Shadows

| Token         | Usage                                |
|---------------|---------------------------------------|
| `shadow-sm`   | Card (subtle elevation)              |
| `shadow-md`   | Toast notification                   |
| `shadow-xl`   | Modal dialog (strong elevation)      |

### Shadow Hierarchy

```text
Flat (no shadow)  →  Cards (shadow-sm)  →  Toasts (shadow-md)  →  Modals (shadow-xl)
     ground              surface              floating              overlay
```

---

## 6. Borders & Dividers

### Border Widths

All borders use the default `border` (1px). No `border-2` or thicker is used anywhere.

### Border Colors

| Context          | Light            | Dark             |
|------------------|------------------|------------------|
| Cards            | `zinc-200`       | `zinc-800`       |
| Navbar           | `zinc-200`       | `zinc-800`       |
| Footer           | `zinc-200`       | `zinc-800`       |
| Dividers         | `zinc-200`       | `zinc-800`       |
| Log viewer       | `zinc-200`       | `zinc-800`       |
| Modal            | `zinc-200`       | `zinc-800`       |
| Theme divider    | `zinc-200`       | `zinc-800`       |

> **Rule**: Every border is `zinc-200` (light) / `zinc-800` (dark). No exceptions.

### Divider Pattern

```html
<div class="divide-y divide-zinc-200 dark:divide-zinc-800">
  <!-- items -->
</div>
```

### Ring (Badges only)

```text
ring-1 ring-inset ring-{semantic}-200 dark:ring-{semantic}-700/800
```

---

## 7. Z-Index Layers

| Layer   | Z-Index | Element                  |
|---------|---------|--------------------------|
| Base    | auto    | Page content             |
| Sticky  | `z-40`  | Navbar                   |
| Modal   | `z-50`  | Modal overlay + dialog   |
| Toast   | `z-50`  | Toast notifications      |

```text
z-50  ┌─────────┐ ┌──────┐
      │  Modal  │ │Toast │
z-40  ├─────────┴─┴──────┤
      │      Navbar       │
auto  ├───────────────────┤
      │   Page Content    │
      └───────────────────┘
```

---

## 8. Transitions & Animations

### CSS Transitions

| Token                     | Duration | Usage                             |
|---------------------------|----------|-----------------------------------|
| `transition`              | 150ms    | Buttons, nav links, theme toggle, footer links |
| `transition-transform`    | 150ms    | Accordion chevron rotate          |

### Alpine.js Transitions

#### Toast (enter/leave)

```text
enter:  ease-out 200ms  →  opacity-0 translate-y-2  →  opacity-100 translate-y-0
leave:  ease-in  150ms  →  opacity-100              →  opacity-0 translate-y-2
```

#### Accordion Panel (enter/leave)

```text
enter:  ease-out 150ms  →  opacity-0 -translate-y-1  →  opacity-100 translate-y-0
leave:  ease-in  100ms  →  opacity-100               →  opacity-0
```

#### Modal

```text
backdrop:  x-transition.opacity (default 150ms)
dialog:    x-transition (default scale + opacity, 150ms)
```

### Spinner Animation

```html
<svg class="h-4 w-4 animate-spin">
  <circle class="opacity-25" ... />   <!-- track -->
  <path class="opacity-75" ... />     <!-- arc -->
</svg>
```

### Transform Patterns

| Pattern                          | Usage                     |
|----------------------------------|---------------------------|
| `rotate-180` (conditional)       | Accordion chevron on open |
| `translate-y-2` (enter/leave)    | Toast slide-up            |
| `-translate-y-1` (enter/leave)   | Accordion panel slide-down |

---

## 9. Dark Mode Strategy

### Implementation

```text
Mode:     class-based (Tailwind `darkMode: 'class'`)
Storage:  localStorage key "theme" ("dark" | "light")
Default:  prefers-color-scheme media query fallback
Toggle:   Alpine.js `x-data="{ dark: false }"` on <body>
Sync:     $watch('dark', ...) adds/removes .dark on <html>
```

### Token Mapping

| Element                | Light                        | Dark                           |
|------------------------|------------------------------|--------------------------------|
| Page background        | `bg-zinc-50`                | `bg-zinc-950`                  |
| Card/panel background  | `bg-white`                  | `bg-zinc-950`                  |
| Navbar background      | `bg-white/80`               | `bg-zinc-950/80`               |
| Footer background      | `bg-white`                  | `bg-zinc-950`                  |
| Log viewer bg          | `bg-zinc-50`/`bg-white`     | `bg-zinc-900`/`bg-zinc-950`   |
| Primary text           | `text-zinc-900`             | `text-zinc-50` or `text-zinc-100` |
| Secondary text         | `text-zinc-600`             | `text-zinc-300` or `text-zinc-400` |
| Muted text             | `text-zinc-500`             | `text-zinc-400`                |
| Borders                | `border-zinc-200`           | `border-zinc-800`              |
| Primary button bg      | `bg-zinc-900`               | `bg-zinc-50`                   |
| Primary button text    | `text-white`                | `text-zinc-900`                |
| Secondary button bg    | `bg-zinc-100`               | `bg-zinc-900`                  |
| Hover backgrounds      | `hover:bg-zinc-100`         | `dark:hover:bg-zinc-900`       |
| Brand avatar bg        | `bg-zinc-900`               | `bg-zinc-100`                  |
| Brand avatar text      | `text-white`                | `text-zinc-900`                |
| Semantic bg (success)  | `bg-emerald-50`             | `bg-emerald-900/30`            |
| Semantic bg (danger)   | `bg-rose-50`                | `bg-rose-900/30`               |

> **Pattern**: In dark mode, primary button inverts (dark bg -> light bg). Semantic colors use `900/30` opacity for subtlety. Surfaces go from `white` to `zinc-950`.

---

## 10. Component Specifications

### Layout

| Component       | File                           | Props                                    |
|-----------------|--------------------------------|------------------------------------------|
| **Layout**      | `layouts/Layout.jinja`         | `title`, `lang`, `description`, `navbar_links`, `brand`, `breadcrumb` |
| **Navbar**      | `layouts/Navbar.jinja`         | `brand`, `img`, `links`                  |
| **Content**     | `layouts/Content.jinja`        | (none, slot only)                        |
| **Footer**      | `layouts/Footer.jinja`         | `brand`, `links`                         |

### UI Primitives

#### Button

```text
File:     ui/Button.jinja
Props:    variant, size, href, type
Renders:  <a> if href, <button> otherwise
```

| Variant     | Light                                    | Dark                                    |
|-------------|------------------------------------------|-----------------------------------------|
| `primary`   | zinc-900 bg, white text                  | zinc-50 bg, zinc-900 text               |
| `secondary` | zinc-100 bg, zinc-900 text               | zinc-900 bg, zinc-100 text              |
| `ghost`     | transparent bg, zinc-700 text            | transparent bg, zinc-200 text           |
| `danger`    | rose-600 bg, white text                  | rose-500 bg, white text                 |

| Size | Height | Padding | Font   |
|------|--------|---------|--------|
| `sm` | h-9    | px-3    | text-sm |
| `md` | h-10   | px-4    | text-sm |
| `lg` | h-11   | px-5    | text-base |

States: `focus:ring-2 ring-slate-400 ring-offset-2` | `disabled:opacity-50 pointer-events-none`

#### Badge

```text
File:     ui/Badge.jinja
Props:    tone ("neutral" | "success" | "danger")
Shape:    rounded-full (pill)
Ring:     ring-1 ring-inset
Size:     px-2 py-0.5 text-xs font-medium
```

#### Card

```text
File:     ui/Card.jinja
Props:    title, subtitle
Slots:    content (body), footer
Shape:    rounded-xl
Border:   zinc-200 / dark:zinc-800
Shadow:   shadow-sm
Padding:  header px-5 py-4, body px-5 py-4
```

```text
┌─────────────────────────────────────┐
│ Header: title + subtitle  (px-5 py-4)│  ← border-b (only if title/subtitle)
├─────────────────────────────────────┤
│ Body: {{ content }}       (px-5 py-4)│
├─────────────────────────────────────┤
│ Footer: {% slot footer %} (custom)   │  ← optional slot
└─────────────────────────────────────┘
```

#### Modal

```text
File:     ui/Modal.jinja
Props:    title, open
Slots:    content (body), actions (footer)
Shape:    rounded-xl
Border:   zinc-200 / dark:zinc-800
Shadow:   shadow-xl
Overlay:  zinc-950/60
Close:    Escape key, backdrop click, close button
```

```text
┌──────────────────── z-50 ─────────────────────┐
│ ░░░░░░░░░░░░ Backdrop (zinc-950/60) ░░░░░░░░░│
│ ░░░ ┌───────────────────────────────┐ ░░░░░░░│
│ ░░░ │ Header: title + close btn     │ ░░░░░░░│
│ ░░░ ├───────────────────────────────┤ ░░░░░░░│
│ ░░░ │ Body: {{ content }}           │ ░░░░░░░│
│ ░░░ ├───────────────────────────────┤ ░░░░░░░│
│ ░░░ │ Footer: {% slot actions %}    │ ░░░░░░░│
│ ░░░ └───────────────────────────────┘ ░░░░░░░│
└───────────────────────────────────────────────┘
```

#### StatusDot

```text
File:     ui/StatusDot.jinja
Props:    ok (boolean)
Shape:    rounded-full (circle)
Size:     h-2.5 w-2.5 (10px)
Color:    emerald-500/400 (ok) | rose-500/400 (down)
```

### Partials

#### Breadcrumb

```text
File:     partials/Breadcrumb.jinja
Props:    items (list of {label, href?})
Sep:      "/" in text-zinc-400
Active:   last item, no href, text-zinc-700/200
```

#### ThemeToggle

```text
File:     partials/ThemeToggle.jinja
Props:    (none)
Icons:    Sun (dark:block) / Moon (dark:hidden)
Size:     h-9 w-9 button, h-5 w-5 icon
Stroke:   stroke-width="1.8"
```

#### Toast

```text
File:     partials/Toast.jinja
Props:    message, tone ("success" | "danger" | "neutral")
Position: fixed right-4 top-4 z-50
Duration: 3000ms auto-dismiss
Delivery: hx-swap-oob="true" targeting #toast-portal
```

#### HealthAccordion / HealthAccordionItem

```text
Files:    partials/HealthAccordion.jinja, HealthAccordionItem.jinja
Props:    services (list), service (single)
Features: SSE streaming, Alpine toggle, chevron rotation
Log view: <pre> with font-mono, h-40 overflow-auto
```

#### HealthSummary

```text
File:     partials/HealthSummary.jinja
Props:    services (list)
Refresh:  hx-get every 10s with morph:innerHTML
```

---

## 11. Page Templates

### Home Page

```text
┌─────────────────────────────────────────┐
│ Navbar [Brand] [Home] [Status] [Theme]  │
├─────────────────────────────────────────┤
│ Breadcrumb: Home                        │
│                                         │
│ ┌─ H1 ──────────────────┐ ┌─Badge──┐   │
│ │ Hello, World!          │ │ Online │   │
│ └────────────────────────┘ └────────┘   │
│                                         │
│ ┌─ Card ────────────────────────────┐   │
│ │ Description text                  │   │
│ │                                   │   │
│ │ [View status] (secondary, sm)     │   │
│ └───────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│ Footer: (c) 2025 Brand                  │
└─────────────────────────────────────────┘
```

### Status Page

```text
┌─────────────────────────────────────────┐
│ Navbar                                  │
├─────────────────────────────────────────┤
│ Breadcrumb: Home / Status               │
│                                         │
│ ┌─ H1 ───────┐          ┌──────────┐   │
│ │ Status      │          │ Refresh  │   │
│ └─────────────┘          └──────────┘   │
│                                         │
│ ┌─ Card ────────────────────────────┐   │
│ │ ┌─ Accordion ────────────────────┐│   │
│ │ │ ● Portfolio  [OK]    8000   ▼  ││   │
│ │ ├────────────────────────────────┤│   │
│ │ │ ● Blog       [OK]    8001   ▼  ││   │
│ │ ├────────────────────────────────┤│   │
│ │ │ ● Admin      [DOWN]  8002   ▼  ││   │
│ │ │   ┌─ Logs ──────────────────┐  ││   │
│ │ │   │ [2025-01-01T...] admin: │  ││   │
│ │ │   │ {"status":"DOWN",...}   │  ││   │
│ │ │   └────────────────────────┘  ││   │
│ │ └────────────────────────────────┘│   │
│ └───────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│ Footer                                  │
└─────────────────────────────────────────┘
```

### Error Page (404)

```text
┌─────────────────────────────────────────┐
│ Navbar                                  │
├─────────────────────────────────────────┤
│                                         │
│              404                        │
│         (text-6xl, zinc-200/800)        │
│                                         │
│       ┌─ Card (max-w-md) ─────┐        │
│       │ Page not found         │        │
│       │ The page you are...    │        │
│       │                        │        │
│       │ [Go to Home] [Go back] │        │
│       └────────────────────────┘        │
│                                         │
├─────────────────────────────────────────┤
│ Footer                                  │
└─────────────────────────────────────────┘
```

---

## 12. Interaction Patterns

### HTMX Patterns

| Pattern                    | Trigger            | Swap Strategy           | Target              |
|----------------------------|--------------------|-------------------------|----------------------|
| Health summary polling     | `load, every 10s`  | `morph:innerHTML`       | `#healthz-summary`   |
| Health summary refresh     | click              | `innerHTML`             | `#healthz-summary`   |
| Toast injection            | server-push        | `hx-swap-oob="true"`   | `#toast-portal`      |

### Alpine.js Patterns

| Pattern              | `x-data`                     | Behavior                                     |
|----------------------|------------------------------|----------------------------------------------|
| Dark mode            | `{ dark: false }` on body    | Toggle class on `<html>`, persist to localStorage |
| Modal                | `{ open: true }`             | Escape to close, backdrop click, auto-remove  |
| Toast                | `{ show: true }`             | Auto-dismiss after 3s via `setTimeout`        |
| Accordion            | `{ open, logs, es }`         | Toggle SSE connect/disconnect, chevron rotate |

### SSE Lifecycle (Accordion)

```text
User clicks item
  → toggle()
    → open = true
      → connect()
        → new EventSource('/healthz/logs/stream?service_id=X')
        → onmessage: prepend to logs
        → onerror: disconnect()

User clicks again
  → toggle()
    → open = false
      → disconnect()
        → es.close()
        → es = null
        → logs = ''

HTMX morphs page
  → @htmx:before-swap.window
    → disconnect() (cleanup before DOM replacement)
```

### Focus & Disabled States

```css
/* Buttons */
focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2
disabled:opacity-50 disabled:pointer-events-none
```

### Hover States

| Element          | Light Hover              | Dark Hover                 |
|------------------|--------------------------|----------------------------|
| Nav links        | `bg-zinc-100 text-zinc-900` | `bg-zinc-900 text-zinc-100` |
| Theme toggle     | `bg-zinc-100 text-zinc-900` | `bg-zinc-900 text-zinc-100` |
| Accordion btn    | `bg-zinc-50`            | `bg-zinc-900/50`            |
| Footer links     | `text-zinc-700`         | `text-zinc-200`             |
| Modal close      | `bg-zinc-100`           | `bg-zinc-900`               |

---

## 13. User Flow Diagrams

### Navigation Flow

```text
┌──────────┐  click "Home"   ┌──────────┐
│  Status  │ ──────────────→ │   Home   │
│  /status │ ←────────────── │   /      │
└──────────┘  click "Status"  └──────────┘
      │                            │
      │  click "View status"       │
      └────────────────────────────┘

Any unknown route → 404 Error Page
  → [Go to Home] → /
  → [Go back]    → /
```

### Health Check Data Flow

```text
Browser                     App Server               Other Apps
  │                            │                         │
  │  GET /status               │                         │
  │ ─────────────────────────→ │                         │
  │  ← HTML (Health page)      │                         │
  │                            │                         │
  │  GET /healthz/summary      │                         │
  │ ─────────────────────────→ │                         │
  │                            │  GET /api/healthz ×3    │
  │                            │ ──────────────────────→ │
  │                            │  ← { status, code }     │
  │  ← HTML partial            │                         │
  │    (morph:innerHTML)       │                         │
  │                            │                         │
  │  ... repeats every 10s ... │                         │
  │                            │                         │
  │  [User opens accordion]    │                         │
  │  GET /healthz/logs/stream  │                         │
  │ ─────────────────────────→ │                         │
  │  ← SSE: data: [timestamp]  │                         │
  │  ← SSE: data: [timestamp]  │  (polls /api/healthz    │
  │  ← SSE: data: [timestamp]  │   every 3s per service) │
  │  ...                       │                         │
  │  [User closes accordion]   │                         │
  │  EventSource.close()       │                         │
```

### Toast Notification Flow

```text
Server Action (e.g., form submit)
  │
  ├─ Normal HTML response
  │
  └─ Toast partial (OOB swap)
       │
       ├─ hx-swap-oob="true" → replaces #toast-portal
       │
       └─ Alpine x-init
            │
            ├─ show = true (enters with translate-y-2 → 0)
            │
            └─ setTimeout 3000ms
                 │
                 └─ show = false (leaves with opacity → 0)
```

### Dark Mode Toggle Flow

```text
User clicks ThemeToggle
  │
  └─ Alpine: dark = !dark
       │
       └─ $watch('dark', v => ...)
            │
            ├─ document.documentElement.classList.add/remove('dark')
            │
            └─ localStorage.setItem('theme', 'dark'|'light')

Page Load
  │
  └─ Alpine x-init
       │
       ├─ Check localStorage('theme')
       │    ├─ Found → use saved value
       │    └─ Not found → check prefers-color-scheme
       │
       └─ Apply class to <html>
```

---

## Appendix: Quick Reference Card

```text
COLORS:     Zinc (neutral) + Emerald (success) + Rose (danger)
RADIUS:     md (6px) → lg (8px) → xl (12px) → full (pill/dot)
SHADOWS:    sm (card) → md (toast) → xl (modal)
SPACING:    4px grid (gap-1 → gap-6, px-2 → px-5, py-0.5 → py-6)
BORDERS:    Always 1px, zinc-200 / dark:zinc-800
TEXT:        xs (12) → sm (14) → base (16) → lg (18) → 2xl (24) → 6xl (60)
WEIGHTS:    medium (500) → semibold (600) → bold (700)
Z-INDEX:    40 (navbar) → 50 (modal, toast)
TRANSITIONS: 100–200ms, ease-in (leave) / ease-out (enter)
DARK MODE:  class-based, localStorage, zinc-950 surfaces, inverted buttons
```
