"""figures s12 to s30"""
from figlib import *  # noqa: F401,F403


def panel(x, y, w, h, title, lines, accent=OR, gid=None, size=28):
    out = [R(x, y, w, h, rx=16, gid=gid)]
    out.append(T(x + 26, y + 52, title, size=size, anchor="start",
                 fill=accent, weight=700))
    for i, ln in enumerate(lines):
        out.append(T(x + 26, y + 96 + i * 32, ln, size=24, anchor="start",
                     fill=MUT))
    return "".join(out)


def twin_cols(key, left, right, chips, chip_h, chip_step, chip_y,
              accent_l=OR, accent_r=ROSE, head_h=64, notes=(None, None),
              t_right=2.2):
    """Two columns: a header pill and a stack of chips, one column per beat."""
    b = []
    left_note, right_note = notes
    b.append('<g id="%s-left">' % key)
    b.append(pill(30, 90, 350, head_h, left, size=28, fill=SURF, txt=accent_l,
                  stroke=accent_l, gid="%s-hl" % key))
    for i, t in enumerate(chips[0]):
        b.append(chip(40, chip_y + i * chip_step, 330, chip_h, t,
                      gid="%s-lc%d" % (key, i), stroke=accent_l))
    if left_note:
        for j, l in enumerate(left_note):
            b.append(T(205, chip_y + len(chips[0]) * chip_step + 30 + j * 34, l,
                       size=24, fill=MUT, gid="%s-ln%d" % (key, j)))
    b.append("</g>")
    b.append('<g id="%s-right">' % key)
    b.append(pill(420, 90, 350, head_h, right, size=28, fill=SURF, txt=accent_r,
                  stroke=accent_r, gid="%s-hr" % key))
    for i, t in enumerate(chips[1]):
        b.append(chip(430, chip_y + i * chip_step, 330, chip_h, t,
                      gid="%s-rc%d" % (key, i), stroke=accent_r))
    if right_note:
        for j, l in enumerate(right_note):
            b.append(T(585, chip_y + len(chips[1]) * chip_step + 30 + j * 34, l,
                       size=24, fill=MUT, gid="%s-rn%d" % (key, j)))
    b.append("</g>")
    tw = [dict(sel="#%s-all" % key, kind="wrap", t=0, d=0.5),
          dict(sel="#%s-left" % key, kind="rise", t=0.8, d=0.5),
          dict(sel="#%s-right" % key, kind="rise", t=t_right, d=0.5)]
    if left_note:
        tw += [dict(sel="#%s-ln%d" % (key, j), kind="rise",
                    t=1.4 + 0.1 * j, d=0.4) for j in range(len(left_note))]
    if right_note:
        tw += [dict(sel="#%s-rn%d" % (key, j), kind="rise",
                    t=t_right + 0.4 + 0.1 * j, d=0.4)
               for j in range(len(right_note))]
    els = [("%s-left" % key, "b1", "column", "dimmed"),
           ("%s-right" % key, "b2", "column", "dimmed")]
    els += [("%s-lc%d" % (key, i), "b1", "chip", "dimmed")
            for i in range(len(chips[0]))]
    els += [("%s-rc%d" % (key, i), "b2", "chip", "dimmed")
            for i in range(len(chips[1]))]
    return "".join(b), tw, els


# --------------------------------------------------------------------------
# s12: three technique panels
# --------------------------------------------------------------------------
def fig_s12():
    b = []
    b.append(panel(40, 90, 720, 220, "Dispatch-байт",
                   ["первый байт выбирает режим,", "остальные байты данные режима"],
                   OR, "fs12-p1"))
    b.append(chip(66, 232, 240, 56, "data[0] % 5", gid="fs12-c1", stroke=OR))
    b.append(panel(40, 360, 720, 220, "fmemopen()",
                   ["буфер фаззера становится FILE*,", "цель читает обычный поток"],
                   ROSE, "fs12-p2"))
    b.append(chip(66, 500, 150, 56, "буфер", gid="fs12-c2a"))
    b.append(arrow([(228, 528), (274, 528)], "fs12-a2", sw=3))
    b.append(chip(288, 500, 150, 56, "FILE*", gid="fs12-c2b", stroke=ROSE))
    b.append(panel(40, 630, 720, 200, "Структура",
                   ["поля читаются по порядку:"], OR, "fs12-p3"))
    for i, (t, x) in enumerate([("mode", 66), ("n: uint16", 260),
                                ("payload", 454)]):
        b.append(chip(x, 748, 180, 56, t, gid="fs12-s%d" % i, stroke=OR))
    tw = [dict(sel="#fs12-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs12-p1", kind="rise", t=0.8, d=0.5),
          dict(sel="#fs12-c1", kind="rise", t=1.05, d=0.45),
          dict(sel="#fs12-p2", kind="rise", t=2.0, d=0.5),
          dict(sel="#fs12-c2a", kind="rise", t=2.15, d=0.45),
          dict(sel="#fs12-a2", kind="draw", t=2.25, d=0.35),
          dict(sel="#fs12-c2b", kind="rise", t=2.35, d=0.45),
          dict(sel="#fs12-p3", kind="rise", t=3.2, d=0.5)]
    tw += [dict(sel="#fs12-s%d" % i, kind="rise", t=3.4 + 0.1 * i, d=0.45)
           for i in range(3)]
    els = [("fs12-p1", "b1", "panel", "dimmed"),
           ("fs12-c1", "b1", "chip", "hidden"),
           ("fs12-p2", "b2", "panel", "dimmed"),
           ("fs12-c2a", "b2", "chip", "hidden"),
           ("fs12-a2", "b2", "arrow", "undrawn"),
           ("fs12-c2b", "b2", "chip", "hidden"),
           ("fs12-p3", "b3", "panel", "dimmed")]
    els += [("fs12-s%d" % i, "b3", "segment", "hidden") for i in range(3)]
    return "".join(b), tw, els


