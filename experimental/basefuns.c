#include <stdio.h>
#include <stdlib.h>
#import "base.h"

inline void *check_malloc(size_t size) {
	void *new = malloc(size);
	if (!new)
		error("Error allocating %d bytes!\n", size);
	return new;
}

inline void *check_realloc(void *ptr, size_t size) {
	void *new = realloc(ptr, size);
	if (!new)
		error("Error reallocating %d bytes!\n", size);
	return new;
}

