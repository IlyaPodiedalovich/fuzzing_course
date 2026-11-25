# presentation/

Рабочее пространство для перевода курса «Курс по фаззингу: AFL, libFuzzer, Atheris»
(`course.md`) в HTML-презентацию.

| Файл | Что |
|---|---|
| `fuzzing-course.skeleton.yaml` | скелет (schema v1.1): 35 слайдов: титул, разделы, таблицы, три diagram-сцены, beat-таблицы. Validate: `python3 .pi/skills/presentation-skeleton/scripts/validate.py fuzzing-course.skeleton.yaml` |
| `design.md` | airbrush design-пакет (из designmd.app/library/airbrush): токены, цвета, типографика, радиус/отступы, компоненты, эффекты, do's/don'ts. Ссылается `meta.design_ref` |
| `prompt.md` | AI Prompt + Execution Rules + Implementation Checklist с той же страницы, дословно |

Следующий этап (после валидации): сборка деки через `deck-html` (HTML + PDF).
Скелет на этом этапе служит источником контента и анимации, а не готовыми артефактами.
