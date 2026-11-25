"""figures s1 to s14"""
from figlib import *  # noqa: F401,F403

# --------------------------------------------------------------------------
# s1: coverage-guided loop
# --------------------------------------------------------------------------
def fig_s1():
    b = []
    b.append(lines_box(230, 30, 340, 80, ["Стартовый корпус"], gid="fs1-n1"))
    b.append(arrow([(400, 110), (400, 146)], "fs1-a12"))
    b.append(lines_box(230, 150, 340, 80, ["Мутация входов"], gid="fs1-n2"))
    b.append(arrow([(400, 230), (400, 266)], "fs1-a23"))
    b.append(lines_box(180, 270, 440, 100,
                       ["Обёртка: цель", "под инструментацией"], gid="fs1-n3"))
    b.append(arrow([(400, 370), (400, 400)], "fs1-a34"))
    b.append(lines_box(230, 400, 340, 80, ["Битмап покрытия"], gid="fs1-n4"))
    b.append(arrow([(400, 480), (400, 522)], "fs1-a4d"))
    b.append('<g id="fs1-diamond">'
             + f'<path d="M 400,526 L 600,590 L 400,654 L 200,590 Z" fill="{SURF}" '
             f'stroke="{OR}" stroke-width="3"/>'
             + T(400, 600, "Новое покрытие?", size=26) + "</g>")
    b.append(arrow([(400, 654), (400, 686), (195, 686), (195, 700)], "fs1-ada"))
    b.append(arrow([(400, 654), (400, 686), (605, 686), (605, 700)], "fs1-adn"))
    b.append(T(285, 668, "Да", size=26, fill=OR, gid="fs1-lbda"))
    b.append(T(520, 668, "Нет", size=26, fill=MUT, gid="fs1-lbdn"))
    b.append(lines_box(30, 700, 300, 90, ["Сохранить в корпус"], size=25,
                       gid="fs1-n6"))
    b.append(lines_box(470, 700, 300, 90, ["Отбросить вход"], size=25,
                       gid="fs1-n7"))
    b.append(arrow([(30, 745), (14, 745), (14, 70), (230, 70)], "fs1-aret1"))
    b.append(arrow([(770, 745), (786, 745), (786, 190), (570, 190)], "fs1-aret2"))
    tw = [
        dict(sel="#fs1-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs1-n1", kind="rise", t=0.8, d=0.45),
        dict(sel="#fs1-a12", kind="draw", t=0.9, d=0.45),
        dict(sel="#fs1-n2", kind="rise", t=1.1, d=0.45),
        dict(sel="#fs1-a23", kind="draw", t=1.25, d=0.45),
        dict(sel="#fs1-n3", kind="rise", t=1.45, d=0.45),
        dict(sel="#fs1-a34", kind="draw", t=2.0, d=0.45),
        dict(sel="#fs1-n4", kind="rise", t=2.1, d=0.45),
        dict(sel="#fs1-a4d", kind="draw", t=2.2, d=0.45),
        dict(sel="#fs1-diamond", kind="rise", t=2.3, d=0.45),
        dict(sel="#fs1-ada", kind="draw", t=2.45, d=0.45),
        dict(sel="#fs1-adn", kind="draw", t=2.55, d=0.45),
        dict(sel="#fs1-lbda", kind="rise", t=2.6, d=0.35),
        dict(sel="#fs1-lbdn", kind="rise", t=2.65, d=0.35),
        dict(sel="#fs1-n6", kind="rise", t=2.7, d=0.45),
        dict(sel="#fs1-n7", kind="rise", t=2.75, d=0.45),
        dict(sel="#fs1-aret1", kind="draw", t=2.85, d=0.6),
        dict(sel="#fs1-aret2", kind="draw", t=2.95, d=0.6),
    ]
    els = [("fs1-n1", "b1", "node", "dimmed"), ("fs1-a12", "b1", "arrow", "undrawn"),
           ("fs1-n2", "b1", "node", "dimmed"), ("fs1-a23", "b1", "arrow", "undrawn"),
           ("fs1-n3", "b1", "node", "dimmed"), ("fs1-a34", "b2", "arrow", "undrawn"),
           ("fs1-n4", "b2", "node", "dimmed"), ("fs1-diamond", "b2", "node", "dimmed"),
           ("fs1-ada", "b2", "arrow", "undrawn"), ("fs1-adn", "b2", "arrow", "undrawn"),
           ("fs1-n6", "b2", "node", "dimmed"), ("fs1-n7", "b2", "node", "dimmed"),
           ("fs1-aret1", "b2", "arrow", "undrawn"),
           ("fs1-aret2", "b2", "arrow", "undrawn")]
    return "".join(b), tw, els


