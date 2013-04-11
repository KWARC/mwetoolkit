/*##############################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# symboltable.c is part of mwetoolkit
#
# mwetoolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mwetoolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mwetoolkit.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################*/

#include <stdio.h>
#include "base.h"
#include "rbtree.h"
#include "readline.h"

typedef int symbolnumber_t;
typedef char *symbolname_t;

// Symbol table descriptor.
typedef struct symboltable_t {
	int numentries;
	int allocated_entries;
	rbtree_t *name_to_number;
	symbolname_t *number_to_name;
} symboltable_t;
	

symboltable_t *make_symboltable() {
	symbolnumber_t intern_symbol(symboltable_t *table, symbolname_t key);

	symboltable_t *new = alloc(1, symboltable_t);
	symbolname_t empty_symbol = alloc(1, char);
	empty_symbol[0] = '\0';
	new->numentries = 0;
	new->allocated_entries = 0;
	new->name_to_number = rbmake();
	new->number_to_name = NULL;
	intern_symbol(new, empty_symbol);
	return new;
}

void free_symboltable(symboltable_t *table) {
	int i;
	rbfree(table->name_to_number);
	for (i=0; i < table->numentries; i++)
		free(table->number_to_name[i]);
	free(table->number_to_name);
	free(table);
}

symbolnumber_t intern_symbol(symboltable_t *table, symbolname_t key) {
	rbnode_t *node = rbinsert(table->name_to_number, key, table->numentries);
	if (node->value == table->numentries) {
		if (table->numentries >= table->allocated_entries) {
			resize_alloc(table->number_to_name,
			             table->allocated_entries + SYMBOL_ENTRY_ALLOC_CHUNK,
			             symbolname_t);
			table->allocated_entries += SYMBOL_ENTRY_ALLOC_CHUNK;
		}
		table->number_to_name[table->numentries] = key;
		table->numentries++;
	}
	else {
		free(key);
	}
	return node->value;
}

void write_symbols(symboltable_t *table, FILE *file) {
	int i;
	for (i=0; i < table->numentries; i++) {
		fprintf(file, "%s\n", table->number_to_name[i]);
	}
}

void read_symbols(symboltable_t *table, FILE *file) {
	char *line, *newname;
	/*int length;*/

	while (line = readline(file)) {
		newname = copystring(line);
		intern_symbol(table, newname);
	}
}

void load_symbols_from_file(symboltable_t *table, char *basepath) {
	char path[strlen(basepath) + 8 + 1];
	strcpy(path, basepath);
	strcat(path, ".symbols");
	FILE *file = fopen(path, "r");
	if (!file)
		error("-- Error opening symbols file for reading!\n");
	read_symbols(table, file);
	fclose(file);
}

void save_symbols_to_file(symboltable_t *table, char *basepath) {
	char path[strlen(basepath) + 8 + 1];
	strcpy(path, basepath);
	strcat(path, ".symbols");
	FILE *file = fopen(path, "w");
	if (!file)
		error("-- Error opening symbols file for writing!\n");
	write_symbols(table, file);
	fclose(file);
}

