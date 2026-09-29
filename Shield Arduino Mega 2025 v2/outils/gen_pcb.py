#!/usr/bin/env python3
# Construit le PCB du Shield Mega 2025 v2 avec l'API pcbnew de KiCad 9 :
# contour, empreintes, nets, routage manuel des alimentations, vias de masse et
# keepouts temporaires pour l'autorouteur.
# Usage (dans le chroot) : python3 gen_pcb.py <fichier.kicad_pcb>
import os, sys, uuid, json
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as D
from place import PL, BX0, BY0, BX1, BY1
import route as R

OUT = sys.argv[1]
PRJDIR = os.path.dirname(os.path.abspath(OUT))
KFP = "/usr/share/kicad/footprints/"
MM = pcbnew.FromMM
NS = uuid.UUID("5a1e1d25-0000-4000-8000-000000000025")
LAY = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}


def U(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def libpath(lib):
    if lib == "JDG2025":
        return os.path.join(PRJDIR, "JDG2025.pretty")
    return KFP + lib + ".pretty"


board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(2)
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(1.6))

# ---------- contour ----------
for (x0, y0, x1, y1) in [(BX0, BY0, BX1, BY0), (BX1, BY0, BX1, BY1), (BX1, BY1, BX0, BY1), (BX0, BY1, BX0, BY0)]:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(V(x0, y0)); s.SetEnd(V(x1, y1))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    board.Add(s)

# ---------- nets ----------
netobj = {}
for name in sorted(D.nets()):
    n = pcbnew.NETINFO_ITEM(board, name)
    board.Add(n)
    netobj[name] = n

# ---------- empreintes ----------
for c in D.C:
    ref = c["ref"]
    lib, name = c["fp"].split(":")
    fp = pcbnew.FootprintLoad(libpath(lib), name)
    if fp is None:
        raise SystemExit("empreinte introuvable " + c["fp"])
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    board.Add(fp)
    x, y, r = PL[ref]
    fp.SetPosition(V(x, y))
    fp.SetOrientationDegrees(r)
    fp.SetReference(ref)
    fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH("/" + U("sym", ref)))
    for k in ("MPN", "LCSC"):
        if c["extra"].get(k):
            fp.SetField(k, c["extra"][k])
            f = fp.GetFieldByName(k)
            f.SetVisible(False)
            f.SetLayer(pcbnew.F_Fab)
    if c["extra"].get("dnp"):
        fp.SetDNP(True)
        fp.SetExcludedFromBOM(True)
        fp.SetExcludedFromPosFiles(True)
    for pad in fp.Pads():
        net = c["pins"].get(pad.GetNumber())
        if net:
            pad.SetNet(netobj[net])

# ---------- routage manuel ----------
for net, lay, w, pts in R.T:
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        tr = pcbnew.PCB_TRACK(board)
        tr.SetStart(V(x0, y0)); tr.SetEnd(V(x1, y1))
        tr.SetWidth(MM(w)); tr.SetLayer(LAY[lay]); tr.SetNet(netobj[net])
        tr.SetLocked(True)
        board.Add(tr)
for net, x, y in R.V:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(V(x, y)); via.SetWidth(MM(0.6)); via.SetDrill(MM(0.3))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(netobj[net])
    via.SetLocked(True)
    board.Add(via)

# ---------- keepouts temporaires (nommes KO_*) ----------
for i, poly in enumerate(R.KO):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName("KO_%d" % i)
    z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowCopperPour(False)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu)
    z.SetLayerSet(ls)
    ol = z.Outline(); ol.NewOutline()
    for x, y in poly:
        ol.Append(MM(x), MM(y))
    board.Add(z)

pcbnew.SaveBoard(OUT, board)

# ---------- classes de nets et regles (fichier projet) ----------
pro = os.path.splitext(OUT)[0] + ".kicad_pro"
d = json.load(open(pro))
cls = d["net_settings"]["classes"]
base = dict(cls[0])
base.update(track_width=0.25, clearance=0.2, via_diameter=0.6, via_drill=0.3)
cls[0] = base
for name, tw, cl in [("Alim", 0.5, 0.2), ("Puissance", 1.5, 0.3)]:
    c = dict(base); c.update(name=name, track_width=tw, clearance=cl, priority=0 if name == "Puissance" else 1)
    cls.append(c)
d["net_settings"]["netclass_patterns"] = [
    {"netclass": "Alim", "pattern": p} for p in ("+5V", "5V_BUCK", "V12", "SW5")
] + [{"netclass": "Puissance", "pattern": p} for p in ("VBAT", "VBAT_IN", "+6V", "SW6")]
rules = d["board"]["design_settings"]["rules"]
rules.update(min_clearance=0.2, min_track_width=0.2, min_via_diameter=0.5, min_through_hole_diameter=0.3,
             min_copper_edge_clearance=0.3, min_hole_clearance=0.25, min_hole_to_hole=0.25,
             min_via_annular_width=0.1, min_silk_clearance=0.0)
json.dump(d, open(pro, "w"), indent=2)
print("ok", len(D.C), "empreintes,", len(R.T), "pistes,", len(R.V), "vias")
