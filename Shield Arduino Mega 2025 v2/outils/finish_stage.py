#!/usr/bin/env python3
# Finition : retrait des keepouts, zones de puissance, plans de masse, vias de couture.
# Usage (chroot) : python3 finish_stage.py <routed.kicad_pcb> <final.kicad_pcb>
import os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route as R
from place import BX0, BY0, BX1, BY1

SRC, FINAL = sys.argv[1], sys.argv[2]
MM = pcbnew.FromMM
LAY = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


board = pcbnew.LoadBoard(SRC)
def add_zone(net, layers, prio, poly, clearance, spoke, name=""):
    z = pcbnew.ZONE(board)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    z.SetNet(board.FindNet(net))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(0.25))
    z.SetThermalReliefGap(MM(0.3))
    z.SetThermalReliefSpokeWidth(MM(spoke))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    if name:
        z.SetZoneName(name)
    for x, y in poly:
        z.AppendCorner(V(x, y), -1)
    board.Add(z)
    return z


# ---------- serigraphie ----------
# reperes gardes en serigraphie (les borniers sont deja nommes par DIR/PWM/+/-)
KEEP_REF = {"J6", "J8", "J9", "S1", "S2", "S3", "S4", "F1"}
for fp in board.GetFootprints():
    ref = fp.Reference()
    if fp.GetReference() in KEEP_REF:
        ref.SetTextSize(pcbnew.VECTOR2I(MM(0.9), MM(0.9))); ref.SetTextThickness(MM(0.15))
    else:
        ref.SetLayer(pcbnew.F_Fab)
    fp.Value().SetLayer(pcbnew.F_Fab)


def silk(s, x, y, h=1.0, ang=0, th=0.18):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(h), MM(h))); t.SetTextThickness(MM(th))
    t.SetTextAngleDegrees(ang)
    board.Add(t)


for s, x, y, h, a in R.SILK:
    silk(s, x, y, h, a, 0.3 if h >= 1.5 else 0.18)

for net, lay, prio, poly in R.ZONES:
    add_zone(net, [LAY[lay]], prio, poly, 0.3, 1.0)
m = 0.3
outline = [(BX0 + m, BY0 + m), (BX1 - m, BY0 + m), (BX1 - m, BY1 - m), (BX0 + m, BY1 - m)]
gF = add_zone("GND", [pcbnew.F_Cu], 0, outline, 0.3, 0.5, "GND_F")
gB = add_zone("GND", [pcbnew.B_Cu], 0, outline, 0.3, 0.5, "GND_B")

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

# ---------- vias de couture GND ----------
gnd = board.FindNet("GND")


def inside(polys, x, y, r):
    pts = [(x, y)] + [(x + r * c, y + r * s) for c, s in
                      [(1, 0), (-1, 0), (0, 1), (0, -1), (.707, .707), (-.707, .707), (.707, -.707), (-.707, -.707)]]
    return all(polys.Contains(V(px, py)) for px, py in pts)


pf = gF.GetFilledPolysList(pcbnew.F_Cu)
pb = gB.GetFilledPolysList(pcbnew.B_Cu)
existing = [(pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y)) for v in board.GetTracks()
            if v.GetClass() == "PCB_VIA"]
step = 3.0
added = 0
y = BY0 + 1.5
while y < BY1 - 1.0:
    x = BX0 + 1.5
    while x < BX1 - 1.0:
        if inside(pf, x, y, 0.62) and inside(pb, x, y, 0.62) and all((x - ex) ** 2 + (y - ey) ** 2 > 2.2 ** 2 for ex, ey in existing):
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(V(x, y)); via.SetWidth(MM(0.6)); via.SetDrill(MM(0.3))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(gnd)
            board.Add(via)
            existing.append((x, y)); added += 1
        x += step
    y += step
print("vias de couture", added)
for z in board.Zones():
    if not z.GetIsRuleArea():
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
filler.Fill(board.Zones())
# origine de percage/placement au coin bas-gauche : Gerbers et CPL en coordonnees positives
board.GetDesignSettings().SetAuxOrigin(V(BX0, BY1))
board.GetDesignSettings().SetGridOrigin(V(BX0, BY1))
# ---------- retrait des keepouts (en dernier : l'API SWIG se degrade apres Remove) ----------
kos = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith("KO_")]
for z in kos:
    board.Remove(z)
pcbnew.SaveBoard(FINAL, board)
print("sauve", FINAL)