figure("s12", (W_A, H_A), fig_s12, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "three technique panels, one per beat; the field scheme closes the third")

# --------------------------------------------------------------------------
# s13: stubs and include trick
# --------------------------------------------------------------------------
def fig_s13():
    b = []
    b.append(panel(40, 90, 720, 320, "Стабы",
                   ["зависимость заменяют поддельной",
                    "реализацией без побочных эффектов"], ROSE, "fs13-p1"))
    b.append(lines_box(70, 258, 260, 80, ["оригинальная цель"], size=24,
                       gid="fs13-b1"))
    b.append(arrow([(340, 298), (420, 298)], "fs13-a1"))
    b.append(lines_box(430, 258, 300, 80, ["стаб"], size=24, gid="fs13-b2"))
    b.append(panel(40, 440, 720, 380, "Include-trick",
                   ["static-функция попадает в нашу единицу",
                    "трансляции через подмену main"], ROSE, "fs13-p2"))
    b.append(lines_box(70, 580, 300, 80, ["api.c"], size=24, gid="fs13-b3"))
    b.append(chip(70, 648, 370, 96, ["#define main", "fuzz_original_main"],
                  gid="fs13-c1", stroke=ROSE))
    b.append(arrow([(380, 620), (452, 620)], "fs13-a2"))
    b.append(lines_box(462, 580, 268, 80, ["обёртка"], size=24, gid="fs13-b4"))
    b.append(T(70, 790, "«api.c» включается вместо заголовка", size=24,
               anchor="start", fill=MUT, gid="fs13-l1"))
    tw = [dict(sel="#fs13-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs13-p1", kind="rise", t=0.8, d=0.5),
          dict(sel="#fs13-b1", kind="rise", t=0.95, d=0.45),
          dict(sel="#fs13-a1", kind="draw", t=1.05, d=0.4),
          dict(sel="#fs13-b2", kind="rise", t=1.1, d=0.45),
          dict(sel="#fs13-p2", kind="rise", t=2.0, d=0.5),
          dict(sel="#fs13-b3", kind="rise", t=2.1, d=0.45),
          dict(sel="#fs13-c1", kind="rise", t=2.2, d=0.45),
          dict(sel="#fs13-a2", kind="draw", t=2.3, d=0.4),
          dict(sel="#fs13-b4", kind="rise", t=2.35, d=0.45),
          dict(sel="#fs13-l1", kind="rise", t=2.45, d=0.4)]
    els = [("fs13-p1", "b1", "panel", "dimmed"),
           ("fs13-b1", "b1", "box", "dimmed"),
           ("fs13-a1", "b1", "arrow", "undrawn"),
           ("fs13-b2", "b1", "box", "dimmed"),
           ("fs13-p2", "b2", "panel", "dimmed"),
           ("fs13-b3", "b2", "box", "dimmed"),
           ("fs13-c1", "b2", "chip", "hidden"),
           ("fs13-a2", "b2", "arrow", "undrawn"),
           ("fs13-b4", "b2", "box", "dimmed"),
           ("fs13-l1", "b2", "label", "hidden")]
    return "".join(b), tw, els


figure("s13", (W_A, H_A), fig_s13, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.8)],
       "stubs panel, then the include trick panel")

# --------------------------------------------------------------------------
# s14: two samples
# --------------------------------------------------------------------------
def fig_s14():
    chips = ([["NUL заменяются", "пробелами"],
              ["вход не больше", "1024 байт"],
              ["#undef unused"],
              ["один файл", "на все фаззеры"]],
             [["fmemopen()", "даёт FILE*"],
              ["LineNumber = 0"],
              ["#define MAIN_PROGRAM"],
              ["статический буфер", "envstr"]])
    body, tw, els = twin_cols("fs14", "sgetpwent", "load_env", chips, 110, 150, 190)
    body += T(400, 822, "общее правило: один файл обёртки на все фаззеры",
              size=24, fill=MUT, gid="fs14-note")
    tw.append(dict(sel="#fs14-note", kind="rise", t=3.4, d=0.4))
    els.append(("fs14-note", "b2", "note", "hidden"))
    return body, tw, els


figure("s14", (W_A, H_A), fig_s14, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.2), ("b2", 2.2, 4.8)],
       "two sample panels side by side, four chips each")

# --------------------------------------------------------------------------
# s15: two build columns
# --------------------------------------------------------------------------
def build_col(key, x, name, comp, flags, chips_, binary, accent):
    out = [pill(x, 90, 350, 64, name, size=28, fill=SURF, txt=accent,
                stroke=accent, gid=key + "-h")]
    out.append(chip(x, 180, 350, 110, [comp] + flags, gid=key + "-c0",
                    stroke=accent, color=TXT))
    for i, t in enumerate(chips_):
        out.append(chip(x, 316 + i * 76, 350, 62, t, gid=key + "-c%d" % (i + 1)))
    out.append(arrow([(x + 175, 546), (x + 175, 596)], key + "-a"))
    out.append(chip(x, 604, 350, 74, binary, gid=key + "-bin", stroke=accent,
                    color=accent))
    return "".join(out)


