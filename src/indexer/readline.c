/*##############################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# readline.c is part of mwetoolkit
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
#include <string.h>
#include "readline.h"

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
