#ifndef MWETK_BASE
#define MWETK_BASE

#include <stdlib.h>
#include "basefuns.h"

#define error(fmt, ...) (fprintf(stderr, fmt, ##__VA_ARGS__), exit(42), 42)
#define alloc(quantity, type) ((type *) check_malloc((quantity) * sizeof(type)))
#define resize_alloc(var, quantity, type) (var = (type *) check_realloc((void *) var, (quantity) * sizeof(type)))

#define dealloc(ptr) (free(ptr), ptr=NULL)

typedef enum bool { false, true } bool;

#define SYMBOL_ENTRY_ALLOC_CHUNK 65536
#define SYMBOL_STRINGS_ALLOC_CHUNK 65536
#define SUFFIX_ARRAY_ALLOC_CHUNK 65536

// This should be dynamic.
#define LINE_BUFFER_LEN 4096

#define NGRAM_COMPARE_LIMIT 16

#endif
