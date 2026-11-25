#!/usr/bin/env python3
"""deck-html layout catalog — validation driver (ticket 09).

For every catalog template: fill the slots of templates/<name>.slide.html
with a dense fixture (the template file is the single source of the slide
structure — the driver instantiates it, it does not retype it), assemble a
mini-deck (cover + fixture) with the ticket-01 assembler, run the full gate
suite — assemble guards, content_check, text_audit (the
text-collision/overflow gate), visible-content, PDF size/pages, R3
double-capture — and keep the deck + frames under
evals/results/layout-catalog/<name>/ for the catalog entry's fixture link.

AGENTS.md test-artifact rule: before a re-render overwrites a FAILED run's
output, the failed tree is copied to <name>/archive/<ts>/ (broken renders
must be archived before fixing in place; the driver enforces it via a
last-run.json status file — a re-render over a PASS is safe, R3 already
proved byte stability).

Usage: catalog_check.py [name ...]   (default: all templates)
Exit: 0 = every template PASS, 1 = at least one FAIL.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(SKILL, "..", ".."))
TPL = os.path.join(SKILL, "templates")
TOKENS = os.path.join(HERE, "themes", "noir.tokens.json")
OUTROOT = os.path.join(ROOT, "evals", "results", "layout-catalog")
CATALOG_CSS = os.path.join(TPL, "catalog.css")

# ---------------------------------------------------------------- fixtures
# Per template: the dense fixture = the slide title + every visible string as
# a skeleton field (content_check is one-directional, but keeping them in the
# skeleton keeps them checked) + the slot values that fill
# templates/<name>.slide.html. Slot values are content fragments only — the
# structural markup (reveal classes, data-beat) lives in the template file.


def f_title():
    return {
        "title": "Плотный контрольный заголовок каталога шаблонов",
        "fields": [
            "ДОКЛАД · БАЗЫ ДАННЫХ",
            "Плотный контрольный заголовок каталога шаблонов",
            "Проверочный слайд: плотный текст для измерения вместимости зоны заголовка",
        ],
        "slots": {
            "id": "x",
            "kicker": "ДОКЛАД · БАЗЫ ДАННЫХ",
            "title": "Плотный контрольный заголовок каталога шаблонов",
            "sub": "Проверочный слайд: плотный текст для измерения вместимости зоны заголовка",
        },
    }


def f_duo(side):
    side_r = "справа" if side == "l" else "слева"
    if side == "l":
        blocks = (
            '<div class="b reveal" data-beat="b1">Первая плотная строка буллета: '
            'двадцать четыре пикселя и мягкий перенос длинных слов.</div>\n'
            '    <div class="b reveal" data-beat="b1">Вторая строка: границы, пределы '
            'и условия, которые обязан показать слайд.</div>\n'
            '    <div class="b reveal" data-beat="b2">Третья строка: цифры и единицы, '
            'проверка переноса чисел со знаками.</div>\n'
            '    <div class="b reveal" data-beat="b2">Четвёртая строка: вывод '
            'для слушателя, один короткий тезис.</div>'
        )
        body = (
            "Первая плотная строка буллета: двадцать четыре пикселя и мягкий перенос длинных слов.\n"
            "Вторая строка: границы, пределы и условия, которые обязан показать слайд.\n"
            "Третья строка: цифры и единицы, проверка переноса чисел со знаками.\n"
            "Четвёртая строка: вывод для слушателя, один короткий тезис."
        )
    else:
        blocks = (
            '<div class="b reveal" data-beat="b1">Зеркальная колонка: первый плотный '
            'буллет с длинным словом и переносом.</div>\n'
            '    <div class="b reveal" data-beat="b1">Второй буллет: условия, '
            'пределы и границы, что должен показать слайд.</div>\n'
            '    <div class="b reveal" data-beat="b2">Третий буллет: цифры, '
            'единицы и проверка переноса со знаками.</div>\n'
            '    <div class="b reveal" data-beat="b2">Четвёртый буллет: '
            'короткий вывод для слушателя.</div>'
        )
        body = (
            "Зеркальная колонка: первый плотный буллет с длинным словом и переносом.\n"
            "Второй буллет: условия, пределы и границы, что должен показать слайд.\n"
            "Третий буллет: цифры, единицы и проверка переноса со знаками.\n"
            "Четвёртый буллет: короткий вывод для слушателя."
        )
    return {
        "title": f"Колонка текста, фигура {side_r}",
        "fields": [
            f"Колонка текста, фигура {side_r}",
            body,
        ],
        "slots": {
            "id": "x",
            "title": f"Колонка текста, фигура {side_r}",
            "blocks": blocks,
            # A real 720x843 geometry (the figure-asset aspect): preserveAspectRatio
            # "none" stretches the SVG to the zone — an off-aspect zone would turn
            # the circle into a visible ellipse, so the frame proves the fit.
            "figure": FIG_SVG_720,
        },
    }


def f_full():
    return {
        "title": "Полный текст: абзац и формула",
        "fields": [
            "Полный текст: абзац и формула",
            "Плотный абзац без буллетов: два-три предложения с длинными словами,\n"
            "цифрами и единицами, проверка переноса на всю ширину слайда.",
            "E = mc²\nΔE_g ≈ 0,6–0,7 эВ",
        ],
        "slots": {
            "id": "x",
            "title": "Полный текст: абзац и формула",
            "blocks": (
                '  <div class="para reveal" data-beat="b1">Плотный абзац без буллетов: '
                'два-три предложения с длинными словами,\n'
                'цифрами и единицами, проверка переноса на всю ширину слайда.</div>\n'
                '  <div class="formula reveal" data-beat="b2">E = mc²\nΔE_g ≈ 0,6–0,7 эВ</div>'
            ),
        },
    }


def f_table():
    rows = [
        ("SCA", "состав поставки", "CVE, лицензии, SBOM"),
        ("SAST", "исходный код", "70+ классов дефектов"),
        ("Фаззинг", "поведение", "покрытие + санитайзеры"),
        ("Харнес", "вход в функцию", "декодер + окружение"),
        ("Корпус", "сиды", "границы, мутации"),
        ("Итого", "все слои", "один конвейер: от состава до поведения"),
    ]
    body = "\n".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    tbl = ("<thead><tr><th>Метод</th><th>Фокус</th><th>Инструменты</th></tr></thead>"
           f"<tbody>\n{body}\n</tbody>")
    field = "Метод Фокус Инструменты\n" + "\n".join(f"{a} {b} {c}" for a, b, c in rows)
    return {
        "title": "Таблица: методы и инструменты",
        "fields": [
            "Таблица: методы и инструменты",
            field,
            "Вывод: таблица держит шесть строк и три колонки без переполнения",
        ],
        "slots": {
            "id": "x",
            "title": "Таблица: методы и инструменты",
            "table": tbl,
            "strip": "Вывод: таблица держит шесть строк и три колонки без переполнения",
        },
    }


def f_cards(n):
    data = [
        ("Состав", "Уязвимые и запрещённые компоненты поставок, лицензии, SBOM"),
        ("Код", "Дефекты в исходниках до выполнения: 70+ классов, 1300+ детекторов"),
        ("Поведение", "Поиск дефектов памяти покрытием: санитайзеры + мутации"),
        ("Вход", "Харнес: декодер байтов в параметры, честная инициализация"),
        ("Корпус", "Сиды на границах: пустые строки, длинные строки, UTF-8"),
    ][:n]
    cards = ""
    for i, (t, b) in enumerate(data):
        cards += (f'  <div class="card reveal" data-beat="b{i // 2 + 1}">\n'
                  f'    <div class="c-title">{t}</div>\n'
                  f'    <div class="c-body">{b}</div>\n  </div>\n')
    fields = ["\n".join(f"{t}\n{b}" for t, b in data)]
    return {
        "title": f"Карточки: {n} концепций",
        "fields": [f"Карточки: {n} концепций"] + fields,
        "slots": {
            "id": "x",
            "title": f"Карточки: {n} концепций",
            "cards": cards,
        },
    }


def f_figure():
    return {
        "title": "Слайд-фигура: рисунок — это слайд",
        "fields": [
            "Слайд-фигура: рисунок — это слайд",
            "Подпись: плотный текст подписи на всю ширину слайда",
        ],
        "slots": {
            "id": "x",
            "title": "Слайд-фигура: рисунок — это слайд",
            # Wide figure asset (the tpl-figure zone inner geometry).
            "figure": FIG_SVG_WIDE,
            "caption": "Подпись: плотный текст подписи на всю ширину слайда",
        },
    }


def f_code():
    code = (
        '<span class="ln reveal" data-beat="b1">CC=afl-clang-fast CXX=afl-clang-fast++ \\\n</span>'
        '<span class="ln reveal" data-beat="b1">CFLAGS="-fsanitize=address" CXXFLAGS="-fsanitize=address" \\\n</span>'
        '<span class="ln reveal" data-beat="b1">../configure --enable-cassert --enable-debug\n</span>'
        '<span class="ln reveal" data-beat="b1">make -j$(nproc)</span>'
    )
    bullets = (
        '<div class="b reveal" data-beat="b2">afl-clang-fast — компилятор AFL: метки покрытия для фаззера\n'
        '-fsanitize=address — AddressSanitizer: переполнения, use-after-free\n'
        '--enable-cassert — штатные assert\u2019ы: инварианты срабатывают раньше ASan\n'
        '--enable-debug — трассировки при сбое читаемы, а не адреса</div>'
    )
    return {
        "title": "Сборка: AFL-компиляторы + ASan + cassert",
        "fields": [
            "Сборка: AFL-компиляторы + ASan + cassert",
            "CC=afl-clang-fast CXX=afl-clang-fast++ \\\nCFLAGS=\"-fsanitize=address\" CXXFLAGS=\"-fsanitize=address\" \\\n../configure --enable-cassert --enable-debug\nmake -j$(nproc)",
            "afl-clang-fast — компилятор AFL: метки покрытия для фаззера\n"
            "-fsanitize=address — AddressSanitizer: переполнения, use-after-free\n"
            "--enable-cassert — штатные assert\u2019ы: инварианты срабатывают раньше ASan\n"
            "--enable-debug — трассировки при сбое читаемы, а не адреса",
            "Пара AFL+ASan: AFL требует «сбой = ненулевой код возврата», ASan именно так роняет процесс",
        ],
        "slots": {
            "id": "x",
            "title": "Сборка: AFL-компиляторы + ASan + cassert",
            "code": code,
            "bullets": bullets,
            "strip": "Пара AFL+ASan: AFL требует «сбой = ненулевой код возврата», ASan именно так роняет процесс",
        },
    }


def f_signature():
    c1 = ('<div class="b reveal" data-beat="b3">Флаг -fsanitize=fuzzer: компилятор сам '
          'подключает фаззер, заменяя main\nБайты из data/size — передаём функции; '
          'сбой — санитайзер сохраняет вход</div>')
    c2 = ('<div class="b reveal" data-beat="b3">Корпус — директория со «зёрнами», '
          'фаззер пополняет её сам;\nудобно прогонять в пайплайне: один бинарник, '
          'без внешнего процесса</div>')
    return {
        "title": "Встраиваемый фаззер LLVM",
        "fields": [
            "Встраиваемый фаззер LLVM",
            "LLVM — инфраструктура компиляторов: «движок», который превращает C-код\n"
            "в машинные команды. «In-process» — фаззер не отдельная программа, а код "
            "внутри бинарника: генерация входов и вызов функции — в одном процессе.",
            "int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size);",
            "Флаг -fsanitize=fuzzer: компилятор сам подключает фаззер, заменяя main\n"
            "Байты из data/size — передаём функции; сбой — санитайзер сохраняет вход",
            "Корпус — директория со «зёрнами», фаззер пополняет её сам;\n"
            "удобно прогонять в пайплайне: один бинарник, без внешнего процесса",
        ],
        "slots": {
            "id": "x",
            "title": "Встраиваемый фаззер LLVM",
            "intro": ("LLVM — инфраструктура компиляторов: «движок», который превращает "
                      "C-код\nв машинные команды. «In-process» — фаззер не отдельная "
                      "программа, а код внутри бинарника: генерация входов и вызов "
                      "функции — в одном процессе."),
            "signature": "int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size);",
            "cards": f'<div class="scard">{c1}</div><div class="scard">{c2}</div>',
        },
    }


def f_pipeline():
    nodes = [
        ("1. Вход", "AFL подсовывает произвольные байты, функция ждёт char*, int64 — декодер превращает байты в параметры"),
        ("2. Окружение", "Много глобального состояния: кодировка, локаль, кэш. Инициализируем до первого вызова"),
        ("3. Вызов", "Прямой вызов тестируемой функции с декодированными параметрами"),
        ("4. Статус", "0 — ок, ненулевой — вход некорректен по логике харнеса; порвалась память — объявит ASan"),
    ]
    html = ""
    fields = []
    for i, (h, c) in enumerate(nodes):
        html += (f'  <div class="pnode reveal" data-beat="b{i + 1}">\n'
                 f'    <div class="chip">\n      <div class="ch-head">{h}</div>\n'
                 f'      <div class="cbody">{c}</div>\n    </div>\n  </div>\n')
        if i < len(nodes) - 1:
            html += '  <div class="parr"></div>\n'
        fields.append(f"{h}\n{c}")
    return {
        "title": "Анатомия харнеса: четыре узла",
        "fields": ["Анатомия харнеса: четыре узла"] + fields,
        "slots": {
            "id": "x",
            "title": "Анатомия харнеса: четыре узла",
            "nodes": html,
        },
    }


def f_verdict():
    layers = [
        ("SCA — Trivy", "Чистота состава поставки: уязвимые и запрещённые по лицензии компоненты", False),
        ("Фаззинг", "Поведение: самый эффективный метод поиска дефектов памяти в больших C-кодбазах", True),
        ("Слои над ними", "Корпус и харнесы: декодер, честная инициализация окружения, хорошие сиды", False),
    ]
    html = ""
    fields = []
    for i, (t, b, hot) in enumerate(layers):
        cls = "layer hot reveal" if hot else "layer reveal"
        html += (f'  <div class="{cls}" data-beat="b{i + 1}">\n'
                 f'    <div class="lt">{t}</div>\n    <div class="lb">{b}</div>\n  </div>\n')
        fields.append(f"{t}\n{b}")
    tail = "Ключ проекта: цель фаззинга — не «весь сервер», а функция; правильный декодер и хорошие сиды"
    return {
        "title": "Итог: безопасность в слоях",
        "fields": ["Итог: безопасность в слоях"] + fields + [tail],
        "slots": {
            "id": "x",
            "title": "Итог: безопасность в слоях",
            "layers": html,
            "tail": tail,
        },
    }


def f_chipduo():
    chips = [
        ("Trivy", "SCA", [("ТИП", "SCA — состав поставки"), ("ФОКУС", "Зависимости, CVE, лицензии, SBOM"), ("ВОПРОС ПРОЕКТА", "«Плохие компоненты в поставке?»")]),
        ("SVACE", "SAST", [("ТИП", "SAST — исходный код"), ("ФОКУС", "70+ классов, 1300+ детекторов"), ("ВОПРОС ПРОЕКТА", "«Дефекты в собственном коде?»")]),
    ]
    html = ""
    fields = []
    for name, badge, rows in chips:
        r = "".join(f'    <div class="ch-row reveal" data-beat="b1"><span class="k">{k}</span><span class="v">{v}</span></div>\n' for k, v in rows)
        html += (f'    <div class="chip">\n'
                 f'      <div class="ch-head reveal">{name}<span class="badge">{badge}</span></div>\n'
                 f'{r}    </div>\n')
        fields.append(f"{name} {badge}\n" + "\n".join(f"{k} {v}" for k, v in rows))
    return {
        "title": "Инструменты проекта: Trivy и SVACE",
        "fields": [
            "Инструменты проекта: Trivy и SVACE",
            "Критерий: Тип · Фокус · Вопрос проекта",
        ] + fields,
        "slots": {
            "id": "x",
            "title": "Инструменты проекта: Trivy и SVACE",
            "critline": "Критерий: Тип · Фокус · Вопрос проекта",
            "chips": html,
        },
    }


def f_quote():
    quote = ("Фаззинг не проверяет программу по спецификации — он ломает её вход "
             "и смотрит, что выживет.\nДефект найден тогда, когда процесс пал, "
             "а не тогда, когда тест провален.")
    source = "Семинар по надёжности ПО, 2025"
    return {
        "title": "Цитата: принцип метода",
        "fields": [
            "Цитата: принцип метода",
            quote,
            source,
        ],
        "slots": {
            "id": "x",
            "title": "Цитата: принцип метода",
            "quote": quote,
            "source": source,
        },
    }


def f_stat():
    return {
        "title": "Цифра: масштаб дефектоскопии",
        "fields": [
            "Цифра: масштаб дефектоскопии",
            "1300+",
            "детекторов дефектов в исходном коде — покрытие всех 70+ классов, "
            "до выполнения программы",
            "Масштаб инструмента определяет, что успевает проверить команда: "
            "статический анализ здесь — не формальность",
        ],
        "slots": {
            "id": "x",
            "title": "Цифра: масштаб дефектоскопии",
            "number": "1300+",
            "caption": ("детекторов дефектов в исходном коде — покрытие всех 70+ "
                        "классов, до выполнения программы"),
            "strip": ("Масштаб инструмента определяет, что успевает проверить "
                      "команда: статический анализ здесь — не формальность"),
        },
    }


TEMPLATES = {
    "title": f_title,
    "duo-l": lambda: f_duo("l"),
    "duo-r": lambda: f_duo("r"),
    "full": f_full,
    "table": f_table,
    "cards": lambda: f_cards(4),
    "grid5": lambda: f_cards(5),
    "figure": f_figure,
    "code": f_code,
    "signature": f_signature,
    "pipeline": f_pipeline,
    "verdict": f_verdict,
    "chipduo": f_chipduo,
    "quote": f_quote,
    "stat": f_stat,
}

# ---------------------------------------------------------------- machinery

# Fixture figure geometry — the exact INNER geometry of each template's
# figure zone (duo: 720x843 zone minus 2x28 padding = 664x787; figure:
# 1776 zone minus 2x24 padding, minus the caption line and gap = 1728x~751).
# preserveAspectRatio="none" stretches the SVG to the inner box, so any
# geometry error in the CSS shows up as a visible ellipse/tilt in the frame.
FIG_SVG_720 = (
    '<svg viewBox="0 0 664 787" preserveAspectRatio="none" aria-hidden="true">\n'
    '  <rect x="6" y="6" width="652" height="775" fill="none"'
    ' stroke="var(--figline)" stroke-width="6"/>\n'
    '  <circle cx="332" cy="393" r="280" fill="none"'
    ' stroke="var(--accent)" stroke-width="6"/>\n'
    '  <line x1="6" y1="781" x2="658" y2="6"'
    ' stroke="var(--accent)" stroke-width="4"/>\n'
    '</svg>'
)
FIG_SVG_WIDE = (
    '<svg viewBox="0 0 1728 751" preserveAspectRatio="none" aria-hidden="true">\n'
    '  <rect x="6" y="6" width="1716" height="739" fill="none"'
    ' stroke="var(--figline)" stroke-width="6"/>\n'
    '  <circle cx="864" cy="375" r="330" fill="none"'
    ' stroke="var(--accent)" stroke-width="6"/>\n'
    '  <line x1="6" y1="745" x2="1722" y2="6"'
    ' stroke="var(--accent)" stroke-width="4"/>\n'
    '</svg>'
)


def now_ts():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def maybe_archive(out, name):
    """AGENTS.md: archive the previous run's output when it FAILED, before the
    new render overwrites it (broken renders are evidence, not throwaways)."""
    lr = os.path.join(out, "last-run.json")
    if not (os.path.isdir(out) and os.path.isfile(lr)):
        return
    try:
        prev = json.load(open(lr, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if prev.get("status") != "FAIL":
        return
    arch = os.path.join(out, "archive", prev.get("ts") or "unknown")
    os.makedirs(arch, exist_ok=True)
    for f in os.listdir(out):
        if f in ("archive", "last-run.json"):
            continue
        src = os.path.join(out, f)
        dst = os.path.join(arch, f)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    print(f"catalog: archived failed render of {name} → "
          f"{os.path.relpath(arch, ROOT)}")


def instantiate(name, fx):
    """Fill the template file's slots; the template is the structure's source
    of truth, so any divergence between fixture and template is a FAIL, not a
    silent re-implementation."""
    tpl = open(os.path.join(TPL, name + ".slide.html"), encoding="utf-8").read()
    slide = tpl
    for k, v in fx["slots"].items():
        slide = slide.replace("{{%s}}" % k, v)
    leftover = sorted(set(re.findall(r"\{\{\w+\}\}", slide)))
    if leftover:
        return None, f"unfilled slots in {name}.slide.html: {leftover}"
    if 'id="x"' not in slide:
        return None, f"{name}: section id 'x' not filled (skeleton slide id mismatch)"
    return slide, None


def css_sections():
    css = open(CATALOG_CSS, encoding="utf-8").read()
    parts = re.split(r"/\* =+ ", css)
    out = {}
    for p in parts[1:]:
        header, _, body = p.partition("\n")
        key = header.split(" — ")[0].strip()
        out[key] = body.rstrip() + "\n"
    return out


def skeleton_yaml(name, fx):
    blocks = []
    for i, f_ in enumerate(fx["fields"]):
        if i == 0:
            continue  # the slide title field
        blocks.append(f"  - id: a{i}\n    type: text\n    text: |\n" +
                      "".join("      " + ln + "\n" for ln in f_.split("\n")))
    return (
        "skeleton_version: 1\n"
        "meta:\n  title: 'Catalog fixture: " + name + "'\n  audience: test\n"
        "  lang: ru\n  target: html\n  canvas: '16:9'\n  tone: academic\n"
        "  anim_role: factual\n"
        "slides:\n"
        "- id: t\n  title: 'Catalog fixture cover'\n  layout: section\n"
        "  blocks:\n  - id: a0\n    type: text\n    text: 'Mini-deck for template validation'\n"
        "  figure: null\n"
        f"- id: x\n  title: {fx['title']!r}\n  layout: full\n"
        "  blocks:\n" + "\n".join(blocks) + "\n  figure: null\n"
    )


COVER = ('<section class="slide title" id="t"><div class="inner">\n'
         '<h1 class="reveal">Catalog fixture cover</h1>\n'
         '<p class="reveal">Mini-deck for template validation</p>\n'
         '</div></section>\n')


def run(cmd, cwd=ROOT):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def check(name):
    fx = TEMPLATES[name]()
    slide, err = instantiate(name, fx)
    problems = []
    if err:
        problems.append(err)
    else:
        secs = css_sections()
        keys = [k for k in secs if k.startswith("common") or k.startswith(f"tpl-{name}")]
        styles = "\n".join(secs[k] for k in keys)
        out = os.path.join(OUTROOT, name)
        maybe_archive(out, name)
        sd = os.path.join(out, "slides")
        os.makedirs(sd, exist_ok=True)
        with open(os.path.join(sd, "01-t.html"), "w", encoding="utf-8") as f:
            f.write(COVER)
        with open(os.path.join(sd, "02-x.html"), "w", encoding="utf-8") as f:
            f.write(slide)
        sk = os.path.join(out, "skeleton.yaml")
        with open(sk, "w", encoding="utf-8") as f:
            f.write(skeleton_yaml(name, fx))
        st = os.path.join(out, "styles.css")
        with open(st, "w", encoding="utf-8") as f:
            f.write(styles)
        deck = os.path.join(out, "deck.html")

        r = run([sys.executable, os.path.join(HERE, "assemble.py"), sd, deck,
                 "--tokens", TOKENS, "--styles", st, "--skeleton", sk])
        if r.returncode != 0:
            problems.append(f"assemble: {r.stderr.strip()}")
        else:
            r = run([sys.executable, os.path.join(HERE, "content_check.py"), sk, deck])
            if r.returncode != 0:
                problems.append("content_check:\n" + r.stdout.strip())
            r = run([sys.executable, os.path.join(HERE, "text_audit.py"), deck])
            if r.returncode != 0:
                problems.append("text_audit:\n" + r.stdout.strip())
            r = run(["bash", os.path.join(HERE, "render_html.sh"), deck,
                     os.path.join(out, "qa"), "2", "2"])
            if r.returncode != 0:
                problems.append("render gates:\n" + (r.stdout + r.stderr).strip())

    status = "PASS" if not problems else "FAIL"
    out = os.path.join(OUTROOT, name)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "last-run.json"), "w", encoding="utf-8") as f:
        json.dump({"name": name, "status": status, "ts": now_ts(),
                   "problems": problems}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"catalog [{status}] {name}")
    for p in problems:
        print("   " + p.replace("\n", "\n   "))
    return not problems


def main():
    names = sys.argv[1:] or list(TEMPLATES)
    for n in names:
        if n not in TEMPLATES:
            sys.exit(f"unknown template: {n} (known: {', '.join(TEMPLATES)})")
    results = [check(n) for n in names]
    if not all(results):
        sys.exit(1)
    print(f"catalog_check: {sum(results)}/{len(results)} templates PASS")


if __name__ == "__main__":
    main()
