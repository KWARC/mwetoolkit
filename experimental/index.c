#include <stdio.h>
#import "base.h"
#import "readline.h"
#import "suffixarray.h"

int main(int argc, char **argv) {
	char *basepath = argv[1];
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

