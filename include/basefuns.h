#ifndef MWETK_BASEFUNS
#define MWETK_BASEFUNS

#include <stdio.h>
#include <stdlib.h>
#include "base.h"

// Type of an integer representing a corpus token position (int for small corpora, size_t for large corpora)
typedef unsigned int position_t;

void *check_malloc(position_t size);

void *check_realloc(void *ptr, position_t size);

#endif
