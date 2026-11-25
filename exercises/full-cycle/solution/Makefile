# Практика «полный цикл»: сборка обёртки под оба фаззера.
# Пути: исходники cronie — /opt/fuzzenv/src/cronie-1.5.7 (в контейнере).
# Перед сборкой разово (см. task.md):
#   cp /opt/fuzzenv/refs/cronie/config.h.manual      $(SRC)/config.h
#   cp /opt/fuzzenv/refs/cronie/cron-paths.h.manual  $(SRC)/src/cron-paths.h

SRC ?= /opt/fuzzenv/src/cronie-1.5.7
CFLAGS := -g -O1 -DHAVE_CONFIG_H -I$(SRC)/src -I$(SRC)

.PHONY: libfuzzer afl clean

libfuzzer: fuzz_load_env.c
	clang -fsanitize=fuzzer,address $(CFLAGS) \
		fuzz_load_env.c $(SRC)/src/env.c $(SRC)/src/misc.c $(SRC)/src/pw_dup.c \
		-o fuzz_load_env_lf

afl: fuzz_load_env.c
	afl-clang-fast $(CFLAGS) \
		fuzz_load_env.c $(SRC)/src/env.c $(SRC)/src/misc.c $(SRC)/src/pw_dup.c \
		-o fuzz_load_env_afl

clean:
	rm -f fuzz_load_env_lf fuzz_load_env_afl
