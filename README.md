# fuzzing_course

Курс по фаззингу для коллеги: AFL, libFuzzer, Atheris + lizard (цикломатическая
сложность) + процесс сбора покрытия. Практика — полный цикл на cronie.

## Состав

| Путь | Что |
|---|---|
| `course.md` | курс (полный путь: lizard → обёртка → сборка → AFL/libFuzzer → покрытие → Atheris) |
| `demo.md` | runbook демонстрации: точные команды и ожидаемые выводы по контейнерам |
| `exercises/full-cycle/` | задание «Полный цикл»: `task.md`, сиды в `seed/`, решение в `solution/` (все встроены в образ в `/opt/course/exercises/full-cycle/`) |
| `container/` | Dockerfile и README двух контейнеров (`fuzz-c`, `fuzz-py`) |
| `fuzz-builder/` | исходный AI-workspace с обёртками (из архива; материал для разборов) |
| `docs/agents/`, `.scratch/` | локальный issue-трекер (markdown) и правила для agent-skills |
| `.pi/skills/` | установленные matt-skills (engineering + productivity) |

## Быстрый старт

```bash
docker build -t fuzz-c:latest -f container/fuzz-c/Dockerfile .
docker build -t fuzz-py:latest -f container/fuzz-py/Dockerfile .
docker run -d --name fuzz-course --rm fuzz-c:latest sleep infinity
docker run -d --name fuzz-py  --rm fuzz-py:latest  sleep infinity
docker exec -it fuzz-course bash
```

## Статус

- [x] контейнеры собраны и проверены (сборки/прогоны всех обёрток — в `container/README.md`)
- [x] курс `course.md`
- [x] задание + решение + сиды
- [ ] прохождение задания самим пользователем
- [ ] созвон по `course.md`
