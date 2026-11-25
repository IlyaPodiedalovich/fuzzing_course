# Контейнеры курса

Фаззинг-утилиты не ставятся на хост — вся практика в контейнерах.
Два образа, оба самодостаточны (исходники и обёртки уже внутри, монтировать ничего не нужно).

## `fuzz-c` — C-часть (AFL + libFuzzer + lizard)

| Компонент | Версия | Примечание |
|---|---|---|
| AFL | AFL++ 4.04c (apt `afl`) | тот же интерфейс, что у классического AFL 2.92b |
| libFuzzer | clang 14 + `libclang-rt-14-dev` | рантайм в секции contrib — в sources уже включён |
| lizard | 1.26.1 | venv `/opt/fuzz` (в PATH) |
| исходники | cronie 1.5.7, shadow-utils 4.8.1 | `/opt/fuzzenv/src/`; у shadow `config.h` уже сгенерирован |
| референсы | обёртки/корпуса из workspace | `/opt/fuzzenv/refs/{cronie,shadow,coreutils,rpm}` |
| курс/задание | `course.md`, `demo.md`, `exercises/` | `/opt/course/` (вся внутренняя копия) |
| cronie config | `config.h`/`cron-paths.h` «от руки» | уже скопированы из `refs/cronie/*.manual` |

```bash
# из корня проекта (контекст сборки = корень, COPY видит fuzz-builder/)
docker build -t fuzz-c:latest -f container/fuzz-c/Dockerfile .
docker run -d --name fuzz-course --rm fuzz-c:latest sleep infinity
docker exec -it fuzz-course bash
```

## `fuzz-py` — Atheris (Python-фаззинг)

| Компонент | Версия | Примечание |
|---|---|---|
| atheris | 3.0.0 | 3.1.0+ без колёс для Python 3.11 (bookworm) |
| coverage | 7.6.10 | покрытие строк (coverage.py), §8.4 курса |
| lizard | 1.26.1 | тот же инструмент, что и в fuzz-c; работает на Python |
| цель демо | openstack/watcher | `/opt/atheris-src/watcher` (editable-install; импорт не зависит от cwd) |
| обёртка | `watcher/fuzz_watcher_utils.py` из workspace | `/opt/atheris/refs/watcher/` |

```bash
docker build -t fuzz-py:latest -f container/fuzz-py/Dockerfile .
docker run -d --name fuzz-py --rm fuzz-py:latest sleep infinity
# демо (cwd — исходники watcher):
docker exec -it -w /opt/atheris-src/watcher fuzz-py bash -c '
  mkdir -p /tmp/wcorpus && printf "* * * * *\necho hi\n" > /tmp/wcorpus/seed1
  /opt/atheris/bin/python /opt/atheris/refs/watcher/fuzz_watcher_utils.py \
    -max_len=1024 -timeout=5 -detect_leaks=0 /tmp/wcorpus'
```

## Воспроизводимость

- Все версии: пакеты — Debian bookworm, python — пин в Dockerfile,
  исходники — фиксированные релизы (cronie 1.5.7, shadow 4.8.1),
  watcher — HEAD master openstack/watcher (единственное «плавающее»).
- В обоих Dockerfile дымовой тест: образ не соберётся, если инструмент
  или обёртка не работает.
- Проверено (см. `course.md`, разделы 3–5): референс cronie `fuzz_load_entry`
  (libFuzzer), решение `fuzz_load_env` (оба фаззера), shadow `fuzz_sgetpwent`
  (оба фаззера), watcher (atheris).

## Экспорт / импорт образов

Готовые архивы образов — в `images/` (не коммитятся; ~355 МБ и ~183 МБ соответственно в gzip-виде):

| Архив | Образ |
|---|---|
| `images/fuzz-c.tar.gz` | `fuzz-c:latest` (C-практика) |
| `images/fuzz-py.tar.gz` | `fuzz-py:latest` (Atheris) |

Чтобы сохранить текущие образы заново:

```bash
docker save fuzz-c:latest  | gzip -1 > images/fuzz-c.tar.gz
docker save fuzz-py:latest | gzip -1 > images/fuzz-py.tar.gz
```

Чтобы загрузить образ на другой хост (или восстановить после удаления):

```bash
docker load -i images/fuzz-c.tar.gz    # грузит fuzz-c:latest
docker load -i images/fuzz-py.tar.gz    # грузит fuzz-py:latest
```

После импорта образа поднимаются контейнеры без монтирований:

```bash
docker run -d --name fuzz-course --rm fuzz-c:latest sleep infinity
docker run -d --name fuzz-py --rm fuzz-py:latest sleep infinity
```