figure("s1", (W_A, H_A), fig_s1, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.8)],
       "loop figure; wrapper rises 0.5 s, informative tweens 0.45 s each, "
       "the last beat holds the settled picture")

# --------------------------------------------------------------------------
# s2: three layers
# --------------------------------------------------------------------------
def fig_s2():
    b = []
    b.append(lines_box(430, 30, 780, 150,
                       ["Фаззер: afl-fuzz, libFuzzer, atheris",
                        "мутирует входы, оценивает покрытие, сохраняет корпус"],
                       fills=[TXT, MUT], gid="fs2-top"))
    b.append(arrow([(820, 220), (820, 180)], "fs2-a-top"))
    b.append(lines_box(430, 220, 780, 150,
                       ["Обёртка (harness)",
                        "сырые байты становятся формой, которую ждёт цель"],
                       fills=[OR, MUT], gid="fs2-mid"))
    b.append(arrow([(820, 410), (820, 370)], "fs2-a-mid"))
    b.append(lines_box(430, 410, 780, 150,
                       ["Компилятор и флаги",
                        "clang -fsanitize=fuzzer,address; afl-clang-fast"],
                       fills=[TXT, MUT], stroke=OR, gid="fs2-bot"))
    b.append(T(30, 492, "инструментация", size=25, anchor="start",
               fill=OR, gid="fs2-lleft"))
    b.append(T(30, 524, "при сборке", size=25, anchor="start",
               fill=OR, gid="fs2-lleft2"))
    b.append(arrow([(215, 505), (426, 505)], "fs2-a-left"))
    b.append(T(1540, 112, "исполнение", size=25, anchor="end", fill=MUT,
               gid="fs2-lright"))
    b.append(arrow([(1214, 107), (1340, 107)], "fs2-a-right"))
    tw = [
        dict(sel="#fs2-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs2-bot", kind="rise", t=0.8, d=0.5),
        dict(sel="#fs2-lleft", kind="rise", t=0.95, d=0.45),
        dict(sel="#fs2-lleft2", kind="rise", t=0.98, d=0.45),
        dict(sel="#fs2-a-left", kind="draw", t=1.05, d=0.4),
        dict(sel="#fs2-mid", kind="rise", t=2.0, d=0.5),
        dict(sel="#fs2-top", kind="rise", t=2.15, d=0.5),
        dict(sel="#fs2-a-mid", kind="draw", t=2.2, d=0.4),
        dict(sel="#fs2-a-top", kind="draw", t=2.3, d=0.4),
        dict(sel="#fs2-lright", kind="rise", t=2.5, d=0.45),
        dict(sel="#fs2-a-right", kind="draw", t=2.6, d=0.45),
    ]
    els = [("fs2-bot", "b1", "box", "dimmed"), ("fs2-lleft", "b1", "label", "dimmed"),
           ("fs2-lleft2", "b1", "label", "dimmed"),
           ("fs2-a-left", "b1", "leader", "undrawn"),
           ("fs2-mid", "b2", "box", "dimmed"), ("fs2-top", "b2", "box", "dimmed"),
           ("fs2-a-mid", "b2", "arrow", "undrawn"),
           ("fs2-a-top", "b2", "arrow", "undrawn"),
           ("fs2-lright", "b2", "label", "dimmed"),
           ("fs2-a-right", "b2", "leader", "undrawn")]
    return "".join(b), tw, els


figure("s2", (W_B, H_B), fig_s2, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.8)],
       "stack of three layers; bottom layer first (instrumentation), then the "
       "harness and the fuzzer with their arrows")

