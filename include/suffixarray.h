#ifndef MWETK_SUFFIXARRAY
#define MWETK_SUFFIXARRAY

#include <stdio.h>
#include "base.h"
#include "symboltable.h"

typedef struct suffixarray_t {
	symbolnumber_t *corpus;
	symbolnumber_t *suffix;
	symboltable_t *symboltable;
	int allocated;
	int used;
} suffixarray_t;

suffixarray_t* make_suffixarray();

void free_suffixarray(suffixarray_t *suf);

void suffixarray_append_word(suffixarray_t *suf, symbolname_t word);

int suffixarray_compare(suffixarray_t *suf, int pos1, int pos2);

int suffixarray_compare_global(const void *ptr1, const void *ptr2);

void suffixarray_sort(suffixarray_t *suf);

void read_suffix_array(suffixarray_t *suf, FILE *corpusfile, FILE *suffixfile);

void write_suffix_array(suffixarray_t *suf, FILE *corpusfile, FILE *suffixfile);

void load_suffix_array(suffixarray_t *suf, char *basepath);

void save_suffix_array(suffixarray_t *suf, char *basepath);

#endif