def fig_s15():
    b = [build_col("fs15-l", 30, "libFuzzer", "clang",
                   ["-fsanitize=fuzzer,address", "-g -O1"],
                   ["битмап", "main", "ASan"], "fuzz_load_env_lf", OR),
         build_col("fs15-r", 420, "AFL", "afl-clang-fast", ["-g -O1"],
                   ["битмап 64K", "fork-сервер", "__AFL_LOOP"],
                   "fuzz_load_env_afl", ROSE)]
    b.append(T(400, 790, "битмапы AFL и libFuzzer несовместимы",
               size=24, fill=MUT, gid="fs15-note"))
    tw = [dict(sel="#fs15-all", kind="wrap", t=0, d=0.5)]
    for sel in ("#fs15-l", "#fs15-r"):
        pass
    tw += [dict(sel="#fs15-l-h", kind="rise", t=0.8, d=0.45),
           dict(sel="#fs15-l-c0", kind="rise", t=0.9, d=0.45)]
    tw += [dict(sel="#fs15-l-c%d" % i, kind="rise", t=1.0 + 0.1 * i, d=0.4)
           for i in range(1, 4)]
    tw += [dict(sel="#fs15-l-a", kind="draw", t=1.3, d=0.4),
           dict(sel="#fs15-l-bin", kind="rise", t=1.45, d=0.45)]
    tw += [dict(sel="#fs15-r-h", kind="rise", t=2.2, d=0.45),
           dict(sel="#fs15-r-c0", kind="rise", t=2.3, d=0.45)]
    tw += [dict(sel="#fs15-r-c%d" % i, kind="rise", t=2.4 + 0.1 * i, d=0.4)
           for i in range(1, 4)]
    tw += [dict(sel="#fs15-r-a", kind="draw", t=2.7, d=0.4),
           dict(sel="#fs15-r-bin", kind="rise", t=2.85, d=0.45)]
    els = [("fs15-l-h", "b1", "header", "dimmed"),
           ("fs15-l-c0", "b1", "box", "dimmed"),
           ("fs15-l-bin", "b1", "binary", "dimmed"),
           ("fs15-r-h", "b2", "header", "dimmed"),
           ("fs15-r-c0", "b2", "box", "dimmed"),
           ("fs15-r-bin", "b2", "binary", "dimmed")]
    els += [("fs15-l-c%d" % i, "b1", "chip", "dimmed") for i in range(1, 4)]
    els += [("fs15-r-c%d" % i, "b2", "chip", "dimmed") for i in range(1, 4)]
    tw.append(dict(sel="#fs15-note", kind="rise", t=3.2, d=0.45))
    els.append(("fs15-note", "b2", "note", "hidden"))
    return "".join(b), tw, els


figure("s15", (W_A, H_A), fig_s15, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.2), ("b2", 2.2, 4.8)],
       "two build columns: compiler box, instrumentation chips, binary")

# --------------------------------------------------------------------------
# s16: cronie build pipeline with dropped dependencies and two errors
# --------------------------------------------------------------------------
def fig_s16():
    b = []
    b.append(lines_box(60, 80, 680, 140, ["cronie 1.5.7",
                                          "автоtools, PAM, selinux, inotify"],
                       fills=[TXT, MUT], gid="fs16-b1"))
    b.append('<g id="fs16-deps">')
    for i, t in enumerate(["autotools", "PAM", "selinux", "inotify"]):
        b.append(chip(60 + i * 172, 246, 156, 60, t, gid="fs16-d%d" % i))
    b.append("</g>")
    b.append('<g id="fs16-strike" stroke="' + ROSE + '" stroke-width="3" '
             'stroke-linecap="round">')
    for i in range(4):
        x = 60 + i * 172
        b.append('<line x1="%d" y1="252" x2="%d" y2="300"/>' % (x + 8, x + 148))
    b.append("</g>")
    b.append(arrow([(400, 318), (400, 372)], "fs16-a1"))
    b.append(lines_box(60, 384, 680, 150,
                       ["фильтр: env.c, misc.c, pw_dup.c",
                        "и обёртка, обходим автоtools"],
                       fills=[OR, MUT], stroke=OR, gid="fs16-b2"))
    b.append(arrow([(400, 540), (400, 596)], "fs16-a2"))
    b.append(lines_box(250, 602, 300, 90, ["fuzz-target"], gid="fs16-b3"))
    b.append('<g id="fs16-e1">' + chip(40, 736, 340, 116,
                                      ["undefined LineNumber",
                                       "#define MAIN_PROGRAM"],
                                      gid="fs16-e1i", stroke=ROSE, color=ROSE)
             + "</g>")
    b.append('<g id="fs16-e2">' + chip(420, 736, 340, 116,
                                       ["undefined unused", "#undef unused"],
                                       gid="fs16-e2i", stroke=ROSE, color=ROSE)
             + "</g>")
    tw = [dict(sel="#fs16-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs16-b1", kind="rise", t=0.8, d=0.5),
          dict(sel="#fs16-deps", kind="sink", t=1.9, d=0.5, to=0.3),
          dict(sel="#fs16-strike", kind="rise", t=2.0, d=0.45, to=0.6),
          dict(sel="#fs16-a1", kind="draw", t=2.05, d=0.4),
          dict(sel="#fs16-b2", kind="rise", t=2.1, d=0.5),
          dict(sel="#fs16-a2", kind="draw", t=3.2, d=0.4),
          dict(sel="#fs16-b3", kind="rise", t=3.25, d=0.5),
          dict(sel="#fs16-e1", kind="rise", t=3.35, d=0.45),
          dict(sel="#fs16-e2", kind="rise", t=3.45, d=0.45)]
    els = [("fs16-b1", "b1", "box", "dimmed"),
           ("fs16-deps", "b1", "dropped", "dimmed"),
           ("fs16-strike", "b2", "mark", "hidden"),
           ("fs16-a1", "b2", "arrow", "undrawn"),
           ("fs16-b2", "b2", "box", "dimmed"),
           ("fs16-a2", "b3", "arrow", "undrawn"),
           ("fs16-b3", "b3", "box", "dimmed"),
           ("fs16-e1", "b3", "error badge", "hidden"),
           ("fs16-e2", "b3", "error badge", "hidden")]
    return "".join(b), tw, els


figure("s16", (W_A, H_A), fig_s16, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "cronie box, four dropped dependencies crossed out, filter box, target "
       "and two error badges with their fixes")

