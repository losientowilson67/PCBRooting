#!/usr/bin/env python3
# Convertit les exports KiCad (fab.sh) en BOM + CPL au format JLCPCB (composants CMS seulement).
# Usage : python3 jlc.py <dossier fabrication>
import csv, os, re, sys

F = sys.argv[1]


def expand(des):
    out = []
    for part in des.split(","):
        m = re.fullmatch(r"([A-Z]+)(\d+)-([A-Z]+)(\d+)", part.strip())
        if m:
            out += ["%s%d" % (m.group(1), i) for i in range(int(m.group(2)), int(m.group(4)) + 1)]
        elif part.strip():
            out.append(part.strip())
    return out


rows = list(csv.DictReader(open(os.path.join(F, "bom_raw.csv"), encoding="utf-8")))
cms = set()
with open(os.path.join(F, "BOM_JLCPCB.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for r in rows:
        if r["Montage"] != "CMS":
            continue
        refs = expand(r["Designator"])
        cms.update(refs)
        w.writerow([r["Comment"], ",".join(refs), r["Footprint"].split(":")[-1], r["LCSC Part #"]])
n = 0
with open(os.path.join(F, "CPL_JLCPCB.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for r in csv.DictReader(open(os.path.join(F, "positions_raw.csv"), encoding="utf-8")):
        if r["Ref"] in cms:
            w.writerow([r["Ref"], "%.3fmm" % float(r["PosX"]), "%.3fmm" % float(r["PosY"]),
                        "Top" if r["Side"] == "top" else "Bottom", "%g" % float(r["Rot"])])
            n += 1
os.replace(os.path.join(F, "bom_raw.csv"), os.path.join(F, "BOM_complet.csv"))
os.replace(os.path.join(F, "positions_raw.csv"), os.path.join(F, "positions_kicad.csv"))
missing = sorted(cms - set(r[0] for r in csv.reader(open(os.path.join(F, "CPL_JLCPCB.csv")))))
print("BOM CMS :", len(cms), "composants / CPL :", n, "lignes", ("MANQUANTS " + str(missing)) if missing else "")