# --------------------------------------------------------------------------
# s3: McCabe CFG with two paths
# --------------------------------------------------------------------------
def fig_s3():
    b = []
    n = {"1": (400, 100), "2": (230, 280), "3": (570, 280), "4": (230, 470),
         "5": (570, 470), "6": (400, 650)}
    edges = [(n["1"], n["2"]), (n["1"], n["3"]), (n["2"], n["4"]),
             (n["3"], n["5"]), (n["4"], n["6"]), (n["5"], n["6"])]
    es = []
    for (x1, y1), (x2, y2) in edges:
        es.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                  f'stroke="{LINE}" stroke-width="3"/>')
    b.append('<g id="fs3-edges">' + "".join(es) + "</g>")
    b.append(draw("fs3-p1", [n["1"], n["2"], n["4"], n["6"]], OR))
    b.append(draw("fs3-p2", [n["1"], n["3"], n["5"], n["6"]], ROSE))
    nodes = []
    for k, (x, y) in n.items():
        nodes.append(f'<circle cx="{x}" cy="{y}" r="42" fill="{SURF}" '
                     f'stroke="{TXT}" stroke-width="3"/>')
        nodes.append(T(x, y + 10, k, size=30, weight=700))
    b.append('<g id="fs3-nodes">' + "".join(nodes) + "</g>")
    b.append(T(150, 392, "P1", size=28, fill=OR, weight=700, gid="fs3-lp1"))
    b.append(T(650, 392, "P2", size=28, fill=ROSE, weight=700, gid="fs3-lp2"))
    b.append(pill(290, 742, 220, 64, "CCN = 2", size=28, fill=SURF, txt=TXT,
                  stroke=OR, gid="fs3-badge"))
    b.append(T(400, 852, "два независимых пути", size=25, fill=MUT, gid="fs3-lnote"))
    tw = [
        dict(sel="#fs3-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs3-edges", kind="rise", t=0.05, d=0.45, to=0.55),
        dict(sel="#fs3-nodes", kind="rise", t=0.05, d=0.45, to=0.7),
        dict(sel="#fs3-p1", kind="draw", t=0.85, d=1.1),
        dict(sel="#fs3-lp1", kind="rise", t=0.95, d=0.35),
        dict(sel="#fs3-p2", kind="draw", t=2.05, d=1.1),
        dict(sel="#fs3-lp2", kind="rise", t=2.15, d=0.35),
        dict(sel="#fs3-badge", kind="rise", t=2.35, d=0.4),
        dict(sel="#fs3-lnote", kind="rise", t=2.45, d=0.4),
        dict(sel="#fs3-edges", kind="rise", t=2.5, d=0.4, to=1),
        dict(sel="#fs3-nodes", kind="rise", t=2.5, d=0.4, to=1),
    ]
    els = [("fs3-edges", "b0", "cfg edges", "dimmed"),
           ("fs3-nodes", "b0", "cfg nodes", "dimmed"),
           ("fs3-p1", "b1", "path", "undrawn"),
           ("fs3-lp1", "b1", "label", "hidden"),
           ("fs3-p2", "b2", "path", "undrawn"),
           ("fs3-lp2", "b2", "label", "hidden"),
           ("fs3-badge", "b2", "badge", "hidden"),
           ("fs3-lnote", "b2", "label", "hidden")]
    return "".join(b), tw, els


figure("s3", (W_A, H_A), fig_s3, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.8)],
       "McCabe CFG; the cfg is dim at b0, path P1 draws over it, path P2 draws, "
       "the CCN badge appears; the cfg reaches full strength at the end")

