# Prompt: Airbrush / 70s-80s Illustration

**Источник:** [designmd.app/library/airbrush](https://designmd.app/library/airbrush)
(раздел «AI Prompt» на странице дизайн-системы). Сохранён дословно —
в `<INSERT THEME>` и `<INSERT SECTIONS>` нужно подставлять
контекст конкретного задания.

---

Act as a Senior Frontend Engineer and Expert UI Designer.
Your task is to code a complete Landing Page on the first attempt.
- Landing Page Theme: `<INSERT THEME>`
- Sections to add: `<INSERT SECTIONS>`

Generate the final code immediately following these definitions:

## Style

- **Name:** Airbrush / 70s-80s Illustration
- **Type:** claude-artisan/texture
- **Keywords:** Airbrush / 70s-80s Illustration, airbrushed, van art, Smooth gradient shading and soft glows, Chrome, lasers, fantasy sci-fi scenes, Highly polished rendered surfaces, Retro album/poster illustration, texture
- **Era:** 1970s–1980s
- **Light/Dark:** Fonte não declara modos; validar em light e dark antes de publicar

## Color Palette

- **Primary:** bg: #1a0f2e, surface: #2b1b3d, surface-strong: #3d2554, border: #6b4a8a
- **Secondary:** text: #fdf3e7, text-muted: rgba(253, 243, 231, 0.72), primary: #ff6b35, accent: #ff2e88, chrome: #cbd5e1

## Visual Effects

Smooth gradient shading and soft glows, Chrome, lasers, fantasy sci-fi scenes, Highly polished rendered surfaces, Retro album/poster illustration, shadow

## AI Visual Direction

Airbrush / 70s-80s Illustration, Smooth gradient shading and soft glows, Chrome, lasers, fantasy sci-fi scenes, Highly polished rendered surfaces, Retro album/poster illustration, 70s-80s sci-fi paperback covers; van murals.

## CSS Technical

\`\`\`css
/* Airbrush / 70s-80s Illustration — design tokens */
/* 1970s–1980s | Airbrush illustration golden age (sci-fi/van art), condensed */
:root {
  /* color */
  --color-bg: #1a0f2e;
  --color-surface: #2b1b3d;
  --color-surface-strong: #3d2554;
  --color-border: #6b4a8a;
  --color-text: #fdf3e7;
  --color-text-muted: rgba(253, 243, 231, 0.72);
  --color-primary: #ff6b35;
  --color-accent: #ff2e88;
  --color-chrome: #cbd5e1;
  /* radius */
  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 32px;
  --radius-pill: 999px;
  /* shadow */
  --shadow-sm: 0 2px 10px rgba(255,107,53,0.25);
  --shadow-md: 0 10px 30px rgba(255,46,136,0.28);
  --shadow-lg: 0 24px 60px rgba(255,107,53,0.3);
  /* font */
  --font-sans: 'Avenir Next', 'Century Gothic', system-ui, sans-serif;
  --font-display: 'Eurostile', 'Century Gothic', sans-serif;
  --font-mono: ui-monospace, monospace;
  /* text */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.375rem;
  --text-2xl: 1.75rem;
  --text-3xl: 2.25rem;
  --text-4xl: 3rem;
  --text-5xl: 4rem;
  /* space */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
  --space-24: 96px;
  /* ease */
  --ease-standard: cubic-bezier(0.3, 0, 0.15, 1);
  /* extra: sunset airbrush glow + polished specular highlight */
  --bg-image: radial-gradient(80% 60% at 80% 0%, #ff6b35 0%, transparent 55%),
    radial-gradient(70% 50% at 10% 100%, #ff2e88 0%, transparent 60%),
    linear-gradient(160deg, #2b1b3d 0%, #1a0f2e 60%);
  --airbrush-glow: radial-gradient(120% 140% at 20% -20%, rgba(255,255,255,0.25) 0%, transparent 45%),
    linear-gradient(135deg, #3d2554, #2b1b3d);
}
\`\`\`

## Execution Rules (из страницы дизайна)

1. Strictly follow the defined visual style.
2. Use high-quality inline SVG icons (Heroicons or Lucide style) — NEVER use emojis as icons.
3. Add `cursor-pointer` and smooth `hover` states (transition-all) on all interactive elements.
4. Required Page Structure: Navbar (Logo + Links + CTA) → Hero Section (Impactful Headline + Subtitle + 2 buttons + 3D/Abstract visual element via CSS) → Features (3 cards with icons) → Testimonials (3 cards) → Pricing (3 tiers, highlight the middle one) → Final CTA → Footer (social links, privacy policy, terms of use, contact and SEO links).
5. All text content must be in English (на странице источника; для русского дедика — перевести на русский).
6. The visual must be CLEARLY distinct — do not create a "default Bootstrap" design. Force the use of the provided design system variables.
7. Use `<style>` tags in the head for custom classes (especially for complex backdrop-filter effects and animations) that Tailwind CDN doesn't cover.
8. Full Responsiveness: Layout must adapt perfectly to Mobile, Tablet and Desktop (vertical stack on mobile).
9. Include basic SEO, Viewport and Open Graph meta tags in `<head>`.
10. Footer must contain: Copyright 2026, Secondary navigation links and Social media icons.
11. Make the creative decisions needed to deliver the complete, functional result now.

## Implementation Checklist (из страницы дизайна)

- Contraste WCAG AA; foco visível; navegação por teclado; estados hover/pressed; responsividade; prefers-reduced-motion; Tailwind v4 via @theme.

## Provenance

Last synced: 8/30/2026 · designmd.app/library/airbrush · claude-artisan (MIT) · commit `ae6d3ad`

**Заметка (перевод для русского дедика):** пункты про «English only» и «page structure» (Navbar/Hero/Features/Testimonials/Pricing/Footer) — шаблон для ленда, НЕ для дедика. Для этого дедика применим только токен-сет, шрифты и эффекты; структура слайдов задана skeleton'ом.