# --------------------------------------------------------------------------
# s17: seeds, corpus, fuzzer
# --------------------------------------------------------------------------
def fig_s17():
    b = []
    seeds = [("seed1", ["SHELL=, PATH=", "строка задания"]),
             ("seed2", ["MAILTO=", "и /usr/bin/true"]),
             ("seed3", ["FOO=\"a b c\"", "BAR=12345"])]
    for i, (t, ls) in enumerate(seeds):
        x = 40 + i * 250
        b.append('<g id="fs17-s%d">' % (i + 1)
                 + R(x, 90, 220, 180, rx=16)
                 + T(x + 110, 138, t, size=26, weight=700, fill=OR)
                 + "".join(T(x + 110, 190 + j * 34, ln, size=24, fill=MUT)
                           for j, ln in enumerate(ls))
                 + "</g>")
        b.append(arrow([(x + 110, 276), (x + 110, 352)], "fs17-as%d" % (i + 1)))
    b.append(lines_box(140, 358, 520, 130, ["corpus", "3 файла"],
                       fills=[TXT, MUT], stroke=OR, gid="fs17-corpus"))
    b.append(arrow([(400, 494), (400, 546)], "fs17-ac"))
    b.append(lines_box(210, 552, 380, 100, ["afl-fuzz"], gid="fs17-fuzz"))
    b.append(R(120, 700, 560, 84, rx=42, fill=SURF, stroke=ROSE, sw=2,
               dash="10 8", gid="fs17-note"))
    b.append(T(400, 752, "добавить 1 или 2 файла", size=26, fill=ROSE,
               gid="fs17-notetxt"))
    tw = [dict(sel="#fs17-all", kind="wrap", t=0, d=0.5)]
    for i in range(3):
        tw.append(dict(sel="#fs17-s%d" % (i + 1), kind="rise", t=0.8 + 0.15 * i, d=0.45))
    for i in range(3):
        tw.append(dict(sel="#fs17-as%d" % (i + 1), kind="draw", t=2.0 + 0.1 * i, d=0.4))
    tw.append(dict(sel="#fs17-corpus", kind="rise", t=2.05, d=0.5))
    tw.append(dict(sel="#fs17-ac", kind="draw", t=3.2, d=0.4))
    tw.append(dict(sel="#fs17-fuzz", kind="rise", t=3.25, d=0.5))
    tw.append(dict(sel="#fs17-note", kind="rise", t=3.4, d=0.45))
    tw.append(dict(sel="#fs17-notetxt", kind="rise", t=3.45, d=0.45))
    els = [("fs17-s%d" % (i + 1), "b1", "seed", "dimmed") for i in range(3)]
    els += [("fs17-as%d" % (i + 1), "b2", "arrow", "undrawn") for i in range(3)]
    els += [("fs17-corpus", "b2", "corpus", "dimmed"),
            ("fs17-ac", "b3", "arrow", "undrawn"),
            ("fs17-fuzz", "b3", "fuzzer", "dimmed"),
            ("fs17-note", "b3", "badge", "hidden"),
            ("fs17-notetxt", "b3", "label", "hidden")]
    return "".join(b), tw, els


figure("s17", (W_A, H_A), fig_s17, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "three seeds feed the corpus, the corpus feeds the fuzzer, a dashed badge "
       "asks for one or two more files")

# --------------------------------------------------------------------------
# s18 / s20: command anatomy
# --------------------------------------------------------------------------
def fig_s18():
    rows = [(["AFL_I_DONT_CARE_ABOUT_", "MISSING_CRASHES=1"],
             ["согласие с", "окружением"], 90, 90),
            (["afl-fuzz"], ["драйвер AFL++"], 200, 60),
            (["-i corpus"], ["входной корпус"], 280, 60),
            (["-o out"], ["результаты:", "out/default/"], 360, 60),
            (["-V 20"], ["время фаззинга,", "секунд"], 440, 60),
            (["./fuzz_load_env_afl"], ["бинарник"], 520, 60)]
    b = []
    for i, (tok, ann, y, h) in enumerate(rows):
        b.append(chip(40, y, 390, h, tok, size=24, gid="fs18-p%d" % i,
                      stroke=OR if i == 1 else LINE,
                      color=TXT if i != 1 else OR))
        b.append('<g id="fs18-a%d">' % i
                 + "".join(T(460, y + h / 2 - (len(ann) - 1) * 16 + 8 + j * 32, l,
                             size=24, anchor="start", fill=MUT)
                           for j, l in enumerate(ann))
                 + "</g>")
    chips_ = ["queue/", "crashes/", "hangs/", "fuzzer_stats"]
    for i, t in enumerate(chips_):
        b.append(chip(40 + i * 183, 656, 165, 66, t, gid="fs18-k%d" % i,
                      stroke=ROSE if i == 1 else LINE,
                      color=ROSE if i == 1 else TXT))
    tw = [dict(sel="#fs18-all", kind="wrap", t=0, d=0.5)]
    tw += [dict(sel="#fs18-p%d" % i, kind="rise", t=0.8 + 0.12 * i, d=0.35)
           for i in range(6)]
    tw += [dict(sel="#fs18-a%d" % i, kind="rise", t=2.0 + 0.1 * i, d=0.4)
           for i in range(6)]
    tw += [dict(sel="#fs18-k%d" % i, kind="rise", t=3.2 + 0.1 * i, d=0.4)
           for i in range(4)]
    els = [("fs18-p%d" % i, "b1", "token", "dimmed") for i in range(6)]
    els += [("fs18-a%d" % i, "b2", "annotation", "hidden") for i in range(6)]
    els += [("fs18-k%d" % i, "b3", "artifact chip", "hidden") for i in range(4)]
    return "".join(b), tw, els


