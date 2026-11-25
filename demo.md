# Runbook демонстрации

Точная последовательность команд для созвона (~60 мин). Все пути внутри
контейнера; хостные команды — для запуска контейнеров. Контейнеры запускать
с `--rm`, чтобы не оставлять мусор.

> Не путать с `exercises/full-cycle/task.md` — там студент, там не видны
> ни решение, ни ожидаемые результаты.

## 0. Запуск контейнеров (хост, разово)

```bash
docker run -d --name fuzz-course --rm fuzz-c:latest sleep infinity
docker run -d --name fuzz-py  --rm fuzz-py:latest  sleep infinity
```

| Флаг | Значение |
|---|---|
| `-d` | фоновый режим — контейнер работает без привязки к терминалу |
| `--name` | имя контейнера для `docker exec` (без него Docker выдумывает имя) |
| `--rm` | контейнер удаляется при остановке — не остаётся «мусорных» контейнеров |
| `sleep infinity` | главный процесс контейнера: держит контейнер живым для `docker exec` |

Войти (внутри контейнера):

```bash
docker exec -it fuzz-course bash                     # C-демонстрация
docker exec -it -w /opt/atheris-src/watcher fuzz-py bash   # Python-демонстрация
```

| Флаг | Значение |
|---|---|
| `-it` | интерактивный TTY + stdin — нужен для интерактивной сессии `bash` |
| `-w <dir>` | `--workdir`: рабочая директория процесса (см. раздел 2) |

## 1. Контейнер `fuzz-course` — полный путь (C)

Собираем и фаззим `load_env()` из cronie 1.5.7. Рабочий каталог:

```bash
cd /opt/course/exercises/full-cycle/solution
```

### 1.1 Lizard — выбор функции

```bash
lizard /opt/fuzzenv/src/cronie-1.5.7/src/*.c
```

| Что в строке | Пояснение |
|---|---|
| `lizard` | статический анализатор: подсчитывает метрики сложности каждой функции. Никакого заголовка или системы сборки не требует |
| `/opt/fuzzenv/src/cronie-1.5.7/src/*.c` | путь к исходникам; `*.c` — шелл-экспансия, подставит все `.c`-файлы каталога |

Другие ключи (если надо): `-C 20` — порог предупреждений по CCN (функция с
CCN выше порога получит warning); `-s cyclomatic_complexity` — сортировать
отчёт по CCN; `-t 4` — 4 рабочих потока для ускорения.

**Что показать.** Колонки NLOC / CCN / token: топ — `child_process` (84),
`load_entry` (67), `parse_args` (54), `edit_cmd` (52), `main` (50). Выбор —
`load_env` (env.c:181–276, CCN 31, NLOC 88): чистый парсер без побочных
эффектов, линкуется минимумом .c-файлов, а `child_process` exec'ит процессы
и пишет в файлы — мимо фаззера.

### 1.2 Разово — config cronie

```bash
cp /opt/fuzzenv/refs/cronie/config.h.manual     /opt/fuzzenv/src/cronie-1.5.7/config.h
cp /opt/fuzzenv/refs/cronie/cron-paths.h.manual /opt/fuzzenv/src/cronie-1.5.7/src/cron-paths.h
```

`cp` — консольная копия; источник — файл «от руки» из workspace (то, что
сгенерировал бы `./configure`), назначение — место, где cronie ждёт config
при сборке.

### 1.3 Сборка — обе сборки, один файл

```bash
make libfuzzer        # clang -fsanitize=fuzzer,address → fuzz_load_env_lf
make afl              # afl-clang-fast → fuzz_load_env_afl
```

`make <цель>` — запускает правило из `Makefile`; цель `libfuzzer` вызывает
`clang -fsanitize=fuzzer,address ...`, цель `afl` — `afl-clang-fast ...`.

| Флаг clang/afl | Значение |
|---|---|
| `-fsanitize=fuzzer` | встроить цикл фаззинга libFuzzer: главная функция `main` и битмап покрытий; без этого нет фаззера вообще |
| `-fsanitize=address` | встроить AddressSanitizer: находит выходы за границы кучи, use-after-free, double-free — это и есть «сбой», который ищет фаззер |
| `-g` | включить отладочную информацию: ASan/libFuzzer печатают читаемые отчёты (функции, строки) вместо адресов |
| `-O1` | оптимизация уровня 1: быстро и без агрессивной удаления «мёртвого» кода (`-O0` — на порядки медленнее, `-O2/-O3` искажают покрытие) |
| `-DHAVE_CONFIG_H` | определить макрос `HAVE_CONFIG_H` — cronie через `config.h` решает, что включать при сборке |
| `-I<dir>` | добавить каталог в поиск заголовков (без него — `undefined reference` на внутренние `.h`) |
| `-o <имя>` | имя выходного бинарника |

