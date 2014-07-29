Metadata
========
:UUID: 7d14cd78-c8a6-4e10-b434-d062fc719c14
:Author: silvioricardoc
:Date: 2014-07-29 13:42


To do
=====
CONLL files may have data that we currently (2014-07-29) do not represent in
the XML format.  The files `f1.conll`, `f2.xml` and `f3.xml` exemplify what
happens when we try to convert from such a CONLL representation to XML and back
to CONLL: some data is lost.

* The columns FEATS, PHEAD and PDEPREL are being ignored when converting to XML,
  and become ``_`` when converting to CONLL.
* The column POSTAG is being ignored as well when converting to XML, but a
  value identical to CPOSTAG is used in its place when converting to CONLL.
