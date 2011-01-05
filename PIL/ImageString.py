# compatibility module

def find(s, p):
    return s.find(p)

def index(s, p, o=0):
    return s.index(p,o)

def join(seq, sep):
    return sep.join(seq)

def split(s, sep=None, maxsplit=None):
    if sep is None:
        return s.split()
    if maxsplit is None:
        return s.split(sep)
    return s.split(sep, maxsplit)
