#!/usr/bin/env python3
# Genere le schema KiCad 9 (.kicad_sch) du Shield Mega 2025 v2 a partir de design.py.
import math, re, sys, uuid, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import parse, find, find1
import design as D

KLIB = os.environ.get("KICAD9_SYMBOL_DIR", "/usr/share/kicad/symbols").rstrip("/") + "/"
_here = os.path.dirname(os.path.abspath(__file__))
PLIB = next(p for p in (os.path.join(_here, "JDG2025.kicad_sym"),
                        os.path.join(_here, "..", "MachineJDG2025_MEGA2560_Shield_v2", "JDG2025.kicad_sym"))
            if os.path.exists(p))
OUT = sys.argv[1]
NS = uuid.UUID("5a1e1d25-0000-4000-8000-00000000jdg0".replace("jdg0", "0025"))
ROOT = str(uuid.uuid5(NS, "root"))


def U(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


# ---------- serialisation s-expr ----------
def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def dump(x, ind=0):
    if not isinstance(x, list):
        return x
    # atomes: on re-quote les chaines qui en ont besoin
    parts = []
    for i, e in enumerate(x):
        if isinstance(e, list):
            parts.append(None)
        else:
            parts.append(e)
    return x


def ser(node, ind=1):
    """Serialise une liste parsee (les chaines sont re-quotees si besoin)."""
    if not isinstance(node, list):
        s = node
        if s == "" or re.search(r'[\s()"]', s) or not re.match(r'^[A-Za-z0-9_.+\-/:*~#$%&@!?<>=,\[\]{}|^]+$', s):
            return q(s)
        return s
    head = [ser(e, ind + 1) for e in node if not isinstance(e, list)]
    kids = [e for e in node if isinstance(e, list)]
    if not kids:
        return "(" + " ".join(head) + ")"
    out = "(" + " ".join(head)
    for k in kids:
        out += "\n" + "\t" * ind + ser(k, ind + 1)
    out += "\n" + "\t" * (ind - 1) + ")"
    return out


# certaines chaines doivent rester quotees meme si "simples" (valeurs de proprietes, noms)
QUOTE_KEYS = {"property", "lib_id", "name", "number", "reference", "project", "path", "title", "date", "rev",
              "company", "comment", "page", "text", "label", "uuid", "generator", "generator_version", "paper",
              "symbol", "extends", "lib_name"}


def fix_quotes(node):
    """Marque les chaines a quoter (en les entourant d'un objet Q)."""
    return node


class Q(str):
    pass


def serq(node, ind=1):
    if not isinstance(node, list):
        if isinstance(node, Q):
            return q(node)
        return ser(node)
    head = [serq(e, ind + 1) for e in node if not isinstance(e, list)]
    kids = [e for e in node if isinstance(e, list)]
    if not kids:
        return "(" + " ".join(head) + ")"
    out = "(" + " ".join(head)
    for k in kids:
        out += "\n" + "\t" * ind + serq(k, ind + 1)
    out += "\n" + "\t" * (ind - 1) + ")"
    return out


def requote(node):
    """Apres parse, les chaines quotees perdent leur quote : on les remet selon la cle."""
    if not isinstance(node, list):
        return node
    key = node[0] if node and not isinstance(node[0], list) else None
    out = [key] if key is not None else []
    rest = node[1:] if key is not None else node
    for i, e in enumerate(rest):
        if isinstance(e, list):
            out.append(requote(e))
        elif key in QUOTE_KEYS and (key != "property" or i < 2) and (key != "text" or i < 1) and (key != "pin" or False):
            out.append(Q(e))
        elif key in ("name", "number") and i == 0:
            out.append(Q(e))
        else:
            out.append(e)
    return out


# ---------- symboles de librairie ----------
_libcache = {}


def libsyms(path):
    if path not in _libcache:
        L = parse(open(path).read())
        _libcache[path] = {s[1]: s for s in find(L, "symbol")}
    return _libcache[path]


def get_lib_symbol(lib_id):
    lib, name = lib_id.split(":")
    path = PLIB if lib == "JDG2025" else KLIB + lib + ".kicad_sym"
    syms = libsyms(path)
    s = syms[name]
    ext = find1(s, "extends")
    if ext:
        parent = get_flat(syms, ext[1])
        props = [p for p in find(s, "property")]
        pnames = {p[1] for p in props}
        body = []
        for e in parent[2:]:
            if isinstance(e, list) and e[0] == "property" and e[1] in pnames:
                continue
            if isinstance(e, list) and e[0] == "symbol":
                e = [e[0], e[1].replace(ext[1] + "_", name + "_", 1)] + e[2:]
            body.append(e)
        # proprietes de l'enfant d'abord, puis le reste du parent
        flat = ["symbol", lib_id]
        flags = [e for e in body if isinstance(e, list) and e[0] in ("pin_numbers", "pin_names", "exclude_from_sim", "in_bom", "on_board", "power")]
        others = [e for e in body if e not in flags]
        flat += flags + props + [e for e in others if not (isinstance(e, list) and e[0] == "extends")]
        return flat
    s2 = ["symbol", lib_id] + [e for e in s[2:]]
    return s2


def get_flat(syms, name):
    s = syms[name]
    ext = find1(s, "extends")
    if not ext:
        return s
    parent = get_flat(syms, ext[1])
    props = find(s, "property")
    pn = {p[1] for p in props}
    out = ["symbol", name]
    for e in parent[2:]:
        if isinstance(e, list) and e[0] == "property" and e[1] in pn:
            continue
        if isinstance(e, list) and e[0] == "symbol":
            e = [e[0], e[1].replace(ext[1] + "_", name + "_", 1)] + e[2:]
        out.append(e)
    return out[:2] + props + out[2:]


def pins_of(sym):
    res = []

    def walk(n):
        if isinstance(n, list):
            if n and n[0] == "pin" and find1(n, "number"):
                at = find1(n, "at")
                res.append(dict(num=find1(n, "number")[1], name=find1(n, "name")[1], x=float(at[1]), y=float(at[2]),
                                a=float(at[3]) if len(at) > 3 else 0.0, type=n[1]))
            for c in n:
                walk(c)
    walk(sym)
    return res


# ---------- geometrie ----------
def rot(x, y, r):
    c, s = round(math.cos(math.radians(r))), round(math.sin(math.radians(r)))
    return x * c - y * s, x * s + y * c


def pin_geom(X, Y, r, p):
    px, py = rot(p["x"], p["y"], r)
    ex, ey = X + px, Y - py
    dx, dy = rot(-math.cos(math.radians(p["a"])), -math.sin(math.radians(p["a"])), r)
    return (round(ex, 3), round(ey, 3)), (round(dx), -round(dy))


def fmt(v):
    v = round(v, 4)
    return ("%.4f" % v).rstrip("0").rstrip(".") if v != int(v) else str(int(v))


# ---------- placement (x, y, rotation) en mm, grille 2.54 ----------
G = 2.54
P = {}


def at(ref, x, y, r=0):
    P[ref] = (x * G, y * G, r)


# Bloc entree batterie (haut gauche)
at("J1", 9, 22)
at("F1", 20, 16, 90)
at("D2", 20, 22, 180)
at("D1", 12, 35, 270)
at("C1", 20, 35)
at("C2", 28, 35)
# Bloc 6V
at("U2", 52, 21)
at("L1", 72, 14, 90)
at("R5", 72, 18, 90)
at("C6", 72, 22, 90)
at("R3", 72, 26, 90)
at("R7", 72, 30, 90)
for i, r in enumerate(["C3", "C4", "C5", "R4", "R6"]):
    at(r, 44 + 6 * i, 35)
for i, r in enumerate(["C7", "C8", "C9"]):
    at(r, 44 + 6 * i, 46)
at("D3", 62, 46, 270)
at("LED1", 68, 46, 90)
# Bloc 5V
at("U3", 100, 21)
at("L2", 120, 14, 90)
at("R10", 120, 18, 90)
at("C13", 120, 22, 90)
at("C12", 120, 26, 90)
at("R8", 120, 30, 90)
at("D4", 120, 34, 180)
at("R12", 120, 38, 90)
for i, r in enumerate(["C10", "C11", "R9", "R11"]):
    at(r, 90 + 6 * i, 35)
for i, r in enumerate(["C14", "C15", "C16", "C17"]):
    at(r, 90 + 6 * i, 46)
at("LED2", 114, 46, 90)
# Mesure VBAT
at("R13", 146, 16, 90)
at("R14", 142, 24)
at("C18", 150, 24)
# Module
at("U1", 81, 82)
# Moteurs : resistances serie
for i, r in enumerate(["R20", "R21", "R22", "R23", "R24", "R25", "R26", "R27"]):
    at(r, 46, 58 + 3 * i, 90)
for i, r in enumerate(["R30", "R31", "R32", "R33"]):
    at(r, 10 + 7 * i, 80)
for i, r in enumerate(["J3", "J11", "J5", "J9"]):
    at(r, 8 + 7 * i, 90)
for i, r in enumerate(["J2", "J10", "J4", "J8"]):
    at(r, 8 + 7 * i, 100)
# Servos et SBUS
for i, (s, r) in enumerate([("S1", "R40"), ("S2", "R41"), ("S3", "R42"), ("S4", "R43")]):
    at(s, 142, 58 + 6 * i)
    at(r, 114, 58 + 6 * i, 90)
at("J6", 142, 86)
at("R1", 114, 90, 90)
at("Q1", 124, 96)
at("R2", 130, 92)

# ---------- construction ----------
items = []
lib_ids = []


def prop(name, val, x, y, ang=0, hide=False, justify=None, size=1.27):
    eff = ["effects", ["font", ["size", fmt(size), fmt(size)]]]
    if justify:
        eff.append(["justify"] + justify)
    if hide:
        eff.append(["hide", "yes"])
    return ["property", Q(name), Q(val), ["at", fmt(x), fmt(y), fmt(ang)], eff]


def wire(a, b):
    items.append(["wire", ["pts", ["xy", fmt(a[0]), fmt(a[1])], ["xy", fmt(b[0]), fmt(b[1])]],
                  ["stroke", ["width", "0"], ["type", "default"]], ["uuid", Q(U("w", a, b))]])


def label(net, x, y, d):
    ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[d]
    just = ["left", "bottom"] if ang in (0, 90) else ["right", "bottom"]
    items.append(["label", Q(net), ["at", fmt(x), fmt(y), str(ang)], ["fields_autoplaced", "yes"],
                  ["effects", ["font", ["size", "1.27", "1.27"]], ["justify"] + just], ["uuid", Q(U("l", net, x, y))]])


def noconn(x, y):
    items.append(["no_connect", ["at", fmt(x), fmt(y)], ["uuid", Q(U("nc", x, y))]])


def text(s, x, y, size=1.27, bold=False):
    font = ["font", ["size", fmt(size), fmt(size)]]
    if bold:
        font.append(["bold", "yes"])
    items.append(["text", Q(s), ["exclude_from_sim", "no"], ["at", fmt(x), fmt(y), "0"],
                  ["effects", font, ["justify", "left", "bottom"]], ["uuid", Q(U("t", s, x, y))]])


placed_labels = set()


def place(c):
    ref = c["ref"]
    X, Y, r = P[ref]
    lib = get_lib_symbol(c["lib"])
    if c["lib"] not in lib_ids:
        lib_ids.append(c["lib"])
    pins = pins_of(lib)
    xs, ys = [], []
    seen = set()
    for p in pins:
        (ex, ey), d = pin_geom(X, Y, r, p)
        xs.append(ex); ys.append(ey)
        net = c["pins"].get(p["num"], "__absent__")
        if net == "__absent__":
            raise SystemExit("pin %s.%s absente de design.py" % (ref, p["num"]))
        key = (round(ex, 2), round(ey, 2))
        if key in seen:
            continue
        seen.add(key)
        if net is None:
            noconn(ex, ey)
        else:
            L = 2.54
            e2 = (ex + d[0] * L, ey + d[1] * L)
            wire((ex, ey), e2)
            label(net, e2[0], e2[1], d)
    fa = r % 180
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    lib = c["lib"]
    two = lib in ("Device:R", "Device:C", "Device:C_Polarized", "Device:L", "Device:Fuse")
    diode = lib.startswith(("Device:D", "Diode:", "Device:LED"))
    ang = 90 if fa == 90 else 0
    if (two and fa == 0) or (diode and fa == 90):
        rp, vp, j = (X + 2.032, Y - 1.27), (X + 2.032, Y + 1.27), ["left"]
        if fa == 90:
            rp, vp, j = (X + 5.08, Y - 1.27), (X + 5.08, Y + 1.27), None
    elif two or diode:
        rp, vp, j = (X, Y - 2.286), (X, Y + 2.54), None
    else:
        rp, vp, j = (minx, miny - 3.81), (minx, maxy + 5.08), ["left"]
        if lib.startswith("JDG2025:69"):
            rp, vp = (X - 3.81, Y - 6.35), (X - 3.81, Y - 3.81)
        if lib.startswith("Connector_Generic"):
            rp, vp = (X, Y - 5.08), (X, Y + 5.08)
        if lib.startswith("JDG2025:MEGA"):
            rp, vp = (X - 12.7, Y - 63.5), (X - 12.7, Y + 66.04)
        if lib.startswith("Regulator"):
            rp, vp = (X - 7.62, Y - 8.89), (X + 1.27, Y + 11.43)
        if lib.startswith("Transistor"):
            rp, vp = (X + 5.08, Y - 1.27), (X + 5.08, Y + 1.27)
    dnp = c["extra"].get("dnp", False)
    sym = ["symbol", ["lib_id", Q(c["lib"])], ["at", fmt(X), fmt(Y), str(r)], ["unit", "1"],
           ["exclude_from_sim", "no"], ["in_bom", "no" if dnp else "yes"], ["on_board", "yes"], ["dnp", "yes" if dnp else "no"],
           ["uuid", Q(U("sym", ref))],
           prop("Reference", ref, rp[0], rp[1], ang, justify=j),
           prop("Value", c["value"], vp[0], vp[1], ang, justify=j),
           prop("Footprint", c["fp"], X, Y, 0, hide=True),
           prop("Datasheet", "", X, Y, 0, hide=True),
           prop("Description", "", X, Y, 0, hide=True)]
    for k in ("MPN", "LCSC", "Montage"):
        v = c["extra"].get(k)
        if k == "Montage" and not v:
            v = "CMS" if not dnp else "NE PAS POSER"
        if v:
            sym.append(prop(k, v, X, Y, 0, hide=True))
    for p in pins:
        sym.append(["pin", Q(p["num"]), ["uuid", Q(U("pin", ref, p["num"]))]])
    sym.append(["instances", ["project", Q(D.PROJECT), ["path", Q("/" + ROOT), ["reference", Q(ref)], ["unit", "1"]]]])
    items.append(sym)


for c in D.C:
    place(c)

# PWR_FLAG sur les rails sans source "power_out"
pf = get_lib_symbol("power:PWR_FLAG")
lib_ids.append("power:PWR_FLAG")
for i, net in enumerate(["V12", "GND", "+5V", "VBAT"]):
    X, Y = (138 + 5 * i) * G, 34 * G
    ref = "#FLG0%d" % (i + 1)
    items.append(["symbol", ["lib_id", Q("power:PWR_FLAG")], ["at", fmt(X), fmt(Y), "0"], ["unit", "1"],
                  ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"], ["dnp", "no"],
                  ["uuid", Q(U("flg", net))],
                  prop("Reference", ref, X, Y - 1.905, 0, hide=True),
                  prop("Value", "PWR_FLAG", X, Y - 3.81, 0),
                  prop("Footprint", "", X, Y, 0, hide=True), prop("Datasheet", "~", X, Y, 0, hide=True),
                  prop("Description", "", X, Y, 0, hide=True),
                  ["pin", Q("1"), ["uuid", Q(U("flgpin", net))]],
                  ["instances", ["project", Q(D.PROJECT), ["path", Q("/" + ROOT), ["reference", Q(ref)], ["unit", "1"]]]]])
    wire((X, Y), (X, Y + 2.54))
    label(net, X, Y + 2.54, (0, 1))

# Textes de blocs
T = [
    ("ENTREE BATTERIE 12V (3S) - fusible, TVS, anti-inversion", 6, 10),
    ("REGULATEUR SERVOS 6V / 5A (LM22678-5.0, sortie ~5.95V)", 42, 10),
    ("REGULATEUR LOGIQUE 5V / 2A (TPS54202) -> 5V du module", 94, 10),
    ("MESURE BATTERIE  A0 = V12/4", 138, 10),
    ("MODULE MEGA 2560 PRO EMBED (VIN non utilise : alimente par 5V)", 62, 54),
    ("MOTEURS - commandes PWM/DIR (100R serie) et alimentation", 6, 54),
    ("SERVOS 6V et recepteur SBUS (inverseur -> RX1/D19)", 110, 54),
]
for s, x, y in T:
    text(s, x * G, y * G, 1.778, True)
NOTES = ("Notes :\n"
         "- VBAT = batterie apres F1, alimente les 4 drivers\n"
         "  moteurs (J2, J10, J4, J8).\n"
         "- D1 (TVS) ecrete les pointes des moteurs ; batterie\n"
         "  inversee = D1 conduit et F1 fond.\n"
         "- D2 isole V12 (regulateurs) : anti-inversion et\n"
         "  maintien pendant les creux de tension moteurs.\n"
         "- D4 : le 5V USB ne remonte pas dans le regulateur.\n"
         "- VIN du module non connecte (5V fourni par U3).\n"
         "- R30-R33 : pull-down PWM optionnelles (DNP).\n"
         "- Brochage des connecteurs identique au shield 2025.")
text(NOTES, 6 * G, 66 * G, 1.27)

# ---------- ecriture ----------
libsyms_out = ["lib_symbols"]
for lid in lib_ids:
    s = get_lib_symbol(lid)
    s = [s[0], lid] + s[2:]
    libsyms_out.append(requote(s))

doc = ["kicad_sch", ["version", "20250114"], ["generator", Q("eeschema")], ["generator_version", Q("9.0")],
       ["uuid", Q(ROOT)], ["paper", Q("A3")],
       ["title_block", ["title", Q("Machine JDG 2025 - Shield Mega 2560 PRO v2 (CMS, 2 couches)")],
        ["date", Q("2026-09-29")], ["rev", Q("2.0")], ["company", Q("UQAR - Defi Machine JDG")],
        ["comment", "1", Q("Derive du shield JDG2025 (2024-12-19) : memes connecteurs, meme brochage")],
        ["comment", "2", Q("CMS, 2 couches, plans GND, regulateurs 6V/5V integres, protections")]],
       libsyms_out] + items + [["sheet_instances", ["path", Q("/"), ["page", Q("1")]]], ["embedded_fonts", "no"]]
open(OUT, "w").write(serq(doc) + "\n")
print("ok", len(D.C), "composants,", len(items), "elements")
