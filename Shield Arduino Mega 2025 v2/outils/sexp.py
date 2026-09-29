import re, sys
tok_re = re.compile(r'\s*(\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+)')
def parse(s):
    pos=0; stack=[[]]
    for m in tok_re.finditer(s):
        t=m.group(1)
        if t=='(':
            stack.append([])
        elif t==')':
            x=stack.pop(); stack[-1].append(x)
        else:
            if t.startswith('"'): t=t[1:-1].replace('\\"','"')
            stack[-1].append(t)
    return stack[0][0]
def find(node, name):
    return [c for c in node if isinstance(c,list) and c and c[0]==name]
def find1(node,name):
    r=find(node,name); return r[0] if r else None
def walk(node, name):
    if isinstance(node,list):
        if node and node[0]==name: yield node
        for c in node: yield from walk(c,name)
def prop(node,key):
    for p in find(node,'property'):
        if p[1]==key: return p[2]
