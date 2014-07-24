/*##############################################################################
#
# Copyright 2011 Carlos Ramisch, Vitor De Araujo
#
# basefuns.c is part of mwetoolkit
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
#include <stdlib.h>
#include "base.h"

void *check_malloc(size_t size) {
	void *new = malloc(size);
	if (!new)
		error("Error allocating %d bytes!\n", (int)size);
	return new;
}

void *check_realloc(void *ptr, size_t size) {
	void *new = realloc(ptr, size);
	if (!new)
		error("Error reallocating %d bytes!\n", (int)size);
	return new;
}

