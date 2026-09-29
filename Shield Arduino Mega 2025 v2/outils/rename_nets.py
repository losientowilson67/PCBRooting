#!/usr/bin/env python3
# Renomme les nets du PCB comme KiCad les nomme depuis le schema (labels locaux -> "/NOM"),
# pour que "Mettre a jour le PCB depuis le schema" et le DRC de parite ne voient aucune difference.
# Usage : python3 rename_nets.py <in.kicad_pcb> <out.kicad_pcb>
import re, sys

src, dst = sys.argv[1], sys.argv[2]
txt = open(src, encoding="utf-8").read()


def fix(name):
    return name if (not name or name.startswith("/")) else "/" + name


txt = re.sub(r'\(net (\d+) "([^"]*)"\)', lambda m: '(net %s "%s")' % (m.group(1), fix(m.group(2))), txt)
txt = re.sub(r'\(net_name "([^"]*)"\)', lambda m: '(net_name "%s")' % fix(m.group(1)), txt)
open(dst, "w", encoding="utf-8").write(txt)
print("nets renommes ->", dst)