# --------------------------------------------------------------------------
# s4: lizard pipeline
# --------------------------------------------------------------------------
def fig_s4():
    b = []
    b.append(lines_box(60, 120, 680, 130,
                       ["каталог: cronie-1.5.7/src/*.c",
                        "lizard <dir> обходит каталог рекурсивно"],
                       fills=[TXT, MUT], gid="fs4-b1"))
    b.append(arrow([(400, 250), (400, 306)], "fs4-a1"))
    b.append(lines_box(60, 310, 680, 140,
                       ["lizard", "статический анализ, без сборки и запуска"],
                       fills=[OR, MUT], stroke=OR, gid="fs4-b2"))
    b.append(arrow([(400, 450), (400, 506)], "fs4-a2"))
    b.append(lines_box(60, 510, 680, 140,
                       ["таблица", "CCN и NLOC, сортировка по CCN"],
                       fills=[TXT, MUT], gid="fs4-b3"))
    rows = [("child_process", "84", "324"), ("load_env", "31", "88"),
            ("cron_popen", "27", "88")]
    t = [R(80, 672, 640, 200, rx=12, fill=BG),
         T(112, 710, "функция", size=24, anchor="start", fill=OR),
         T(560, 710, "CCN", size=24, anchor="end", fill=OR),
         T(700, 710, "NLOC", size=24, anchor="end", fill=OR),
         f'<line x1="92" y1="724" x2="708" y2="724" stroke="{LINE}" stroke-width="2"/>']
    for i, (f_, c, n) in enumerate(rows):
        y = 762 + i * 42
        t.append(T(112, y, f_, size=24, anchor="start"))
        t.append(T(560, y, c, size=24, anchor="end"))
        t.append(T(700, y, n, size=24, anchor="end"))
    b.append('<g id="fs4-tbl">' + "".join(t) + "</g>")
    tw = [
        dict(sel="#fs4-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs4-b1", kind="rise", t=0.8, d=0.5),
        dict(sel="#fs4-b2", kind="rise", t=2.0, d=0.5),
        dict(sel="#fs4-a1", kind="draw", t=2.05, d=0.45),
        dict(sel="#fs4-b3", kind="rise", t=3.2, d=0.5),
        dict(sel="#fs4-a2", kind="draw", t=3.25, d=0.45),
        dict(sel="#fs4-tbl", kind="rise", t=3.4, d=0.45),
    ]
    els = [("fs4-b1", "b1", "stage", "dimmed"), ("fs4-a1", "b2", "arrow", "undrawn"),
           ("fs4-b2", "b2", "stage", "dimmed"), ("fs4-a2", "b3", "arrow", "undrawn"),
           ("fs4-b3", "b3", "stage", "dimmed"), ("fs4-tbl", "b3", "table", "hidden")]
    return "".join(b), tw, els


figure("s4", (W_A, H_A), fig_s4, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "three stage pipeline (catalogue, lizard, table) plus a three row excerpt")

# --------------------------------------------------------------------------
# s5: CCN bar chart
# --------------------------------------------------------------------------
def fig_s5():
    rows = [("child_process", 84, OR), ("load_entry", 67, OR),
            ("parse_args", 54, OR), ("edit_cmd", 52, OR), ("main", 50, OR),
            ("load_env", 31, ROSE), ("cron_popen", 27, OR),
            ("load_user", 25, OR)]
    b = []
    x0, sx = 270, 4.0
    top, step, hgt = 96, 84, 42
    b.append(f'<line x1="{x0}" y1="{top-12}" x2="{x0}" y2="{top+8*step+4}" '
             f'stroke="{LINE}" stroke-width="2"/>')
    for i, (name, v, col) in enumerate(rows):
        y = top + i * step
        b.append(T(x0 - 16, y + hgt * 0.7, name, size=25, anchor="end",
                   gid=f"fs5-l{i}"))
        w = v * sx
        b.append(f'<rect id="fs5-b{i}" x="{x0 + 2}" y="{y}" width="{w}" '
                 f'height="{hgt}" rx="4" fill="{col}"/>')
        b.append(T(x0 + w - 14, y + hgt * 0.7, str(v), size=24, fill=BG,
                   anchor="end", gid=f"fs5-v{i}", weight=700))
    axy = top + 8 * step + 12
    ax = []
    ax.append(f'<line x1="{x0}" y1="{axy}" x2="{x0+90*sx}" y2="{axy}" '
              f'stroke="{LINE}" stroke-width="2"/>')
    for tick in (0, 30, 60, 90):
        x = x0 + tick * sx
        ax.append(f'<line x1="{x}" y1="{axy}" x2="{x}" y2="{axy+10}" '
                  f'stroke="{LINE}" stroke-width="2"/>')
        ax.append(T(x, axy + 38, str(tick), size=24, fill=MUT))
    b.append('<g id="fs5-axis">' + "".join(ax) + "</g>")
    b.append(T(x0 + 31 * sx + 20, top + 5 * step + hgt * 0.7, "выбор", size=26,
               fill=ROSE, anchor="start", gid="fs5-selected"))
    b.append(T(x0 + 84 * sx + 20, top + hgt * 0.7, "отклонён", size=26, fill=MUT,
               anchor="start", gid="fs5-rejected"))
    tw = [
        dict(sel="#fs5-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs5-axis", kind="rise", t=0.05, d=0.5),
    ]
    for i in range(8):
        tw.append(dict(sel=f"#fs5-l{i}", kind="rise", t=0.15, d=0.4))
    for i in range(4):
        tw.append(dict(sel=f"#fs5-b{i}", kind="grow", t=0.85 + 0.16 * i, d=0.6))
        tw.append(dict(sel=f"#fs5-v{i}", kind="rise", t=1.35 + 0.16 * i, d=0.35))
    for i in range(4, 8):
        tw.append(dict(sel=f"#fs5-b{i}", kind="grow", t=2.05 + 0.16 * (i - 4), d=0.6))
        tw.append(dict(sel=f"#fs5-v{i}", kind="rise", t=2.55 + 0.16 * (i - 4), d=0.35))
    tw.append(dict(sel="#fs5-selected", kind="rise", t=2.7, d=0.4))
    tw.append(dict(sel="#fs5-rejected", kind="rise", t=1.5, d=0.4))
    els = [("fs5-axis", "b0", "axis", "dimmed")] + \
          [(f"fs5-l{i}", "b0", "label", "dimmed") for i in range(8)] + \
          [(f"fs5-b{i}", "b1" if i < 4 else "b2", "bar", "zero width")
           for i in range(8)] + \
          [(f"fs5-v{i}", "b1" if i < 4 else "b2", "value", "hidden")
           for i in range(8)] + \
          [("fs5-selected", "b2", "label", "hidden"),
           ("fs5-rejected", "b1", "label", "hidden")]
    return "".join(b), tw, els


