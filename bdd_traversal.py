from pyeda.inter import *

from graphviz import Source

a, b, c = map(bddvar, 'abc')

f = a & b | a & c | b & c
f.smoothing()

gv = Source(f.to_dot())

gv.render('render_pdf_name',view=True)