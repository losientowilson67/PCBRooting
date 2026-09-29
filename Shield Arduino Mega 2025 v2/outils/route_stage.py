#!/usr/bin/env python3
# Etape de routage : export DSN -> Freerouting -> import SES -> sauvegarde du PCB route.
# Les pistes/vias de masse manuelles sont remplacees par des keepouts pendant l'autoroutage
# (la masse sera faite par les plans), puis remises apres l'import.
# Usage (chroot) : python3 route_stage.py <pre.kicad_pcb> <passes|ses> [zones_B_interdites]
import os, sys, re, math, subprocess
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route as R

PRE = sys.argv[1]
PASSES = sys.argv[2] if len(sys.argv) > 2 else "40"
BKO = sys.argv[3] if len(sys.argv) > 3 else ""
WORK = os.path.dirname(os.path.abspath(PRE))
MM = pcbnew.FromMM
dsn = os.path.join(WORK, "route.dsn")
ses = os.path.join(WORK, "route.ses")


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def rule_area(board, pts, layers, name):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowCopperPour(False)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    for x, y in pts:
        z.AppendCorner(V(x, y), -1)
    board.Add(z)


if PASSES != "ses":
    board = pcbnew.LoadBoard(PRE)
    gnd = board.FindNet("GND")
    # masse manuelle -> keepouts temporaires
    for tr in list(board.GetTracks()):
        if tr.GetNetCode() != gnd.GetNetCode():
            continue
        if tr.GetClass() == "PCB_VIA":
            x, y = pcbnew.ToMM(tr.GetPosition().x), pcbnew.ToMM(tr.GetPosition().y)
            r = 0.55
            pts = [(x + r * math.cos(a * math.pi / 4), y + r * math.sin(a * math.pi / 4)) for a in range(8)]
            rule_area(board, pts, [pcbnew.F_Cu, pcbnew.B_Cu], "TMPV")
        else:
            x0, y0 = pcbnew.ToMM(tr.GetStart().x), pcbnew.ToMM(tr.GetStart().y)
            x1, y1 = pcbnew.ToMM(tr.GetEnd().x), pcbnew.ToMM(tr.GetEnd().y)
            h = pcbnew.ToMM(tr.GetWidth()) / 2 + 0.2
            L = math.hypot(x1 - x0, y1 - y0) or 1e-6
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            nx, ny = -uy * h, ux * h
            pts = [(x0 - ux * h + nx, y0 - uy * h + ny), (x1 + ux * h + nx, y1 + uy * h + ny),
                   (x1 + ux * h - nx, y1 + uy * h - ny), (x0 - ux * h - nx, y0 - uy * h - ny)]
            rule_area(board, pts, [tr.GetLayer()], "TMPT")
        board.Remove(tr)
    # les pistes deja routees (passe precedente) sont figees
    for tr in board.GetTracks():
        tr.SetLocked(True)
    # zones ou B.Cu est interdit aux pistes (plan de masse a preserver)
    for poly in (R.BKO if BKO == "bko" else R.BKO2 if BKO == "bko2" else []):
        rule_area(board, poly, [pcbnew.B_Cu], "TMPB")
    ok = pcbnew.ExportSpecctraDSN(board, dsn)
    print("export dsn", ok)
    txt = open(dsn).read()
    # nets geres par des zones : on garde une seule broche -> rien a router
    for net in R.NO_AUTOROUTE:
        pat = re.compile(r'(\(net\s+"?%s"?\s*\n?\s*\(pins\s+)(\S+)[^)]*(\))' % re.escape(net))
        txt, n = pat.subn(r"\1\2\3", txt)
        print("net reduit a une broche dans le DSN", net, n)
    open(dsn, "w").write(txt)
    if os.path.exists(ses):
        os.remove(ses)
    cmd = ["java", "-Djava.awt.headless=true", "-jar", os.environ.get("FREEROUTING_JAR", "/opt/fr/freerouting-2.4.1-executable.jar"),
           "-de", dsn, "-do", ses, "-mp", PASSES, "--gui.enabled=false",
           "--usage_and_diagnostic_data.disable_analytics=true"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=5400)
    log = p.stdout + p.stderr
    open(os.path.join(WORK, "freerouting.log"), "w").write(log)
    print("\n".join(l for l in log.splitlines() if "stage completed" in l or "Stopping the auto" in l))
    if not os.path.exists(ses):
        raise SystemExit("pas de SES produit")

# import dans une copie propre du PCB pre-route, puis remise de la masse manuelle
board = pcbnew.LoadBoard(PRE)
for tr in board.GetTracks():
    tr.SetLocked(True)
ok = pcbnew.ImportSpecctraSES(board, ses)
print("import ses", ok)
have = {(round(pcbnew.ToMM(t.GetPosition().x), 3), round(pcbnew.ToMM(t.GetPosition().y), 3))
        for t in board.GetTracks() if t.GetClass() == "PCB_VIA"}
gnd = board.FindNet("GND")
LAY = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}
nt = nv = 0
for net, x, y in R.V:
    if net == "GND" and (round(x, 3), round(y, 3)) not in have:
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(V(x, y)); via.SetWidth(MM(0.6)); via.SetDrill(MM(0.3))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(gnd); via.SetLocked(True)
        board.Add(via); nv += 1
gtracks = {(round(pcbnew.ToMM(t.GetStart().x), 3), round(pcbnew.ToMM(t.GetStart().y), 3))
           for t in board.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetCode() == gnd.GetNetCode()}
for net, lay, w, pts in R.T:
    if net != "GND":
        continue
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if (round(x0, 3), round(y0, 3)) in gtracks:
            continue
        tr = pcbnew.PCB_TRACK(board)
        tr.SetStart(V(x0, y0)); tr.SetEnd(V(x1, y1)); tr.SetWidth(MM(w))
        tr.SetLayer(LAY[lay]); tr.SetNet(gnd); tr.SetLocked(True)
        board.Add(tr); nt += 1
print("masse remise :", nv, "vias,", nt, "pistes")
routed = os.path.join(WORK, "routed.kicad_pcb")
pcbnew.SaveBoard(routed, board)
print("route sauve", routed)
