# C-контейнер курса по фаззингу: AFL + libFuzzer + lizard
#
#   - AFL: apt `afl` в Debian bookworm = AFL++ 4.04c (надмножество классического
#     AFL 2.92b, тот же интерфейс: afl-fuzz, afl-clang-fast, __AFL_LOOP)
#   - libFuzzer: clang 14 + libclang-rt-14-dev (рантайм -fsanitize=fuzzer;
#     пакет в секции contrib, поэтому sources ниже включают contrib)
#   - lizard: venv /opt/fuzz (в PATH)
#   - исходники: cronie 1.5.7, shadow-utils 4.8.1 — /opt/fuzzenv/src
#   - референсы из workspace (обёртки, корпуса, словари): /opt/fuzzenv/refs
#
# Сборка (контекст = корень проекта, чтобы COPY видел fuzz-builder/):
#   docker build -t fuzz-c:latest -f container/fuzz-c/Dockerfile .
# Запуск:
#   docker run -d --name fuzz-course --rm fuzz-c:latest sleep infinity
# Всё содержимое (курс, задание, решение) встроено в образ в /opt/course —
# монтирования не нужны.

FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

# contrib — ради libclang-rt-14-dev (рантайм libFuzzer); bookworm использует deb822-формат
RUN sed -i 's/^Components: .*/& contrib/' /etc/apt/sources.list.d/debian.sources

# Инструменты
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        clang \
        llvm \
        libclang-rt-14-dev \
        python3 \
        python3-venv \
        python3-dev \
        git \
        wget \
        ca-certificates \
        gdb \
        afl \
    && rm -rf /var/lib/apt/lists/*

# lizard (версия зафиксирована)
RUN python3 -m venv /opt/fuzz \
    && /opt/fuzz/bin/pip install --no-cache-dir --upgrade pip==24.0 \
    && /opt/fuzz/bin/pip install --no-cache-dir lizard==1.26.1
ENV PATH="/opt/fuzz/bin:$PATH"

# Исходники целей (фиксированные релизы)
RUN mkdir -p /opt/fuzzenv/src \
    && wget -q https://github.com/cronie-crond/cronie/releases/download/cronie-1.5.7/cronie-1.5.7.tar.gz \
    && tar xzf cronie-1.5.7.tar.gz -C /opt/fuzzenv/src \
    && rm cronie-1.5.7.tar.gz \
    && wget -q https://github.com/shadow-maint/shadow/releases/download/4.8.1/shadow-4.8.1.tar.gz \
    && tar xzf shadow-4.8.1.tar.gz -C /opt/fuzzenv/src \
    && rm shadow-4.8.1.tar.gz \
    # shadow: config.h (нужен для обёртки sgetpwent; cronie — config.h.manual)
    && cd /opt/fuzzenv/src/shadow-4.8.1 \
    && ./configure --without-pam --without-selinux --without-audit > /dev/null

# Референсы: обёртки/корпуса из workspace
COPY fuzz-builder/targets/cronie      /opt/fuzzenv/refs/cronie
COPY fuzz-builder/targets/shadow      /opt/fuzzenv/refs/shadow
COPY fuzz-builder/targets/coreutils   /opt/fuzzenv/refs/coreutils
COPY fuzz-builder/targets/rpm         /opt/fuzzenv/refs/rpm

# cronie: config «от руки» (аналог ./configure) — разово при сборке образа;
# в задании этот шаг объясняется, а не делается руками
RUN cp /opt/fuzzenv/refs/cronie/config.h.manual      /opt/fuzzenv/src/cronie-1.5.7/config.h \
    && cp /opt/fuzzenv/refs/cronie/cron-paths.h.manual /opt/fuzzenv/src/cronie-1.5.7/src/cron-paths.h

# Курс и задание: всё внутри образа, без монтирований
COPY course.md                          /opt/course/course.md
COPY demo.md                            /opt/course/demo.md
COPY exercises/full-cycle/task.md       /opt/course/exercises/full-cycle/task.md
COPY exercises/full-cycle/seed          /opt/course/exercises/full-cycle/seed
COPY exercises/full-cycle/solution      /opt/course/exercises/full-cycle/solution

# Дымовой тест: image не соберётся, если что-то из инструментов не работает
RUN set -e; \
    afl-fuzz -h 2>&1 | head -1; \
    afl-clang-fast --version 2>&1 | head -1; \
    clang --version | head -1; \
    echo '#include <stddef.h>\nint LLVMFuzzerTestOneInput(unsigned char *d, size_t n){(void)d;return n>1000000?1:0;}' > /tmp/smoke.c; \
    clang -fsanitize=fuzzer,address -g -O1 /tmp/smoke.c -o /tmp/smoke; \
    /tmp/smoke -runs=5 > /dev/null; \
    lizard --help | head -1; \
    test -d /opt/fuzzenv/src/cronie-1.5.7; \
    test -d /opt/fuzzenv/src/shadow-4.8.1; \
    test -d /opt/course/exercises/full-cycle/solution; \
    test -f /opt/course/exercises/full-cycle/task.md; \
    rm -f /tmp/smoke.c /tmp/smoke; \
    echo IMAGE_SMOKE_OK

WORKDIR /opt/fuzzenv
CMD ["sleep", "infinity"]
