#!/usr/bin/env python3
# Etape de routage : export DSN -> Freerouting -> import SES -> zones + plans de masse
# -> vias de couture -> remplissage -> sauvegarde.
# Usage (chroot) : python3 route_stage.py <pre.kicad_pcb> <final.kicad_pcb> [passes]
import os, sys, re, subprocess, shutil
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route as R
from place import BX0, BY0, BX1, BY1

PRE, FINAL = sys.argv[1], sys.argv[2]
PASSES = sys.argv[3] if len(sys.argv) > 3 else "40"
WORK = os.path.dirname(os.path.abspath(PRE))
MM = pcbnew.FromMM
LAY = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


board = pcbnew.LoadBoard(PRE)
dsn = os.path.join(WORK, "route.dsn")
ses = os.path.join(WORK, "route.ses")

if PASSES != "0":
    # ---------- export DSN ----------
    ok = pcbnew.ExportSpecctraDSN(board, dsn)
    print("export dsn", ok)
    txt = open(dsn).read()
    # retire les nets geres par des zones (masse, batterie) du reseau a router
    for net in R.NO_AUTOROUTE:
        pat = re.compile(r'\(net\s+"?%s"?\s*\n?\s*\(pins[^)]*\)\s*\)' % re.escape(net))
        txt, n = pat.subn("", txt)
        print("retire du DSN", net, n)
    open(dsn, "w").write(txt)
    # ---------- Freerouting ----------
    if os.path.exists(ses):
        os.remove(ses)
    cmd = ["java", "-Djava.awt.headless=true", "-jar", "/opt/fr/freerouting-2.4.1-executable.jar",
           "-de", dsn, "-do", ses, "-mp", PASSES, "--gui.enabled=false",
           "--usage_and_diagnostic_data.disable_analytics=true"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3000)
    log = p.stdout + p.stderr
    open(os.path.join(WORK, "freerouting.log"), "w").write(log)
    print("\n".join(l for l in log.splitlines() if "INFO" in l and ("pass" in l.lower() or "unrouted" in l.lower() or "completed" in l.lower()))[-3000:])
    if not os.path.exists(ses):
        raise SystemExit("pas de SES produit")
    ok = pcbnew.ImportSpecctraSES(board, ses)
    print("import ses", ok)

# ---------- retrait des keepouts ----------
for z in list(board.Zones()):
    if z.GetIsRuleArea() and z.GetZoneName().startswith("KO_"):
        board.Remove(z)


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
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    if name:
        z.SetZoneName(name)
    ol = z.Outline(); ol.NewOutline()
    for x, y in poly:
        ol.Append(MM(x), MM(y))
    board.Add(z)
    return z


for net, lay, prio, poly in R.ZONES:
    add_zone(net, [LAY[lay]], prio, poly, 0.3, 1.0)
m = 0.3
outline = [(BX0 + m, BY0 + m), (BX1 - m, BY0 + m), (BX1 - m, BY1 - m), (BX0 + m, BY1 - m)]
gF = add_zone("GND", [pcbnew.F_Cu], 0, outline, 0.25, 0.5, "GND_F")
gB = add_zone("GND", [pcbnew.B_Cu], 0, outline, 0.25, 0.5, "GND_B")

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
filler.Fill(board.Zones())
pcbnew.SaveBoard(FINAL, board)
print("sauve", FINAL)
