/*##############################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# main.c is part of mwetoolkit
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
#include "readline.h"
#include "suffixarray.h"

int main(int argc, char **argv) {
	/* char *basepath = argv[1]; */
	char *line;
	char *newsym;

	if (argc != 2)
		error("Usage: %s basepath\n", argv[0]);

	suffixarray_t *suf = make_suffixarray();

	while (line = readline(stdin)) {
		newsym = copystring(line);
		suffixarray_append_word(suf, newsym);
	}

	fprintf(stderr, "Corpus read: %d words.\n", suf->used);
	fprintf(stderr, "Sorting suffix array...\n");
	
	suffixarray_sort(suf);

	fprintf(stderr, "Sorting done! Saving...\n");
	save_suffix_array(suf, argv[1]);
	save_symbols_to_file(suf->symboltable, argv[1]);

	fprintf(stderr, "Done.\n");
	return 0;
}