**Что показать.** Одна обёртка `fuzz_load_env.c`, два компилятора, два бинарника.

### 1.4 Стартовый корпус

```bash
mkdir -p corpus && cp /opt/course/exercises/full-cycle/seed/*.cr corpus/ && ls corpus/
```

| Команда | Пояснение |
|---|---|
| `mkdir -p corpus` | создать каталог `corpus/` (`-p` — не падать, если он уже есть) |
| `cp .../*.cr corpus/` | скопировать 3 сида в рабочую папку |
| `ls corpus/` | проверить, что файлы на месте |

### 1.5 Прогон AFL

```bash
AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 afl-fuzz -i corpus -o out -V 20 ./fuzz_load_env_afl
```

Разбор строки команды, строка за строкой:

| Элемент | Значение |
|---|---|
| `AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1` | переменная окружения перед командой (см. ниже — разбор подробно) |
| `afl-fuzz` | драйвер AFL++: берёт входы из `corpus/`, мутирует, сохраняет те входы, что открывают новое покрытие |
| `-i corpus` | входная папка с стартовым корпусом (обязательно). Именно отсюда afl-fuzz читает сиды |
| `-o out` | выходная папка для результатов (обязательно). Создаст `out/default/queue/` (обнаруженный корпус), `out/default/crashes/`, `out/default/hangs/`, `out/default/fuzzer_stats`, `out/default/plot_data` |
| `-V 20` | «fuzz for a specified time then terminate» — 20 секунд, после чего afl-fuzz сам завершится; без флага — цикл до Ctrl-C |
| `./fuzz_load_env_afl` | позиционный аргумент: бинарник-цель (без аргументов — нечего передавать) |

**Зачем нужна переменная `AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1`.**

При запуске `afl-fuzz` читает системный файл `/proc/sys/kernel/core_pattern`.
Он определяет, куда ядро шлёт уведомление о краше. В этом контейнере в файле:

```
|/usr/lib/systemd/systemd-coredump %P %u %g %s %t %c %h %d %F
```

то есть уведомление о краше уходит **через пайп во внешнюю утилиту**
(`systemd-coredump`). Внешний обработчик задерживает доставку уведомления в
фаззер через `waitpid()`, поэтому сбой может быть ошибочно классифицирован
как таймаут (`program timeout`), а краши не будут зафиксированы.

Проверка делает `afl-fuzz` в `check_crash_handling()` (`src/afl-fuzz-init.c`).
Без переменной окружения программа **не стартует вовсе** — падает с
`[-] PROGRAM ABORT : Pipe at the beginning of 'core_pattern'`.

Официальный способ решения (из самого сообщения): войти под root и выполнить
`echo core >/proc/sys/kernel/core_pattern`. В контейнере это невозможно —
`/proc` доступен только для чтения (проверено: `Read-only file system`).

`AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1` — единственная доступная здесь
альтернатива: она **подразумевает**, что задержка доставки уведомлений
допустима, и выключает проверку-забастовку. Это не «улучшение» фаззинга:
прогон останавливается без неё, с ней — продолжается с осознанным
ограничением окружения.

> **Важно для демонстрации.** Переменная не делает прогон «быстрее» или
> «лучше» — она убирает забастовку на старте. Если бы у нас был root и
> разрешённая правка `/proc/sys/kernel/core_pattern`, это был бы более
> чистое решение (но в контейнере оно недоступно).

**Что показать.** На экране: `time`, `execs_done`, `corpus`, `stability`,
`edges_found`. После остановки:

```bash
cat out/default/fuzzer_stats | grep -E "execs_done|corpus_count|corpus_favored|stability|edges_found|total_edges|bitmap_cvg|saved_crashes"
```

`grep -E "a|b|c"` — расширенное регулярное выражение по списку колонок
(`-E`). Ожидаемо: execs ~1.7M (~85k/s), corpus 3→71, stability ~98%,
edges 55/331, bitmap_cvg ~16.6%, saved_crashes 0.

### 1.6 Прогон libFuzzer

```bash
./fuzz_load_env_lf corpus/ -max_len=4096 -runs=200000 -print_final_stats
```

| Элемент | Значение |
|---|---|
| `./fuzz_load_env_lf` | бинарник — главный `main` сгенерирован при компиляции (`-fsanitize=fuzzer`) |
| `corpus/` | позиционный аргумент: каталог с валидными входами (таргет читает seed-корпус отсюда) |
| `-max_len=4096` | максимальная длина входа, байты. «If 0, libFuzzer tries to guess a good value based on the corpus and reports it» — без флага лимит берётся из корпуса; мы задаём явно |
| `-runs=200000` | «Number of individual test runs». По умолчанию `-1` (бесконечно) — без флага прогон никогда не закончится. 200 000 — верхняя граница, после которой прогон остановится |
| `-print_final_stats` | «If 1, print statistics at exit» (по умолчанию 0 — выключено). Включает итоговую строку `DONE cov: ... ft: ... corp: ...` |

