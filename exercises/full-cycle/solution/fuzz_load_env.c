/* fuzz_load_env.c
 * Target:   cronie-1.5.7 — load_env()  (src/env.c:181, CCN 31 по lizard)
 * Функция:  int load_env(char *envstr, FILE *f)
 *           читает одну строку из f в envstr и разбирает её как
 *           assignment переменного окружения crontab (NAME=VALUE,
 *           кавычки, экранирование, состояния NAMEI/.../ERROR).
 *
 * Один файл на оба фаззера:
 *   - AFL/AFL++   : __AFL_FUZZ_TESTCASE_BUF (persistent mode, __AFL_LOOP)
 *   - libFuzzer   : LLVMFuzzerTestOneInput
 *
 * Сборка: см. Makefile (цели libfuzzer и afl).
 *
 * Корпус: см. ../seed/ (валидные crontab-строки с переменными окружения).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/*
 * MAIN_PROGRAM: режим «определения» глобальных в globals.h (cronie хранит
 * их в globals.h и определяет ровно в одном main-файле — у нас это обёртка).
 * Без этого линковка падает на undefined reference к LineNumber и др.
 */
#ifndef MAIN_PROGRAM
#  define MAIN_PROGRAM
#endif

/* Заголовки cronie: порядок как в референсе fuzz_load_entry.c */
#include "config.h"
#include "macros.h"
#include "globals.h"

/* Сигнатуры из src/env.c / src/misc.c (в 1.5.7 отдельных заголовков нет) */
int  load_env(char *envstr, FILE *f);
extern int LineNumber;

/*
 * do_fuzz() — общая логика для обоих фаззеров.
 *
 * Ключевой приём: fmemopen() превращает сырые байты фаззера в FILE*,
 * поэтому load_env() видит «обычный файл» и не знает, что её фаззят.
 *
 * LineNumber — глобальный счётчик строк в misc.c; сбрасываем на каждой
 * итерации, иначе состояние накапливается между запусками (антипаттерн,
 * см. course.md, раздел обёрток).
 */
static void do_fuzz(const unsigned char *data, size_t size) {
    static char envstr[MAX_ENVSTR + 16];

    LineNumber = 0;

    FILE *f = fmemopen((void *)data, size, "r");
    if (!f)
        return;

    /* Возвратные коды: ERR = EOF, FALSE = не переменная (f перемотана),
     * TRUE = разобрано. Для фаззинга важен только пройденный путь. */
    load_env(envstr, f);

    fclose(f);
}

#ifdef __AFL_FUZZ_TESTCASE_BUF
/* ------------------------- AFL / AFL++ branch ------------------------- */
/* Всё, что нужно этой ветке (макросы __AFL_INIT/__AFL_LOOP/__AFL_FUZZ_INIT,
 * __AFL_FUZZ_TESTCASE_BUF/LEN), подставляет сам afl-clang-fast при компиляции.
 * Заголовки включать не нужно. Ветка собирается ТОЛЬКО компилятором AFL —
 * в «обычной» сборке __AFL_FUZZ_TESTCASE_BUF не определено. */
int main(void) {
    __AFL_INIT();          /* инициализация: shared memory, fork server */
    __AFL_FUZZ_INIT();     /* декларации ptr/len + fallback-буфер на stdin */

    unsigned char *tbuf = (unsigned char *)__AFL_FUZZ_TESTCASE_BUF;

    while (__AFL_LOOP(10000)) {
        size_t len = __AFL_FUZZ_TESTCASE_LEN;
        if (len == 0)
            continue;
        do_fuzz(tbuf, len);
    }
    return 0;
}
#else
/* -------------------------- libFuzzer branch -------------------------- */
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size == 0)
        return 0;
    do_fuzz(data, size);
    return 0;
}
#endif