figure("s18", (W_A, H_A), fig_s18, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "six command tokens appear left to right, then their annotations, then "
       "the four artifact chips")

# --------------------------------------------------------------------------
# s19: AFL coverage bar
# --------------------------------------------------------------------------
def fig_s19():
    b = []
    b.append('<g id="fs19-track">'
             + R(60, 320, 680, 80, rx=40, fill=SURF)
             + "".join('<line x1="%d" y1="320" x2="%d" y2="400" stroke="%s" '
                       'stroke-width="2"/>' % (x, x, LINE)
                       for x in (230, 400, 570))
             + "".join(T(x, 436, s, size=24, fill=MUT)
                       for x, s in ((230, "25%"), (400, "50%"), (570, "75%")))
             + T(60, 436, "0", size=24, fill=MUT)
             + T(740, 436, "331", size=24, fill=MUT)
             + "</g>")
    b.append('<g id="fs19-fill">'
             + R(60, 320, 113, 80, rx=40, fill=OR, stroke=OR, gid="fs19-bar")
             + "</g>")
    b.append(pill(96, 200, 320, 66, "edges 55 из 331", size=26, fill=SURF,
                  txt=OR, stroke=OR, gid="fs19-badge"))
    b.append(arrow([(173, 272), (173, 316)], "fs19-lead", sw=2.5))
    b.append(T(440, 246, "bitmap_cvg 16.62%", size=25, anchor="start", fill=MUT,
               gid="fs19-pct"))
    b.append('<g id="fs19-m1">' + R(60, 560, 330, 124, rx=16)
             + T(88, 616, "stability", size=24, anchor="start", fill=MUT)
             + T(88, 662, "98.18%", size=32, anchor="start", fill=OR, weight=700)
             + "</g>")
    b.append('<g id="fs19-m2">' + R(410, 560, 330, 124, rx=16)
             + T(438, 616, "saved_crashes", size=24, anchor="start", fill=MUT)
             + T(438, 662, "0", size=32, anchor="start", fill=OR, weight=700)
             + "</g>")
    b.append(T(400, 770, "1.70M исполнений за 20 секунд", size=25, fill=MUT,
               gid="fs19-exec"))
    tw = [dict(sel="#fs19-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs19-track", kind="rise", t=0.05, d=0.5),
          dict(sel="#fs19-bar", kind="grow", t=0.85, d=0.9),
          dict(sel="#fs19-badge", kind="rise", t=2.1, d=0.45),
          dict(sel="#fs19-lead", kind="draw", t=2.2, d=0.35),
          dict(sel="#fs19-pct", kind="rise", t=2.25, d=0.45),
          dict(sel="#fs19-m1", kind="rise", t=3.2, d=0.45),
          dict(sel="#fs19-m2", kind="rise", t=3.3, d=0.45),
          dict(sel="#fs19-exec", kind="rise", t=3.45, d=0.45)]
    els = [("fs19-track", "b0", "track", "dimmed"),
           ("fs19-bar", "b1", "fill", "zero width"),
           ("fs19-badge", "b2", "badge", "hidden"),
           ("fs19-lead", "b2", "leader", "undrawn"),
           ("fs19-pct", "b2", "label", "hidden"),
           ("fs19-m1", "b3", "metric", "hidden"),
           ("fs19-m2", "b3", "metric", "hidden"),
           ("fs19-exec", "b3", "note", "hidden")]
    return "".join(b), tw, els


figure("s19", (W_A, H_A), fig_s19, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "coverage track with 25/50/75 marks, the fill grows to 55 of 331 edges, "
       "then the stability and saved_crashes badges")

# --------------------------------------------------------------------------
# s20: libFuzzer command anatomy
# --------------------------------------------------------------------------
def fig_s20():
    rows = [(["./fuzz_load_env_lf"], ["бинарник с ASan"], 90),
            (["corpus/"], ["стартовый корпус"], 170),
            (["-max_len=4096"], ["предел длины входа"], 250),
            (["-runs=200000"], ["число прогонов"], 330),
            (["-print_final_stats"], ["итоговая статистика"], 410)]
    b = []
    for i, (tok, ann, y) in enumerate(rows):
        b.append(chip(40, y, 390, 60, tok, size=24, gid="fs20-p%d" % i,
                      stroke=OR if i == 3 else LINE,
                      color=OR if i == 3 else TXT))
        b.append(T(460, y + 38, ann[0], size=24, anchor="start", fill=MUT,
                   gid="fs20-a%d" % i))
    b.append(arrow([(235, 490), (235, 566)], "fs20-lead", sw=2.5))
    b.append('<g id="fs20-done">'
             + pill(60, 572, 350, 78, "DONE", size=30, fill=ROSE, txt=BG,
                    gid="fs20-donei")
             + "</g>")
    b.append(T(60, 726, "строка DONE печатается по -print_final_stats",
               size=24, anchor="start", fill=MUT, gid="fs20-note"))
    tw = [dict(sel="#fs20-all", kind="wrap", t=0, d=0.5)]
    tw += [dict(sel="#fs20-p%d" % i, kind="rise", t=0.8 + 0.12 * i, d=0.35)
           for i in range(5)]
    tw += [dict(sel="#fs20-a%d" % i, kind="rise", t=2.0 + 0.1 * i, d=0.4)
           for i in range(5)]
    tw += [dict(sel="#fs20-lead", kind="draw", t=3.2, d=0.35),
           dict(sel="#fs20-done", kind="rise", t=3.25, d=0.45),
           dict(sel="#fs20-note", kind="rise", t=3.45, d=0.4)]
    els = [("fs20-p%d" % i, "b1", "token", "dimmed") for i in range(5)]
    els += [("fs20-a%d" % i, "b2", "annotation", "hidden") for i in range(5)]
    els += [("fs20-lead", "b3", "leader", "undrawn"),
            ("fs20-done", "b3", "badge", "hidden"),
            ("fs20-note", "b3", "label", "hidden")]
    return "".join(b), tw, els


