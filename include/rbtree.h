#ifndef MWETK_RBTREE
#define MWETK_RBTREE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "base.h"

typedef char *rbkey_t;

typedef int rbvalue_t;

typedef struct rbnode_t {
	rbkey_t key;
	rbvalue_t value;
	bool isred;
	struct rbnode_t *parent, *left, *right;
} rbnode_t;

typedef struct rbtree_t {
	rbnode_t *root;
	rbnode_t *greatest;
} rbtree_t;

rbtree_t *rbmake();

rbnode_t *rbinsert(rbtree_t *t, rbkey_t key, rbvalue_t value);

void rbbalance(rbtree_t *t, rbnode_t *this);

rbnode_t *rbfind(rbtree_t *t, rbkey_t key);

void rbprintsub(rbnode_t *this);

void rbprint(rbtree_t *t);

void rbfreesub(rbnode_t *this);

void rbfree(rbtree_t *t);

rbnode_t *rbmoveto(rbtree_t *t, rbnode_t *node, int (*nodecmp)(rbnode_t *, rbnode_t *));

void rbreordersub(rbnode_t *this, rbtree_t *new, int (*cmp)(rbnode_t *, rbnode_t *));

rbtree_t *rbreorder(rbtree_t *t, int (*cmp)(rbnode_t *, rbnode_t *));

#endif