figure("s5", (W_A, H_A), fig_s5, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.8)],
       "eight CCN bars, top four grow first, then the bottom four; load_env "
       "carries the rose accent and the label «выбор»")

# --------------------------------------------------------------------------
# s6: funnel of three stages
# --------------------------------------------------------------------------
def fig_s6():
    b = []
    b.append(lines_box(80, 130, 640, 160,
                       ["8 функций cronie", "CCN от 25 до 84"],
                       fills=[TXT, MUT], gid="fs6-b1"))
    b.append(arrow([(400, 292), (400, 348)], "fs6-a1"))
    b.append(T(420, 330, "CCN", size=25, fill=OR, anchor="start", gid="fs6-lccn"))
    b.append(lines_box(130, 350, 540, 160,
                       ["5 критериев выбора", "достижимость и воспроизводимость"],
                       fills=[TXT, MUT], stroke=OR, gid="fs6-b2"))
    b.append(arrow([(400, 512), (400, 578)], "fs6-a2"))
    b.append(pill(200, 585, 400, 96, "load_env: CCN 31", size=28, fill=SURF,
                  txt=TXT, stroke=ROSE, gid="fs6-b3"))
    b.append(T(400, 756, "парсер без exec и файлов", size=25, fill=MUT,
               gid="fs6-lnote"))
    tw = [
        dict(sel="#fs6-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs6-b1", kind="rise", t=0.8, d=0.5),
        dict(sel="#fs6-lccn", kind="rise", t=2.0, d=0.4),
        dict(sel="#fs6-a1", kind="draw", t=2.05, d=0.45),
        dict(sel="#fs6-b2", kind="rise", t=2.15, d=0.5),
        dict(sel="#fs6-a2", kind="draw", t=3.2, d=0.45),
        dict(sel="#fs6-b3", kind="rise", t=3.3, d=0.5),
        dict(sel="#fs6-lnote", kind="rise", t=3.45, d=0.4),
    ]
    els = [("fs6-b1", "b1", "stage", "dimmed"), ("fs6-lccn", "b2", "label", "hidden"),
           ("fs6-a1", "b2", "arrow", "undrawn"), ("fs6-b2", "b2", "stage", "dimmed"),
           ("fs6-a2", "b3", "arrow", "undrawn"), ("fs6-b3", "b3", "result", "hidden"),
           ("fs6-lnote", "b3", "label", "hidden")]
    return "".join(b), tw, els


figure("s6", (W_A, H_A), fig_s6, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "funnel: 8 functions by CCN, then the five criteria, then the single choice")

