SRC := src
INCLUDE := include
OBJECTS := src/indexer/basefuns.o src/indexer/readline.o src/indexer/rbtree.o src/indexer/symboltable.o src/indexer/suffixarray.o src/indexer/main.o
LIBS :=
BIN := bin
CC := gcc

all: $(BIN)/c-indexer

$(BIN)/c-indexer: $(OBJECTS)
	$(CC) -Wall -Wno-parentheses -I $(INCLUDE) -o $(BIN)/c-indexer $^

%.o: %.c
	$(CC) -Wall -Wno-parentheses -c -I $(INCLUDE) $^ -o $*.o

doc: doc/html/index.html

doc/html/index.html:
	mkdir -p doc
	doxygen Doxyfile
	
clean:
	rm -rf doc/html bin/c-indexer
	rm $(SRC)/indexer/*.o
	
