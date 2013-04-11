#ifndef MWETK_SYMBOLTABLE
#define MWETK_SYMBOLTABLE

#include <stdio.h>
#include "base.h"
#include "rbtree.h"
#include "readline.h"

typedef int symbolnumber_t;

typedef char *symbolname_t;

typedef struct symboltable_t {
	int numentries;
	int allocated_entries;
	rbtree_t *name_to_number;
	symbolname_t *number_to_name;
} symboltable_t;

symboltable_t *make_symboltable();

void free_symboltable(symboltable_t *table);

symbolnumber_t intern_symbol(symboltable_t *table, symbolname_t key);

void write_symbols(symboltable_t *table, FILE *file);

void read_symbols(symboltable_t *table, FILE *file);

void load_symbols_from_file(symboltable_t *table, char *basepath);

void save_symbols_to_file(symboltable_t *table, char *basepath);

#endif
