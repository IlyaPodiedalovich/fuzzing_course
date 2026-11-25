# presentation/

Рабочее пространство для перевода курса «Курс по фаззингу: AFL, libFuzzer, Atheris»
(`course.md`) в HTML-презентацию.

| Файл | Что |
|---|---|
| `fuzzing-course.skeleton.yaml` | скелет (schema v1.1): 35 слайдов: титул, разделы, таблицы, три diagram-сцены, beat-таблицы. Validate: `python3 .pi/skills/presentation-skeleton/scripts/validate.py fuzzing-course.skeleton.yaml` |
| `design.md` | airbrush design-пакет (из designmd.app/library/airbrush): токены, цвета, типографика, радиус/отступы, компоненты, эффекты, do's/don'ts. Ссылается `meta.design_ref` |
| `prompt.md` | AI Prompt + Execution Rules + Implementation Checklist с той же страницы, дословно |
| `airbrush.tokens.json` | токены Airbrush для deck-html (stage_bg/slide_bg #1a0f2e, figfill #2b1b3d, figline #6b4a8a, figtext #fdf3e7, accent #ff6b35, accent_glow rgba(255,46,136,0.28)). Font: Montserrat 400/700 (latin + cyrillic subsets) — Eurostile/Avenir Next не гарантируют кириллицу, см. design.md (кириллический запасной вариант) |
| `airbrush.effects.css` | factura-слой (статичные угловые свечения, frozen-print) |
| `deck.html` / `deck.pdf` | собранная дека (генератор-route, 35 слайдов, 3 фигуры) |
| `assets/fig-<id>.svg/.manifest.json/.tl.js/.png` | ассеты трёх диаграмм (fig-s1, fig-s2, fig-s30) |

## Сборка v1

```
python3 .pi/skills/deck-html/scripts/gen_deck.py fuzzing-course.skeleton.yaml \
  --theme airbrush.tokens.json --effects airbrush.effects.css \
  --figs assets deck.html
```

Gates: `validate.py` (OK) · `text_fit.py` (0 OVER) · `content_check.py` (PASS) ·
`text_audit.py` (PASS, 0 problems) · `render_html.sh` (visible-content, pdf-size
1440x810, pdf-pages 35, r3 — все PASS) · `type_floor.py` (0 warnings).

Фигуры (deck-animation): fig-s1 — цикл обратной связи; fig-s2 — три уровня
инструмента; fig-s30 — полный цикл. Все прошли QA-loop (frames на центрах бэатов,
R3 md5 совпадают).

Примечание: шрифт-токен `Eurostile/Avenir Next` из design.md не гарантирует
глифы кириллицы; в v1 использован Montserrat 400/700 (latin + cyrillic subsets,
как Montserrat-пример в скриптах deck-html). PDF/HTML self-contained: шрифты
встраиваются base64.

Следующий этап: v2 — см. `presentation/v2/` (асинхронно строится субагентом).
