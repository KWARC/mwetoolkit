#ifndef MWETK_READLINE
#define MWETK_READLINE

/*!
 * This function reads a line from a file and returns a char array.
 * @param stream The pointer to the file handler.
 * @return The character array with the line, read from a file. In the file, 
 * lines are separated by '\\n'. In the string, the last character is '\0'
 */
char *readline(FILE *stream);

char *copystring(char *str);

#endif