figure("s20", (W_A, H_A), fig_s20, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "five libFuzzer tokens, their annotations, then the DONE badge")

# --------------------------------------------------------------------------
# s21 / s28: stat cards
# --------------------------------------------------------------------------
def stat_cards(key, cards, accent, y0=90, h=120, step=140, vsize=36):
    b = []
    for i, (val, lab) in enumerate(cards):
        y = y0 + i * step
        b.append('<g id="%s-c%d">' % (key, i + 1)
                 + R(50, y, 700, h, rx=16)
                 + T(82, y + 66, val, size=vsize, anchor="start", fill=accent,
                     weight=700, gid="%s-v%d" % (key, i + 1))
                 + T(82, y + 102, lab, size=24, anchor="start", fill=MUT)
                 + "</g>")
    tw = [dict(sel="#%s-all" % key, kind="wrap", t=0, d=0.5)]
    tw += [dict(sel="#%s-c%d" % (key, i + 1), kind="rise", t=0.8 + 0.12 * i,
                d=0.4) for i in range(len(cards))]
    tw += [dict(sel="#%s-v%d" % (key, i + 1), kind="rise", t=2.0 + 0.1 * i,
                d=0.4) for i in range(len(cards))]
    els = [("%s-c%d" % (key, i + 1), "b1", "card", "dimmed")
           for i in range(len(cards))]
    els += [("%s-v%d" % (key, i + 1), "b2", "value", "hidden")
            for i in range(len(cards))]
    return "".join(b), tw, els


def fig_s21():
    cards = [("cov 47", "покрытые блоки и пути"), ("ft 164", "новые точки"),
             ("corp 77/2080b", "файлы и байты корпуса"),
             ("lim 1788", "лимит длины, растёт сам"),
             ("exec/s 0", "скорость в конце прогона")]
    return stat_cards("fs21", cards, OR, y0=80, h=120, step=146, vsize=34)


figure("s21", (W_A, H_A), fig_s21, 4.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.0)],
       "five stat cards for the DONE line; values appear in the second beat")

# --------------------------------------------------------------------------
# s23: two coverage panels
# --------------------------------------------------------------------------
def fig_s23():
    chips = ([["edges 55 из 331"], ["bitmap_cvg 16.62%"], ["stability 98.18%"]],
             [["lines 20.10%"], ["branches 20.81%"], ["regions 19.78%"]])
    return twin_cols("fs23", "AFL", "llvm-cov", chips, 126, 166, 205,
                     notes=(["рёбра CFG"], ["строки и ветки"]))


figure("s23", (W_A, H_A), fig_s23, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.8)],
       "AFL edge metrics and llvm-cov line metrics side by side")

# --------------------------------------------------------------------------
# s24 / s25: coverage bar charts
# --------------------------------------------------------------------------
def bar_rows(key, rows, accent, sx, x0, y0, step, axis_y, ticks,
             mode="left", bar_h=56):
    """Horizontal bars. rows = [(name, value, value_label)]."""
    b = []
    b.append('<g id="%s-ax">' % key)
    if mode == "left":
        b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                 'stroke-width="2"/>' % (x0, y0 - 24, x0, axis_y + 6, LINE))
    b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>'
             % (x0, axis_y, x0 + ticks[-1] * sx, axis_y, LINE))
    for t in ticks:
        b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                 'stroke-width="2"/>' % (x0 + t * sx, axis_y, x0 + t * sx,
                                         axis_y + 10, LINE))
        b.append(T(x0 + t * sx, axis_y + 38, str(t), size=24, fill=MUT))
    b.append("</g>")
    for i, (name, val, lab) in enumerate(rows):
        y = y0 + i * step
        if mode == "left":
            b.append(T(x0 - 16, y + bar_h * 0.72, name, size=24, anchor="end",
                       gid="%s-l%d" % (key, i)))
        else:
            b.append(T(x0, y - 18, name, size=24, anchor="start",
                       gid="%s-l%d" % (key, i)))
        w = val * sx
        b.append('<rect id="%s-b%d" x="%d" y="%d" width="%.1f" height="%d" '
                 'rx="4" fill="%s"/>' % (key, i + 1, x0 + 2, y, w, bar_h, accent))
        b.append(T(x0 + w + 18, y + bar_h * 0.72, lab, size=25, fill=accent,
                   anchor="start", gid="%s-v%d" % (key, i + 1)))
    return "".join(b)


def fig_s24():
    rows = [("обёртка (файл)", 93.33, "93.33%"), ("env.c", 40.19, "40.19%"),
            ("TOTAL (все файлы)", 20.10, "20.10%")]
    b = [bar_rows("fs24", rows, OR, 4.2, 280, 165, 185, 700, [0, 50, 100])]
    tw = [dict(sel="#fs24-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs24-ax", kind="rise", t=0.05, d=0.5)]
    tw += [dict(sel="#fs24-l%d" % i, kind="rise", t=0.15, d=0.4) for i in range(3)]
    tw += [dict(sel="#fs24-b1", kind="grow", t=0.85, d=0.7),
           dict(sel="#fs24-v1", kind="rise", t=1.4, d=0.4)]
    tw += [dict(sel="#fs24-b2", kind="grow", t=2.0, d=0.7),
           dict(sel="#fs24-b3", kind="grow", t=2.15, d=0.7),
           dict(sel="#fs24-v2", kind="rise", t=2.55, d=0.4),
           dict(sel="#fs24-v3", kind="rise", t=2.65, d=0.4)]
    els = [("fs24-ax", "b0", "axis", "dimmed")]
    els += [("fs24-l%d" % i, "b0", "label", "dimmed") for i in range(3)]
    els += [("fs24-b1", "b1", "bar", "zero width"), ("fs24-v1", "b1", "value", "hidden"),
            ("fs24-b2", "b2", "bar", "zero width"), ("fs24-b3", "b2", "bar", "zero width"),
            ("fs24-v2", "b2", "value", "hidden"), ("fs24-v3", "b2", "value", "hidden")]
    return "".join(b), tw, els


