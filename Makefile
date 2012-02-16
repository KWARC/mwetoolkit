all: FORCE
	make -C src
	ln -sf ../src/indexer/c-indexer bin/c-indexer

FORCE:
