# presentation/v2/

Вторая версия деки: 35 слайдов, на 28 из них фигура (диаграмма, график, карточки),
анимация на каждом слайде показывает идею, а не появление текста.

| Файл | Что |
|---|---|
| `fuzzing-course.v2.skeleton.yaml` | скелет (schema v1.1): 35 слайдов, 28 фигур, beat-таблицы. Валидация: `python3 .pi/skills/presentation-skeleton/scripts/validate.py presentation/v2/fuzzing-course.v2.skeleton.yaml` |
| `tokens.json` | design.md, переведённый в контракт токенов deck-html (см. `.pi/skills/deck-html/references/design-tokens.md`) |
| `airbrush.effects.css` | фактура airbrush (радиальные свечения, хромовая кромка панелей, градиентная линейка раздела). Статика; `position` слайда не трогает (gotchas F-H5) |
| `figs/` | исходники фигур: `figlib.py` (примитивы, манифест, фрагмент, нормировка beat-окон), `figs_a.py` (s1..s10), `figs_b.py` (s12..s30), `build.py` |
| `assets/fig-*.{svg,manifest.json,tl.js,png}` | 28 наборов фигур: осевшее состояние, манифест, GSAP-фрагмент, PNG |
| `deck.html` / `deck.pdf` | собранная дека (generated route, `gen_deck.py`) |
| `qa/` | контактный лист осевших кадров и один средний кадр для проверки |

## Сборка

```bash
python3 presentation/v2/figs/build.py            # пересобрать 28 фигур
python3 .pi/skills/deck-html/scripts/gen_deck.py \
    presentation/v2/fuzzing-course.v2.skeleton.yaml \
    --theme presentation/v2/tokens.json \
    --effects presentation/v2/airbrush.effects.css \
    --figs presentation/v2/assets presentation/v2/deck.html
python3 .pi/skills/deck-html/scripts/content_check.py \
    presentation/v2/fuzzing-course.v2.skeleton.yaml presentation/v2/deck.html
python3 .pi/skills/deck-html/scripts/text_audit.py presentation/v2/deck.html
bash .pi/skills/deck-html/scripts/render_html.sh presentation/v2/deck.html presentation/v2/qa 35 10
```

QA одной фигуры (deck-animation): `fig_harness.py` + `capture.sh`, кадры в центрах
битов; `build.py` печатает проверку «каждый твин заканчивается до центра своего бита».

## Шрифты

Дизайн называет `Eurostile` и `Avenir Next`; кириллицу они не гарантируют
(предупреждение в `../design.md`). В токенах вшит `Montserrat` (latin + cyrillic,
400/700) как кириллический заменитель, стек: `Montserrat, Century Gothic, PT Sans,
DejaVu Sans`.
