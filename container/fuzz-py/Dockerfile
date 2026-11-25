# Atheris-контейнер курса: Python-фаззинг на openstack/watcher
#
#   - atheris 3.0.0 (3.1.0+ не имеет колёс для Python 3.11 в bookworm)
#   - цель демо: watcher (openstack/watcher) — самая лёгкая цепочка зависимостей
#     из Python-обёрток workspace (glance/cinder не поднимаются: см. course.md)
#   - исходники watcher: /opt/atheris-src/watcher (git, pbr требует git-репо)
#   - обёртка из workspace: /opt/atheris/refs/watcher
#
# Сборка (контекст = корень проекта):
#   docker build -t fuzz-py:latest -f container/fuzz-py/Dockerfile .
# Запуск:
#   docker run -d --name fuzz-py --rm fuzz-py:latest sleep infinity
# Всё содержимое (курс, задание, решение) встроено в образ в /opt/course —
# монтирования не нужны.

FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        python3-dev \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# venv с atheris и зависимостями watcher (версии зафиксированы — то, что проверено)
RUN python3 -m venv /opt/atheris \
    && /opt/atheris/bin/pip install --no-cache-dir --upgrade pip==24.0 \
    && /opt/atheris/bin/pip install --no-cache-dir \
        atheris==3.0.0 \
        coverage==7.6.10 \
        lizard==1.26.1 \
        croniter==7.0.0 \
        jsonschema==4.26.0 \
        keystoneauth1==5.18.1 \
        pbr==7.1.3 \
        cotyledon==2.2.0 \
        futurist==3.5.0 \
        "PyYAML==6.0.3" \
        "oslo.config==10.8.1" \
        "oslo.log==8.3.2" \
        "oslo.utils==10.3.0" \
        "oslo.i18n==6.9.0" \
        "oslo.service==4.8.0"
ENV PATH="/opt/atheris/bin:$PATH"

# Исходники watcher + установка для pbr-versioning
RUN git clone --depth 1 https://github.com/openstack/watcher.git /opt/atheris-src/watcher \
    && /opt/atheris/bin/pip install -e /opt/atheris-src/watcher --no-deps --no-cache-dir

# Обёртка из workspace
COPY fuzz-builder/targets/watcher /opt/atheris/refs/watcher

# Курс и задание: всё внутри образа, без монтирований
COPY course.md                          /opt/course/course.md
COPY demo.md                            /opt/course/demo.md
COPY exercises/full-cycle/task.md       /opt/course/exercises/full-cycle/task.md
COPY exercises/full-cycle/seed          /opt/course/exercises/full-cycle/seed
COPY exercises/full-cycle/solution      /opt/course/exercises/full-cycle/solution

# Дымовой тест: прогон обёртки на 2 секунды с одним сидом,
# затем проверка цепочки покрытия (coverage run -> coverage report)
RUN set -e; \
    mkdir -p /tmp/smoke-corpus && printf '* * * * *\necho hi\n' > /tmp/smoke-corpus/seed1; \
    cd /opt/atheris-src/watcher \
    && timeout 60 /opt/atheris/bin/python /opt/atheris/refs/watcher/fuzz_watcher_utils.py \
         -runs=2000 -max_len=512 -timeout=5 -detect_leaks=0 /tmp/smoke-corpus; \
    rm -rf /tmp/smoke-corpus; \
    rm -rf /tmp/smoke-cov && mkdir -p /tmp/smoke-cov/corpus \
        && printf '* * * * *\necho hi\n' > /tmp/smoke-cov/corpus/seed1; \
    cd /tmp/smoke-cov \
    && timeout 60 /opt/atheris/bin/python -m coverage run /opt/atheris/refs/watcher/fuzz_watcher_utils.py \
         -atheris_runs=100 -max_len=512 -timeout=5 -detect_leaks=0 corpus; \
    test -s .coverage \
    && /opt/atheris/bin/python -m coverage report | grep -q fuzz_watcher_utils.py; \
    cd / && rm -rf /tmp/smoke-cov; \
    lizard --version; \
    test -d /opt/course/exercises/full-cycle/solution; \
    echo IMAGE_SMOKE_OK

WORKDIR /opt/atheris
CMD ["sleep", "infinity"]
