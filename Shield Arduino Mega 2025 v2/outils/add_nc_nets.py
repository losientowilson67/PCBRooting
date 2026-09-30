#!/usr/bin/env python3
# Donne aux broches non connectees du PCB les nets "unconnected-(...)" crees par le schema,
# comme le ferait "Mettre a jour le PCB depuis le schema" (parite schema/PCB sans ecart).
# Usage (chroot) : python3 add_nc_nets.py <netlist.net> <in.kicad_pcb> <out.kicad_pcb>
import re, sys
import pcbnew

NET, SRC, DST = sys.argv[1:4]
txt = open(NET, encoding="utf-8").read()
want = {}
name = None
for line in txt.splitlines():
    m = re.search(r'\(net \(code "\d+"\) \(name "([^"]*)"\)', line)
    if m:
        name = m.group(1)
    m = re.search(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', line)
    if m and name and name.startswith("unconnected-"):
        want[(m.group(1), m.group(2))] = name

board = pcbnew.LoadBoard(SRC)
nets = {}
n = 0
for fp in board.GetFootprints():
    for pad in fp.Pads():
        key = (fp.GetReference(), pad.GetNumber())
        if key in want and pad.GetNetCode() == 0:
            name = want[key]
            if name not in nets:
                ni = pcbnew.NETINFO_ITEM(board, name)
                board.Add(ni)
                nets[name] = ni
            pad.SetNet(nets[name])
            n += 1
print("broches NC :", n, "sur", len(want), "/ nets :", len(nets))
# broches empilees dans le symbole (VIN_1/VIN_2, 3V3_1/3V3_2 : meme noeud dans le module) :
# une courte piste F.Cu les relie pour que le PCB corresponde au schema
pads = {}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() in nets:
            pads.setdefault(pad.GetNetname(), []).append(pad)
for name, pl in pads.items():
    for a, b in zip(pl, pl[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(a.GetPosition()); t.SetEnd(b.GetPosition())
        t.SetWidth(pcbnew.FromMM(0.4)); t.SetLayer(pcbnew.F_Cu); t.SetNet(nets[name])
        board.Add(t)
        print("liaison", name)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(DST, board)