> **Важно.** `-help` **не является** валидным флагом libFuzzer. Бинарник
> напечатает `WARNING: unrecognized flag '-help'; use -help=1` и продолжит
> фаззить с пустым корпусом (и никогда не остановится). Правильная помощь:
> `-help=1`. Проверено: запуск с bare `-help` не остановится.

Ожидаемо в конце: `DONE cov: 47 ft: 164 corp: 77/2080b lim: 1788`.

### 1.7 Покрытие — line-level (llvm-cov)

```bash
mkdir -p /tmp/cov_out && cd /tmp/cov_out
cp /opt/course/exercises/full-cycle/solution/fuzz_load_env.c .
mkdir -p cov_corpus && cp /opt/course/exercises/full-cycle/seed/*.cr cov_corpus/
clang -fprofile-instr-generate -fcoverage-mapping -fsanitize=fuzzer,address \
  -g -O1 -DHAVE_CONFIG_H \
  -I/opt/fuzzenv/src/cronie-1.5.7/src -I/opt/fuzzenv/src/cronie-1.5.7 \
  fuzz_load_env.c /opt/fuzzenv/src/cronie-1.5.7/src/env.c \
  /opt/fuzzenv/src/cronie-1.5.7/src/misc.c /opt/fuzzenv/src/cronie-1.5.7/src/pw_dup.c \
  -o cov_lf
./cov_lf cov_corpus -runs=3000
llvm-profdata merge -sparse default.profraw -o default.profdata
llvm-cov report ./cov_lf -instr-profile=default.profdata
```

| Команда/флаг | Пояснение |
|---|---|
| `clang -fprofile-instr-generate` | встроить счётчики профиля: каждый запуск пишет `default.profraw` (профили-счётчики покрытия) |
| `clang -fcoverage-mapping` | встроить coverage-mapping, который `llvm-cov` использует для привязки покрытия к строкам исходника |
| `./cov_lf` (с `-runs=3000`) | тот же флаг `-runs`, что рассказал в 1.6 |
| `llvm-profdata merge -sparse default.profraw -o default.profdata` | `merge` — объединить profraw-файлы; `-sparse` — компактный формат выходного файла; `-o` — имя выходного файла |
| `llvm-cov report ./cov_lf -instr-profile=default.profdata` | `report` — сводная таблица с процентами по каждой строке/файлу; `./cov_lf` — бинарник (llvm-cov читает отладочную информацию из него, чтобы привязать счётчики к исходнику); `-instr-profile` — путь к profdata |

Ожидаемо: TOTAL ~19.8% regions / ~20.1% lines, `env.c` ~40% lines / ~45.5%
regions, `fuzz_load_env.c` ~93% lines. **Вывод демонстрации:** обёртка хорошо
покрыта, целевая логика — нет. Именно поэтому фаззинг продолжается.

### 1.8 (Опционально) Референс — shadow-utils, тот же путь

```bash
cd /tmp && mkdir -p sh && cd sh
cp /opt/fuzzenv/refs/shadow/fuzz_sgetpwent.c .
clang -fsanitize=fuzzer,address -g -O1 -DHAVE_CONFIG_H \
  -I/opt/fuzzenv/src/shadow-4.8.1/lib \
  -I/opt/fuzzenv/src/shadow-4.8.1/libmisc \
  -I/opt/fuzzenv/src/shadow-4.8.1 \
  fuzz_sgetpwent.c \
  /opt/fuzzenv/src/shadow-4.8.1/lib/sgetpwent.c \
  /opt/fuzzenv/src/shadow-4.8.1/lib/get_uid.c \
  /opt/fuzzenv/src/shadow-4.8.1/lib/get_gid.c \
  /opt/fuzzenv/src/shadow-4.8.1/lib/getlong.c \
  /opt/fuzzenv/src/shadow-4.8.1/lib/getulong.c \
  -o sh_lf
mkdir -p sc && cp /opt/fuzzenv/refs/shadow/corpus/*.txt sc/
./sh_lf sc/ -max_len=200 -runs=100000 -print_final_stats
```

Все флаги clang — те же, что в 1.3. `-max_len=200` — максимум 200 байт входа
(строка `/etc/passwd` короткая). `-runs=100000` — стоп после 100k прогонов.
`-print_final_stats` — итоговая статистика.

## 2. Контейнер `fuzz-py` — Atheris (Python)

Вход с выставленной рабочей директорией — так, как в дымовом тесте образа:

```bash
docker exec -it -w /opt/atheris-src/watcher fuzz-py bash
```