# --------------------------------------------------------------------------
# s7: two panel comparison
# --------------------------------------------------------------------------
def fig_s7():
    b = []
    b.append('<g id="fs7-left">'
             + R(30, 80, 350, 660, rx=18)
             + T(205, 128, "child_process", size=27, weight=700)
             + T(205, 164, "do_command.c", size=24, fill=MUT)
             + "</g>")
    b.append('<g id="fs7-cross" stroke="' + ROSE + '" stroke-width="6" '
             'stroke-linecap="round">'
             + '<line x1="140" y1="480" x2="270" y2="600"/>'
             + '<line x1="270" y1="480" x2="140" y2="600"/></g>')
    b.append('<g id="fs7-lchips">'
             + chip(58, 188, 294, 70, "CCN 84", gid="fs7-lc0")
             + chip(58, 266, 294, 70, "spawn и exec", gid="fs7-lc1")
             + chip(58, 344, 294, 70, "записи файлов", gid="fs7-lc2")
             + pill(78, 626, 254, 64, "отклонён", size=26, fill=SURF, txt=ROSE,
                    stroke=ROSE, gid="fs7-lbadge")
             + "</g>")
    b.append('<g id="fs7-right">'
             + R(420, 80, 350, 660, rx=18, stroke=OR, sw=3)
             + T(595, 128, "load_env", size=27, weight=700)
             + T(595, 164, "env.c:181", size=24, fill=MUT)
             + chip(448, 188, 294, 70, "CCN 31", gid="fs7-rc0", stroke=OR)
             + chip(448, 266, 294, 70, "поток как FILE*", gid="fs7-rc1", stroke=OR)
             + chip(448, 344, 294, 70, ["без побочных", "эффектов"],
                    gid="fs7-rc2", stroke=OR)
             + chip(448, 422, 294, 70, "конечный автомат", gid="fs7-rc3", stroke=OR)
             + pill(468, 626, 254, 64, "выбор", size=26, fill=ROSE, txt=BG,
                    gid="fs7-rbadge")
             + "</g>")
    b.append(R(30, 80, 350, 660, rx=18, fill=BG, stroke="none", sw=0,
               opa="0", gid="fs7-veil"))
    b.append(R(412, 72, 366, 676, rx=22, fill="none", stroke=ROSE, sw=4,
               opa="0", gid="fs7-hl"))
    tw = [
        dict(sel="#fs7-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs7-left", kind="rise", t=0.8, d=0.5),
        dict(sel="#fs7-lchips", kind="rise", t=0.85, d=0.5),
        dict(sel="#fs7-right", kind="rise", t=2.0, d=0.5),
        dict(sel="#fs7-veil", kind="rise", t=3.2, d=0.5, to=0.55),
        dict(sel="#fs7-cross", kind="rise", t=3.3, d=0.5),
        dict(sel="#fs7-hl", kind="rise", t=3.45, d=0.5),
    ]
    els = [("fs7-left", "b1", "panel", "dimmed"),
           ("fs7-lchips", "b1", "chips", "dimmed"),
           ("fs7-lbadge", "b1", "badge", "dimmed"),
           ("fs7-right", "b2", "panel", "dimmed"),
           ("fs7-rbadge", "b2", "badge", "dimmed"),
           ("fs7-veil", "b3", "overlay", "transparent"),
           ("fs7-cross", "b3", "mark", "hidden"),
           ("fs7-hl", "b3", "highlight", "hidden")]
    return "".join(b), tw, els


figure("s7", (W_A, H_A), fig_s7, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "comparison panels; the verdict beat veils and crosses the left panel "
       "and puts a rose frame around the right one")