figure("s24", (W_A, H_A), fig_s24, 4.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.0)],
       "wrapper, env.c and TOTAL line coverage; the wrapper bar grows first")


def fig_s25():
    rows = [("fuzz_watcher_utils.py", 85, "85%"), ("_i18n.py", 82, "82%"),
            ("utils.py", 69, "69%"), ("TOTAL", 86, "86%")]
    b = [bar_rows("fs25", rows, ROSE, 6.2, 40, 140, 170, 760, [0, 50, 100],
                  mode="above")]
    tw = [dict(sel="#fs25-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs25-ax", kind="rise", t=0.05, d=0.5)]
    tw += [dict(sel="#fs25-l%d" % i, kind="rise", t=0.15, d=0.4) for i in range(4)]
    tw += [dict(sel="#fs25-b1", kind="grow", t=0.85, d=0.7),
           dict(sel="#fs25-b2", kind="grow", t=1.0, d=0.7),
           dict(sel="#fs25-v1", kind="rise", t=1.4, d=0.4),
           dict(sel="#fs25-v2", kind="rise", t=1.5, d=0.4)]
    tw += [dict(sel="#fs25-b3", kind="grow", t=2.0, d=0.7),
           dict(sel="#fs25-b4", kind="grow", t=2.15, d=0.7),
           dict(sel="#fs25-v3", kind="rise", t=2.55, d=0.4),
           dict(sel="#fs25-v4", kind="rise", t=2.65, d=0.4)]
    els = [("fs25-ax", "b0", "axis", "dimmed")]
    els += [("fs25-l%d" % i, "b0", "label", "dimmed") for i in range(4)]
    els += [("fs25-b1", "b1", "bar", "zero width"), ("fs25-b2", "b1", "bar", "zero width"),
            ("fs25-v1", "b1", "value", "hidden"), ("fs25-v2", "b1", "value", "hidden"),
            ("fs25-b3", "b2", "bar", "zero width"), ("fs25-b4", "b2", "bar", "zero width"),
            ("fs25-v3", "b2", "value", "hidden"), ("fs25-v4", "b2", "value", "hidden")]
    return "".join(b), tw, els


figure("s25", (W_A, H_A), fig_s25, 4.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.0)],
       "coverage.py line coverage for watcher; two bars per beat")

# --------------------------------------------------------------------------
# s26: Atheris pipeline
# --------------------------------------------------------------------------
def fig_s26():
    b = [lines_box(60, 110, 680, 150,
                   ["байткод-инструментация", "при импорте, без компиляции"],
                   fills=[TXT, MUT], gid="fs26-b1"),
         arrow([(400, 266), (400, 322)], "fs26-a1"),
         lines_box(60, 328, 680, 160,
                   ["Atheris: цикл coverage-guided",
                    "atheris.Setup и atheris.Fuzz"],
                   fills=[OR, MUT], stroke=OR, gid="fs26-b2"),
         arrow([(400, 494), (400, 550)], "fs26-a2"),
         lines_box(60, 556, 680, 160,
                   ["отчёт coverage.py", "строки, только при штатной остановке"],
                   fills=[TXT, MUT], gid="fs26-b3")]
    tw = [dict(sel="#fs26-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs26-b1", kind="rise", t=0.8, d=0.5),
          dict(sel="#fs26-a1", kind="draw", t=2.0, d=0.45),
          dict(sel="#fs26-b2", kind="rise", t=2.05, d=0.5),
          dict(sel="#fs26-a2", kind="draw", t=3.2, d=0.45),
          dict(sel="#fs26-b3", kind="rise", t=3.25, d=0.5)]
    els = [("fs26-b1", "b1", "stage", "dimmed"), ("fs26-a1", "b2", "arrow", "undrawn"),
           ("fs26-b2", "b2", "stage", "dimmed"), ("fs26-a2", "b3", "arrow", "undrawn"),
           ("fs26-b3", "b3", "stage", "dimmed")]
    return "".join(b), tw, els


figure("s26", (W_A, H_A), fig_s26, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "instrumentation, Atheris loop, coverage report")

# --------------------------------------------------------------------------
# s27: FuzzedDataProvider flow
# --------------------------------------------------------------------------
def fig_s27():
    b = [lines_box(120, 100, 560, 110, ["сырые байты (data)"], gid="fs27-b1"),
         arrow([(400, 216), (400, 272)], "fs27-a1"),
         '<g id="fs27-b2">' + R(60, 278, 680, 280, rx=16, stroke=ROSE, sw=3)
         + T(400, 330, "FuzzedDataProvider", size=28, weight=700, fill=ROSE)
         + chip(90, 356, 620, 54, "ConsumeIntInRange(0, 5)", gid="fs27-c1")
         + chip(90, 424, 620, 54, "ConsumeBytes(n)", gid="fs27-c2")
         + chip(90, 492, 620, 54, "ConsumeFloat()", gid="fs27-c3")
         + "</g>",
         arrow([(400, 564), (400, 620)], "fs27-a2"),
         lines_box(100, 626, 600, 150,
                   ["target_function(mode, args)", "mode и args из провайдера"],
                   fills=[OR, MUT], gid="fs27-b3")]
    tw = [dict(sel="#fs27-all", kind="wrap", t=0, d=0.5),
          dict(sel="#fs27-b1", kind="rise", t=0.8, d=0.5),
          dict(sel="#fs27-a1", kind="draw", t=2.0, d=0.45),
          dict(sel="#fs27-b2", kind="rise", t=2.05, d=0.5),
          dict(sel="#fs27-c1", kind="rise", t=2.2, d=0.4),
          dict(sel="#fs27-c2", kind="rise", t=2.3, d=0.4),
          dict(sel="#fs27-c3", kind="rise", t=2.4, d=0.4),
          dict(sel="#fs27-a2", kind="draw", t=3.2, d=0.45),
          dict(sel="#fs27-b3", kind="rise", t=3.25, d=0.5)]
    els = [("fs27-b1", "b1", "stage", "dimmed"),
           ("fs27-a1", "b2", "arrow", "undrawn"),
           ("fs27-b2", "b2", "stage", "dimmed"),
           ("fs27-c1", "b2", "chip", "dimmed"),
           ("fs27-c2", "b2", "chip", "dimmed"),
           ("fs27-c3", "b2", "chip", "dimmed"),
           ("fs27-a2", "b3", "arrow", "undrawn"),
           ("fs27-b3", "b3", "stage", "dimmed")]
    return "".join(b), tw, els


