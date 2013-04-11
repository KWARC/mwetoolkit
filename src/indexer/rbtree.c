/*##############################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# rbtree.c is part of mwetoolkit
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

// rbtree.c - Red-black tree.
// Taken from http://inf.ufrgs.br/~vbuaraujo/sw/runespell/ .

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "base.h"

typedef char *rbkey_t;
typedef int rbvalue_t;

// Node structure.
typedef struct rbnode_t {
	rbkey_t key;
	rbvalue_t value;
	bool isred;
	struct rbnode_t *parent, *left, *right;
} rbnode_t;

// Tree descriptor.
typedef struct rbtree_t {
	rbnode_t *root;
	rbnode_t *greatest;
} rbtree_t;

// Creates an empty tree.
rbtree_t *rbmake() {
	rbtree_t *new;

	new = alloc(1, rbtree_t);
	new->root = NULL;
	return new;
}

// Inserts a node in a tree; returns the node.
// If a node with the specified key already exists, return it untouched
// (ignoring 'value').
rbnode_t *rbinsert(rbtree_t *t, rbkey_t key, rbvalue_t value) {
	rbnode_t *this, *parent;
	int cmp;
	void rbbalance(rbtree_t *t, rbnode_t *this);
	
	this = t->root;
	parent = NULL;

	while (this) {
		parent = this;
		cmp = strcmp(key, this->key);
		if (cmp==0) {
			return this;
		} else if (cmp<0)
			this = this->left;
		else
			this = this->right;
	}

	this = alloc(1, rbnode_t);
	this->parent = parent;
	this->left = this->right = NULL;
	this->isred = true;
	//strncpy(this->key, key, WORDLEN-1);
	this->key = key;
	this->value = value;

	if (!parent) {
		t->root = this;
	}
	else {
		if (cmp<0)
			parent->left = this;
		else
			parent->right = this;
	}

	rbbalance(t, this);
	return this;
}

// Rebalances the tree from the specified node.
void rbbalance(rbtree_t *t, rbnode_t *this) {
	rbnode_t *parent, *uncle, *granpa;
	if (!(parent = this->parent)) {
		this->isred = false;
		return;
	}
	if (!parent->isred)
		return;
	granpa = parent->parent;
	uncle = (parent == granpa->left? granpa->right : granpa->left);
	if (uncle && uncle->isred) {
		uncle->isred = false;
		parent->isred = false;
		granpa->isred = true;
		rbbalance(t, granpa);
		return;
	}

	if (this == parent->right && parent == granpa->left) {
		if (parent->right = this->left)
			parent->right->parent = parent;
		this->left = parent;
		parent->parent = this;
		this->parent = granpa;
		granpa->left = this;
		this = parent;
		parent = this->parent;
	} else if (this == parent->left && parent == granpa->right) {
		if (parent->left = this->right)
			parent->left->parent = parent;
		this->right = parent;
		parent->parent = this;
		this->parent = granpa;
		granpa->right = this;
		this = parent;
		parent = this->parent;
	}

	if (this == parent->left && parent == granpa->left) {
		if (granpa->left = parent->right)
			granpa->left->parent = granpa;
		parent->right = granpa;
		parent->parent = granpa->parent;
		granpa->parent = parent;
		parent->left = this;
		if (parent->parent)
			if (parent->parent->left == granpa)
				parent->parent->left = parent;
			else
				parent->parent->right = parent;
		parent->isred = false;
		granpa->isred = true;
		if (t->root == granpa) t->root = parent;
	} else if (this == parent->right && parent == granpa->right) {
		if (granpa->right = parent->left)
			granpa->right->parent = granpa;
		parent->left = granpa;
		parent->parent = granpa->parent;
		granpa->parent = parent;
		parent->right = this;
		if (parent->parent)
			if (parent->parent->left == granpa)
				parent->parent->left = parent;
			else
				parent->parent->right = parent;
		parent->isred = false;
		granpa->isred = true;
		if (t->root == granpa) t->root = parent;
	} else {
		error("-- Found tree in inconsistent state!\n");
	}
}

// Find an element in the tree. Returns NULL if not found.
rbnode_t *rbfind(rbtree_t *t, rbkey_t key) {
	rbnode_t *this;
	int cmp;

	this = t->root;
	while (this) {
		cmp = strcmp(key, this->key);
		if (cmp==0)
			return this;
		else if (cmp<0)
			this = this->left;
		else
			this = this->right;
	}
	return NULL;
}

// Print all words contained in the tree.
// FIXME: make it receive a stream as argument. This is actually
// useful for more than debugging...
void rbprintsub(rbnode_t *this) {
	if (this) {
		rbprintsub(this->left);
		printf("%s\n", this->key);
		rbprintsub(this->right);
	}
}
void rbprint(rbtree_t *t) {
	rbprintsub(t->root);
}


// Frees the tree's memory.
void rbfreesub(rbnode_t *this) {
	if (this) {
		rbfreesub(this->left);
		rbfreesub(this->right);
		dealloc(this);
	}
}

void rbfree(rbtree_t *t) {
	rbfreesub(t->root);
	rbfree(t);
}

////// This won't be used, I believe.

// Move um nó para outra árvore, usando nodecmp como critério de ordenação.
rbnode_t *rbmoveto(rbtree_t *t, rbnode_t *node, int (*nodecmp)(rbnode_t *, rbnode_t *)) {
	int cmp;
	rbnode_t *this, *parent;

	this = t->root;
	parent = NULL;

	while (this) {
		parent = this;
		cmp = nodecmp(node, this);
		if (cmp==0) {
			return this;
		} else if (cmp<0)
			this = this->left;
		else
			this = this->right;
	}

	if (!parent) {
		t->root = node;
	}
	else {
		if (cmp<0)
			parent->left = node;
		else
			parent->right = node;
	}
	node->parent = parent;
	node->isred = true;
	rbbalance(t, node);
	return node;
}

// Retorna a árvore ordenada segundo nodecmp.
// Destrói a árvore original.

void rbreordersub(rbnode_t *this, rbtree_t *new, int (*cmp)(rbnode_t *, rbnode_t *)) {
	if (this) {
		rbreordersub(this->left, new, cmp);
		rbreordersub(this->right, new, cmp);
		this->left = NULL;
		this->right = NULL;
		rbmoveto(new, this, cmp);
	}
}

rbtree_t *rbreorder(rbtree_t *t, int (*cmp)(rbnode_t *, rbnode_t *)) {
	rbtree_t new;

	new.root = NULL;
	new.greatest = NULL;

	rbreordersub(t->root, &new, cmp);
	t->root = new.root;
	t->greatest = NULL;
	return t;
}
