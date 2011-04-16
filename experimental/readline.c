#include <stdio.h>
#include "base.h"
#include <string.h>

char *readline(FILE *stream) {
	static char buffer[LINE_BUFFER_LEN];
	char *s;

	if (!fgets(buffer, LINE_BUFFER_LEN, stream))
		return NULL;

	for (s=buffer; *s; s++)
		if (*s=='\n')
			*s = '\0';

	return buffer;
}

char *copystring(char *str) {
	int length = strlen(str);
	char *new = alloc(length+1, char);
	strcpy(new, str);
	return new;
}