figure("s27", (W_A, H_A), fig_s27, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 3.2), ("b3", 3.2, 4.8)],
       "raw bytes into the FuzzedDataProvider, three consume calls, then the "
       "target call")

# --------------------------------------------------------------------------
# s28: watcher demo stats
# --------------------------------------------------------------------------
def fig_s28():
    cards = [("cov 262", "покрытые блоки"), ("ft 756", "новые точки"),
             ("corp 29/210b", "файлы и байты корпуса"),
             ("lim 34", "лимит длины")]
    return stat_cards("fs28", cards, ROSE, y0=110, h=140, step=180, vsize=34)


figure("s28", (W_A, H_A), fig_s28, 4.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 4.0)],
       "four stat cards for the watcher demo; values in the second beat")

# --------------------------------------------------------------------------
# s29: Jazzer and Go
# --------------------------------------------------------------------------
def fig_s29():
    chips = ([["fuzzerTestOneInput()"], ["сборка JAR"],
              ["java -cp ... jazzer.jar"], ["crash-<sha1>"]],
             [["func FuzzXxx", "(f *testing.F)"], ["go test -fuzz"],
              [["testdata/fuzz/", "FuzzXxx"]][0], ["f.Add и f.Fuzz"]])
    return twin_cols("fs29", "Jazzer (JVM)", "Go", chips, 120, 150, 200)


figure("s29", (W_A, H_A), fig_s29, 4.8,
       [("b0", 0, 0.8), ("b1", 0.8, 2.2), ("b2", 2.2, 4.8)],
       "JVM column and Go column, four chips each")

# --------------------------------------------------------------------------
# s30: six step roadmap (diagram layout canvas)
# --------------------------------------------------------------------------
def fig_s30():
    steps = [("1", "lizard", ["выбор функции", "по CCN"]),
             ("2", "обёртка", ["fuzz_", "<функция>.c"]),
             ("3", "сборка", ["afl-clang-fast", "и clang", "-fsanitize"]),
             ("4", "корпус", ["три сида и", "1 или 2 файла"]),
             ("5", "прогон", ["AFL и", "libFuzzer"]),
             ("6", "покрытие", ["edges и cov", "и llvm-cov"])]
    b = []
    x0, bw, gap = 30, 220, 44
    for i, (num, title, det) in enumerate(steps):
        x = x0 + i * (bw + gap)
        acc = OR if i < 2 else (ROSE if i == 5 else LINE)
        b.append('<g id="fs30-s%d">' % (i + 1)
                 + R(x, 190, bw, 230, rx=16,
                     stroke=ROSE if i == 5 else LINE, sw=3 if i == 5 else 2)
                 + '<circle cx="%.0f" cy="120" r="32" fill="%s" stroke="%s" '
                   'stroke-width="3"/>' % (x + bw / 2, SURF, acc)
                 + T(x + bw / 2, 130, num, size=28, weight=700, fill=acc)
                 + T(x + bw / 2, 260, title, size=27, weight=700)
                 + "".join(T(x + bw / 2, 308 + j * 32, ln, size=24, fill=MUT)
                           for j, ln in enumerate(det))
                 + "</g>")
    for i in range(5):
        x = x0 + i * (bw + gap) + bw + 4
        b.append(arrow([(x, 305), (x + gap - 8, 305)], "fs30-a%d" % (i + 1),
                       sw=3))
    tw = [dict(sel="#fs30-all", kind="wrap", t=0, d=0.5)]
    tw += [dict(sel="#fs30-s%d" % i, kind="rise", t=0.8 + 0.15 * (i - 1), d=0.45)
           for i in (1, 2, 3)]
    tw += [dict(sel="#fs30-a%d" % i, kind="draw", t=1.2 + 0.15 * (i - 1), d=0.35)
           for i in (1, 2)]
    tw += [dict(sel="#fs30-s%d" % i, kind="rise", t=2.0 + 0.15 * (i - 4), d=0.45)
           for i in (4, 5, 6)]
    tw += [dict(sel="#fs30-a%d" % i, kind="draw", t=2.4 + 0.15 * (i - 3), d=0.35)
           for i in (3, 4, 5)]
    els = [("fs30-s%d" % i, "b1" if i <= 3 else "b2", "step", "dimmed")
           for i in range(1, 7)]
    els += [("fs30-a%d" % i, "b1" if i <= 2 else "b2", "arrow", "undrawn")
            for i in range(1, 6)]
    return "".join(b), tw, els


figure("s30", (W_B, 520), fig_s30, 6.0,
       [("b0", 0, 0.8), ("b1", 0.8, 2.0), ("b2", 2.0, 6.0)],
       "six step roadmap, first three steps and their arrows, then the rest")