| Флаг/элемент | Значение |
|---|---|
| `-w <dir>` | `--workdir`: рабочая директория процесса внутри контейнера. Без неё процесс стартует в `WORKDIR` образа — у fuzz-py это `/opt/atheris` |

> Импорт `watcher` работает и без `-w`: в образе он установлен editable
> (.pth в site-packages), поэтому импорт не зависит от каталога. Флаг нужен,
> чтобы демонстрация проходила так же, как дымовой тест образа
> (`cd /opt/atheris-src/watcher && ...`) и так же, как запуск в исходном
> workspace. Без него команда всё равно отработает (проверено: прогон 200
> прогонов из `/opt/atheris` успешен).

**Демо watcher (~10 сек):**

```bash
mkdir -p /tmp/wcorpus && printf "* * * * *\necho hi\n" > /tmp/wcorpus/seed1
/opt/atheris/bin/python /opt/atheris/refs/watcher/fuzz_watcher_utils.py \
  -max_len=512 -timeout=5 -detect_leaks=0 -runs=10000 /tmp/wcorpus
```

| Элемент | Значение |
|---|---|
| `/opt/atheris/bin/python` | python-интерпретатор из venv с atheris (не системный) |
| `fuzz_watcher_utils.py` | точка входа: `Setup(argv, TestOneInput)` + `Fuzz()` |
| `-max_len=512` | максимальная длина входа (те же семантики, что у libFuzzer) |
| `-timeout=5` | секунд на один вход; вход, выполняющийся дольше, считается timeout (по умолчанию 1200 — мы ставим 5) |
| `-detect_leaks=0` | выключить leak-detection (по умолчанию — включен): для демонстрации не нужен |
| `-runs=10000` | стоп после 10000 прогонов (по умолчанию — бесконечно) |
| `/tmp/wcorpus` | каталог с валидным входом (тот же смысл, что `corpus/` у C-фаззеров) |

Ожидаемо в конце: `#10000  DONE  cov: 262 ft: 756 corp: 29/210b lim: 34`.

**Что показать.** `instrument_imports()` до импорта цели,
`FuzzedDataProvider` для разбора байт-потока, `Setup` + `Fuzz()`.

**Покрытие (~15 сек) — coverage.py:**

```bash
mkdir -p /tmp/covtest/corpus && printf "* * * * *\necho hi\n" > /tmp/covtest/corpus/seed1
cd /tmp/covtest
/opt/atheris/bin/python -m coverage run /opt/atheris/refs/watcher/fuzz_watcher_utils.py \
  -atheris_runs=200 -max_len=512 -timeout=5 -detect_leaks=0 corpus
/opt/atheris/bin/python -m coverage report
```

| Элемент | Значение |
|---|---|
| `python -m coverage run` | запуск программы под coverage.py; собирает `.coverage` в текущую папку |
| `-atheris_runs=200` | число прогонов, после которого fuzzer **штатно** завершится и запишет отчёт. Обязателен для генерации отчёта — libFuzzer-флаг `-runs=200` даёт штатное завершение **без** отчёта (проверено: `coverage report` покажет «No data to report») |
| `coverage report` | текстовая таблица `file / Stmts / Miss / Cover` по текущему `.py`-коду (html и xml — `coverage html` / `coverage xml`) |
| `-max_len/-timeout/-detect_leaks=0` | те же флаги, что и выше |

Ожидаемо: `TOTAL ~86%`, `utils.py ~69%`, `fuzz_watcher_utils.py ~85%`.
**Вывод демонстрации:** `cov` в строке `DONE` — внутренняя метрика
(битмап), `coverage report` — line-level картина по строкам и файлам.
Для line-level покрытия на atheris используется coverage.py, а не
встроенная метрика.

**lizard для Python (тот же инструмент):**

```bash
lizard /opt/atheris-src/watcher/watcher/common/utils.py
```

> `lizard` работает на Python — те же ключи, та же таблица. Для Python-цели
> выбор идёт по тем же правилам (высокая CCN, мало зависимостей): в
> `common/` топ — `live_migrate_instance@910-1011` в `nova_helper.py` (CCN 16).
> lizard есть в venv fuzz-py (`lizard==1.26.1`).

## 3. Контрольный список перед созвоном

- [ ] оба контейнера подняты (`docker ps` — `fuzz-course`, `fuzz-py`, `--rm`)
- [ ] config.h / cron-paths.h на месте (шаг 1.2)
- [ ] lizard отработал без ошибок
- [ ] обе сборки (`make libfuzzer`, `make afl`) — без ошибок
- [ ] AFL/LF прогоны — ожидаемые числа (раздел 1.5/1.6)
- [ ] llvm-cov отчёт сгенерирован
- [ ] atheris demo — `cov` растёт
