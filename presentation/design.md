# Airbrush / 70s-80s Illustration — дизайн-система

**Источник:** [designmd.app/library/airbrush](https://designmd.app/library/airbrush)
(Imported from `ara-mkr/claude-artisan` · MIT · commit `ae6d3ad` · 2026-08-30).
Это дизайн-пакет, который skeleton ссылается в `meta.design_ref`; deck skills
конвертируют его в `tokens.json` (+ опционально `effects.css`) перед сборкой.

- **Название:** Airbrush / 70s-80s Illustration
- **Категория:** texture (claude-artisan/texture)
- **Эпоха:** 1970s–1980s — золотой век airbrush-иллюстрации (sci-fi / van art)
- **Референс:** 70s–80s sci-fi обложки буклетов; van-murals
- **Структурная основа:** editorial-разметка с типографической сеткой
- **Ключевые признаки:** гладкие градиентные шейдинги и мягкие свечения;
  хромированные поверхности и лазеры; fantasy sci-fi сцены; высокая полировка
  поверхностей; стиль ретро-плаката/альбома

## Цвета

| Роль | Значение |
|---|---|
| `bg` | `#1a0f2e` — фон (глубокий фиолетовый) |
| `surface` | `#2b1b3d` — карточки, поверхности |
| `surface-strong` | `#3d2554` — вложенные поверхности |
| `border` | `#6b4a8a` — границы |
| `text` | `#fdf3e7` — основной текст (тёплый кремовый) |
| `text-muted` | `rgba(253, 243, 231, 0.72)` — приглушённый |
| `primary` (оранжевый) | `#ff6b35` — главный акцент, свечение |
| `accent` (розовый) | `#ff2e88` — вторичный акцент |
| `chrome` | `#cbd5e1` — металл/хромированные элементы |

**Градиенты:**

```css
--bg-image: radial-gradient(80% 60% at 80% 0%, #ff6b35 0%, transparent 55%),
  radial-gradient(70% 50% at 10% 100%, #ff2e88 0%, transparent 60%),
  linear-gradient(160deg, #2b1b3d 0%, #1a0f2e 60%);
--airbrush-glow: radial-gradient(120% 140% at 20% -20%, rgba(255,255,255,0.25) 0%, transparent 45%),
  linear-gradient(135deg, #3d2554, #2b1b3d);
```

Signature-move: мягкое радиальное «airbrush-подсветка» (свечение sunset-дуги,
плавно исчезающее) на каждой приподнятой поверхности — на nav, card,
кнопке-primary.

## Типографика

| Роль | Семейство | Размер | Вес |
|---|---|---|---|
| Display (заголовки) | `'Eurostile', 'Century Gothic', sans-serif` | `4rem` | 700 |
| Body | `'Avenir Next', 'Century Gothic', system-ui, sans-serif` | `1rem`, line-height 1.6 | 400 |
| Label-caps (метки) | `'Avenir Next', 'Century Gothic', system-ui, sans-serif` | `0.75rem` | 600, letter-spacing 0.06em |
| Mono | `ui-monospace, monospace` | — | — |

> **Внимание (кириллица).** Deck — русский текст. `Eurostile` и `Avenir Next`
> не гарантируют полноценную поддержку кириллицы: перед финализацией
> проверьте глиф-покрытие display/body-шрифтов (checklist renderer:
> font coverage) и подставьте кириллический запасной вариант
> (например, `'PT Sans'`, `'Rubik'`, `'Unbounded'`).

## Радиусы и отступы

- Радиус: `sm 8px` · `md 16px` · `lg 32px` · pill `999px`
- Отступы: `4px · 8px · 12px · 16px · 24px · 32px · 48px · 64px · 96px`
- Тень: `sm: 0 2px 10px rgba(255,107,53,0.25)` · `md: 0 10px 30px rgba(255,46,136,0.28)` · `lg: 0 24px 60px rgba(255,107,53,0.3)`
- Переходы: `cubic-bezier(0.3, 0, 0.15, 1)`

## Компоненты

| Компонент | Токены |
|---|---|
| `page` | фон `--color-bg`, текст `--color-text`, padding 16px |
| `card` | фон `--airbrush-glow`, `border 1px var(--color-border)`, radius `lg`, padding 24px, shadow `md` |
| `button-primary` | фон `--airbrush-glow` + градиент primary→accent, radius `md`, padding 16px, цвет `#1a0f2e`, weight 800 |
| `button-secondary` | фон `--color-accent`, radius `md` |
| `badge` | градиент primary→accent, pill, 12px/700 |
| `input` | фон `--color-surface-strong`, border, radius `sm`; фокус — `border-color accent` + ring `rgba(255,46,136,0.3)` |
| `nav` | фон `--airbrush-glow`, border, radius pill, shadow `sm` |

**Do's:** WCAG AA контраст; видимый фокус; `prefers-reduced-motion`;
hover/pressed/focus состояния на интерактивных элементах; рендер с градиент-свечением вместо «flat» дизайна.
**Don'ts:** не использовать стиль как украшение без функциональной иерархии; не добавлять анимации без смысла; не ложить текст на текст (только на фоны с достаточным контрастом).

## Layout / Elevation

- Editorial-сетка, адаптив (сворачивать колонки ниже 768px без горизонтальной прокрутки).
- Свечения/световые ореолы на поверхности; shadow-elevation вместо flat-размещения.
- Декоративные градиенты всегда за контентом (z-order: фон → декор → контент).

## AI Visual Direction

Airbrush / 70s-80s Illustration — гладкие градиентные шейдинги и мягкие
свечения; хромированные поверхности и лазеры; fantasy sci-fi сцены;
высокая полировка поверхностей; retro album/poster illustration; 70s-80s
sci-fi обложки и van-murals. Для deck-сцены: глубокий фиолетово-тёплый фон,
оранжево-розовый градиентный акцент, тёмный контрастный текст на светлых
поверхностях — всё в стиле «sci-fi poster».

## Execution Rules

1. Строго следовать дизайн-системным токенам.
2. Иконки — качественные инлайн-SVG (Heroicons / Lucide); НЕ использовать эмодзи как иконки.
3. `cursor-pointer` и плавные hover-состояния на всех интерактивных элементах.
4. Полная адаптивность (вертикальный стек на мобильном).
5. SEO/viewport/Open Graph в `<head>`; footer: Copyright + вторичная навигация + соц-иконки.
6. Текст — русский (кириллица); убедиться в полном глиф-покрытии шрифтов.
7. Светлый/тёмный режимы: источник не декларирует пары — декодировать под
   тёмную сцену (как фон #1a0f2e), не объявлять light/dark.

## Справочно (для deck-html)

- `stage_bg` / `slide_bg` — `#1a0f2e`; `rowalt` — `#2b1b3d`/`#3d2554`; `headertext` — `#fdf3e7`; `accent` — `#ff6b35`; `accent_glow` — `rgba(255,46,136,0.28)`; `figfill` — `#2b1b3d`; `figline` — `#6b4a8a`; `figtext` — `#fdf3e7`.
- Fonts: display — Eurostile/Century Gothic (с кириллическим запасным вариантом), body — Avenir Next/Century Gothic.
