SRC := src
INCLUDE := include
LIBS :=
BIN := bin

indexer:
	gcc -Wall -Wno-parentheses -I $(INCLUDE) -o $(BIN)/c-indexer $(SRC)/indexer/*.c

doc: doc/html/index.html

doc/html/index.html:
	mkdir -p doc
	doxygen Doxyfile
	
clean:
	rm -rf doc/html bin/c-indexer
	