# --------------------------------------------------------------------------
# s8: wrapper anatomy, four boxes
# --------------------------------------------------------------------------
def fig_s8():
    b = []
    b.append(lines_box(120, 110, 560, 110,
                       ["байты (вход)", "то, что даёт фаззер"],
                       fills=[TXT, MUT], gid="fs8-b1"))
    b.append(arrow([(400, 226), (400, 282)], "fs8-a1"))
    b.append(lines_box(100, 290, 600, 150,
                       ["обёртка: transform", "FILE* через fmemopen"],
                       fills=[OR, MUT], stroke=OR, gid="fs8-b2"))
    b.append(arrow([(400, 446), (400, 502)], "fs8-a2"))
    b.append(lines_box(140, 510, 520, 150,
                       ["цель: load_env", "разбор NAME=VALUE"],
                       fills=[TXT, MUT], gid="fs8-b3"))
    b.append(arrow([(400, 666), (400, 722)], "fs8-a3"))
    b.append(lines_box(250, 726, 300, 110, ["return 0", "успех"],
                       fills=[TXT, MUT], gid="fs8-b4"))
    tw = [
        dict(sel="#fs8-all", kind="wrap", t=0, d=0.5),
        dict(sel="#fs8-b1", kind="rise", t=0.8, d=0.5),
        dict(sel="#fs8-a1", kind="draw", t=2.0, d=0.45),
        dict(sel="#fs8-b2", kind="rise", t=2.05, d=0.5),
        dict(sel="#fs8-a2", kind="draw", t=3.2, d=0.45),
        dict(sel="#fs8-b3", kind="rise", t=3.25, d=0.5),
        dict(sel="#fs8-a3", kind="draw", t=4.4, d=0.45),
        dict(sel="#fs8-b4", kind="rise", t=4.45, d=0.5),
    ]
    els = [("fs8-b1", "b1", "stage", "dimmed"), ("fs8-a1", "b2", "arrow", "undrawn"),
           ("fs8-b2", "b2", "stage", "dimmed"), ("fs8-a2", "b3", "arrow", "undrawn"),
           ("fs8-b3", "b3", "stage", "dimmed"), ("fs8-a3", "b4", "arrow", "undrawn"),
           ("fs8-b4", "b4", "stage", "dimmed")]
    return "".join(b), tw, els


figure("s8", (W_A, H_A), fig_s8, 6.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.4),
        ("b4", 4.4, 6.0)],
       "four step flow, one box and one arrow per beat, the flow closes at b4")

# --------------------------------------------------------------------------
# s9 / s10: 2x2 guard grid
# --------------------------------------------------------------------------
def grid4(key, items, accent, extra=""):
    b = []
    cells = [(40, 120), (415, 120), (40, 470), (415, 470)]
    for i, ((x, y), (num, title, body)) in enumerate(zip(cells, items)):
        b.append('<g id="%s-c%d">' % (key, i + 1)
                 + R(x, y, 345, 310, rx=18)
                 + T(x + 26, y + 76, num, size=54, fill=accent, anchor="start",
                     weight=700)
                 + T(x + 26, y + 130, title, size=26, anchor="start", weight=700)
                 + "".join(T(x + 26, y + 186 + j * 34, ln, size=24, anchor="start",
                             fill=MUT) for j, ln in enumerate(body))
                 + "</g>")
    if extra:
        b.append(extra)
    tw = [dict(sel=f"#{key}-all", kind="wrap", t=0, d=0.5)]
    for i in range(4):
        tw.append(dict(sel=f"#{key}-c{i+1}", kind="rise", t=0.8 + 1.2 * i, d=0.5))
    els = [(f"{key}-c{i+1}", f"b{i+1}", "card", "dimmed") for i in range(4)]
    return "".join(b), tw, els


def fig_s9():
    items = [("1", "Простота", ["байты, форма,", "цель, ноль", "без логирования"]),
             ("2", "Одна обёртка", ["одна цель:", "один сценарий", "на файл"]),
             ("3", "Детерминированность", ["LineNumber = 0,", "без exit,", "файлов и сети"]),
             ("4", "Проверки до вызова", ["ранний возврат", "на пустом и", "большом входе"])]
    return grid4("fs9", items, OR)


figure("s9", (W_A, H_A), fig_s9, 6.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.4),
        ("b4", 4.4, 6.0)],
       "2x2 grid of principles 1 to 4, one card per beat")


def fig_s10():
    items = [("5", "Не перехватывать", ["только", "документированные", "ошибки"]),
             ("6", "Формат входа", ["fmemopen,", "FuzzedDataProvider,", "dispatch-байт"]),
             ("7", "Комментарий", ["цель, функция,", "формат входа,", "сборка, сиды"]),
             ("8", "Python-специфика", ["instrument_imports()", "до импорта цели,", "не в TestOneInput"])]
    return grid4("fs10", items, ROSE)


figure("s10", (W_A, H_A), fig_s10, 6.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.4),
        ("b4", 4.4, 6.0)],
       "2x2 grid of principles 5 to 8, one card per beat")


