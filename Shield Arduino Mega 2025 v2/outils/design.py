# Definition du Shield Mega 2025 v2 : composants, empreintes, nets.
# Utilise par gen_sch.py (schema) et gen_pcb.py (PCB).

PROJECT = "MachineJDG2025_MEGA2560_Shield_v2"

R0805 = "Resistor_SMD:R_0805_2012Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
TERM = "JDG2025:691214110002"
HDR3 = "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"

# (ref, lib_id, value, footprint, {pin: net}, extra fields)
# net None = pin non connecte (no_connect)
C = []


def add(ref, lib, value, fp, pins, **extra):
    C.append(dict(ref=ref, lib=lib, value=value, fp=fp, pins=pins, extra=extra))


# ---------------- Entree batterie et protections ----------------
add("J1", "JDG2025:691214110002", "BATT 12V", TERM, {"1": "GND", "2": "VBAT_IN"}, Montage="THT")
add("F1", "Device:Fuse", "Fusible mini-lame 10A", "Fuse:Fuseholder_Blade_Mini_Keystone_3568",
    {"1": "VBAT_IN", "2": "VBAT"}, MPN="Keystone 3568 + fusible mini-lame 10A", Montage="THT")
add("D1", "Diode:SMAJ15A", "SMCJ15A", "Diode_SMD:D_SMC", {"1": "VBAT", "2": "GND"},
    MPN="SMCJ15A (TVS 1500W unidirectionnelle 15V)")
add("D2", "Device:D_Schottky", "SS54", "Diode_SMD:D_SMC", {"1": "V12", "2": "VBAT"},
    MPN="SS54 (Schottky 5A 40V) - protection inversion")
add("C1", "Device:C_Polarized", "220uF 35V", "Capacitor_SMD:CP_Elec_8x10.5", {"1": "V12", "2": "GND"},
    MPN="Electrolytique alu CMS 220uF 35V 8x10.5")
add("C2", "Device:C", "100nF 50V", C0805, {"1": "V12", "2": "GND"}, LCSC="C49678")

# ---------------- Regulateur 6V 5A servos (LM22678-5.0 + diviseur) ----------------
add("U2", "Regulator_Switching:LM22678TJ-5", "LM22678TJ-5.0", "Package_TO_SOT_SMD:TO-263-7_TabPin8",
    {"1": "SW6", "2": "V12", "3": "BOOT6", "4": "GND", "5": None, "6": "FB6", "7": "EN6", "8": "GND"},
    MPN="LM22678TJ-5.0/NOPB", LCSC="C527397")
add("R3", "Device:R", "100k", R0805, {"1": "V12", "2": "EN6"}, LCSC="C17407")
add("R4", "Device:R", "33k", R0805, {"1": "EN6", "2": "GND"})
add("C3", "Device:C", "10uF 50V", C1210, {"1": "V12", "2": "GND"})
add("C4", "Device:C", "10uF 50V", C1210, {"1": "V12", "2": "GND"})
add("C5", "Device:C", "100nF 50V", C0805, {"1": "V12", "2": "GND"}, LCSC="C49678")
add("C6", "Device:C", "10nF 50V", C0805, {"1": "BOOT6", "2": "SW6"})
add("D3", "Device:D_Schottky", "PMEG4050EP", "Diode_SMD:D_SOD-128", {"1": "SW6", "2": "GND"},
    MPN="Nexperia PMEG4050EP (Schottky 5A 40V, SOD-128)")
add("L1", "Device:L", "4.7uH", "Inductor_SMD:L_Bourns_SRP1038C_10.0x10.0mm", {"1": "SW6", "2": "+6V"},
    MPN="Bourns SRP1038C-4R7M (4.7uH, Isat >= 8A)")
add("R5", "Device:R", "182R 1%", R0805, {"1": "+6V", "2": "FB6"})
add("R6", "Device:R", "1k 1%", R0805, {"1": "FB6", "2": "GND"}, LCSC="C17513")
add("C7", "Device:C", "22uF 25V", C1210, {"1": "+6V", "2": "GND"})
add("C8", "Device:C", "22uF 25V", C1210, {"1": "+6V", "2": "GND"})
add("C9", "Device:C_Polarized", "220uF 16V", "Capacitor_SMD:CP_Elec_6.3x7.7", {"1": "+6V", "2": "GND"},
    MPN="Electrolytique alu CMS 220uF 16V 6.3x7.7")
add("R7", "Device:R", "1k", R0805, {"1": "+6V", "2": "LED6"}, LCSC="C17513")
add("LED1", "Device:LED", "LED verte 6V", "LED_SMD:LED_0805_2012Metric", {"1": "GND", "2": "LED6"})

# ---------------- Regulateur 5V 2A logique (TPS54202) ----------------
add("U3", "Regulator_Switching:TPS54202DDC", "TPS54202H", "Package_TO_SOT_SMD:SOT-23-6",
    {"1": "GND", "2": "SW5", "3": "V12", "4": "FB5", "5": "EN5", "6": "BOOT5"},
    MPN="TPS54202HDDCR (TPS54202DDCR accepte)", LCSC="C527684")
add("R8", "Device:R", "100k", R0805, {"1": "V12", "2": "EN5"}, LCSC="C17407")
add("R9", "Device:R", "33k", R0805, {"1": "EN5", "2": "GND"})
add("C10", "Device:C", "10uF 50V", C1210, {"1": "V12", "2": "GND"})
add("C11", "Device:C", "100nF 50V", C0805, {"1": "V12", "2": "GND"}, LCSC="C49678")
add("C12", "Device:C", "100nF 50V", C0805, {"1": "BOOT5", "2": "SW5"}, LCSC="C49678")
add("L2", "Device:L", "15uH", "Inductor_SMD:L_Bourns_SRN6045TA", {"1": "SW5", "2": "5V_BUCK"},
    MPN="Bourns SRN6045TA-150M")
add("R10", "Device:R", "100k 1%", R0805, {"1": "5V_BUCK", "2": "FB5"}, LCSC="C17407")
add("R11", "Device:R", "12.7k 1%", R0805, {"1": "FB5", "2": "GND"})
add("C13", "Device:C", "75pF", C0805, {"1": "5V_BUCK", "2": "FB5"})
add("C14", "Device:C", "22uF 16V", C1206, {"1": "5V_BUCK", "2": "GND"})
add("C15", "Device:C", "22uF 16V", C1206, {"1": "5V_BUCK", "2": "GND"})
add("D4", "Device:D_Schottky", "SS34", "Diode_SMD:D_SMA", {"1": "+5V", "2": "5V_BUCK"},
    MPN="SS34 (anti-retour USB)", LCSC="C8678")
add("C16", "Device:C", "10uF 16V", C1206, {"1": "+5V", "2": "GND"})
add("C17", "Device:C", "100nF 50V", C0805, {"1": "+5V", "2": "GND"}, LCSC="C49678")
add("R12", "Device:R", "1k", R0805, {"1": "5V_BUCK", "2": "LED5"}, LCSC="C17513")
add("LED2", "Device:LED", "LED verte 5V", "LED_SMD:LED_0805_2012Metric", {"1": "GND", "2": "LED5"})

# ---------------- Mesure batterie (A0 = VBAT/4) ----------------
add("R13", "Device:R", "30k 1%", R0805, {"1": "V12", "2": "VBAT_SENSE"})
add("R14", "Device:R", "10k 1%", R0805, {"1": "VBAT_SENSE", "2": "GND"}, LCSC="C17414")
add("C18", "Device:C", "100nF 50V", C0805, {"1": "VBAT_SENSE", "2": "GND"}, LCSC="C49678")

# ---------------- SBUS (inverseur) ----------------
add("J6", "Connector_Generic:Conn_01x03", "SBUS", HDR3, {"1": "SBUS_IN", "2": "+5V", "3": "GND"}, Montage="THT")
add("R1", "Device:R", "1k", R0805, {"1": "SBUS_IN", "2": "SBUS_B"}, LCSC="C17513")
add("Q1", "Transistor_BJT:MMBT3904", "MMBT3904", "Package_TO_SOT_SMD:SOT-23",
    {"1": "SBUS_B", "2": "GND", "3": "D19"}, LCSC="C20526")
add("R2", "Device:R", "10k", R0805, {"1": "+5V", "2": "D19"}, LCSC="C17414")

# ---------------- Moteurs : puissance ----------------
add("J2", "JDG2025:691214110002", "MOT1 PWR", TERM, {"1": "GND", "2": "VBAT"}, Montage="THT")
add("J10", "JDG2025:691214110002", "MOT2 PWR", TERM, {"1": "GND", "2": "VBAT"}, Montage="THT")
add("J4", "JDG2025:691214110002", "MOT3 PWR", TERM, {"1": "GND", "2": "VBAT"}, Montage="THT")
add("J8", "JDG2025:691214110002", "MOT4 PWR", TERM, {"1": "VBAT", "2": "GND"}, Montage="THT")

# ---------------- Moteurs : commandes (resistances serie 100R, pull-down DNP) ----------------
add("J3", "JDG2025:691214110002", "MOT1 PWM/DIR", TERM, {"1": "M1_PWM", "2": "M1_DIR"}, Montage="THT")
add("J11", "JDG2025:691214110002", "MOT2 DIR/PWM", TERM, {"1": "M2_DIR", "2": "M2_PWM"}, Montage="THT")
add("J5", "JDG2025:691214110002", "MOT3 PWM/DIR", TERM, {"1": "M3_PWM", "2": "M3_DIR"}, Montage="THT")
add("J9", "JDG2025:691214110002", "MOT4 DIR/PWM", TERM, {"1": "M4_DIR", "2": "M4_PWM"}, Montage="THT")
for ref, a, b in [("R20", "D5", "M1_PWM"), ("R21", "D7", "M1_DIR"),
                  ("R22", "D3", "M2_PWM"), ("R23", "D49", "M2_DIR"),
                  ("R24", "D6", "M3_PWM"), ("R25", "D9", "M3_DIR"),
                  ("R26", "D2", "M4_PWM"), ("R27", "D8", "M4_DIR")]:
    add(ref, "Device:R", "100R", R0805, {"1": a, "2": b}, LCSC="C17408")
for ref, n in [("R30", "M1_PWM"), ("R31", "M2_PWM"), ("R32", "M3_PWM"), ("R33", "M4_PWM")]:
    add(ref, "Device:R", "4.7k", R0805, {"1": n, "2": "GND"}, LCSC="C17673", dnp=True)

# ---------------- Servos ----------------
for ref, rref, d, n in [("S1", "R40", "D10", "SERVO1"), ("S2", "R41", "D12", "SERVO2"),
                        ("S3", "R42", "D13", "SERVO3"), ("S4", "R43", "D11", "SERVO4")]:
    add(ref, "Connector_Generic:Conn_01x03", n, HDR3, {"1": "GND", "2": "+6V", "3": n + "_SIG"}, Montage="THT")
    add(rref, "Device:R", "100R", R0805, {"1": d, "2": n + "_SIG"}, LCSC="C17408")

# ---------------- Module Mega 2560 PRO Embed ----------------
USED = {"D2", "D3", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D19", "D49"}
u1 = {}
for i in range(0, 16):
    u1["A%d" % i] = None
u1["A0"] = "VBAT_SENSE"
for i in range(2, 54):
    u1["D%d" % i] = ("D%d" % i) if ("D%d" % i) in USED else None
u1.update({"RX": None, "TX": None, "AREF": None, "RST": None, "RESET": None, "MISO": None, "MOSI": None,
           "SCK": None, "3V3_1": None, "3V3_2": None, "VIN_1": None, "VIN_2": None,
           "5V_1": "+5V", "5V_2": "+5V", "5V_3": "+5V", "GND_1": "GND", "GND_2": "GND", "GND_3": "GND"})
add("U1", "JDG2025:MEGA_PRO_EMBED_CH340G_ATMEGA2560", "Mega 2560 PRO Embed",
    "JDG2025:MODULE_MEGA_PRO_EMBED_CH340G_ATMEGA2560", u1,
    MPN="RobotDyn Mega 2560 PRO Embed CH340G + embases femelles 2x21, 2x16, 2x3", Montage="THT")

BYREF = {c["ref"]: c for c in C}


def nets():
    n = {}
    for c in C:
        for p, net in c["pins"].items():
            if net:
                n.setdefault(net, []).append((c["ref"], p))
    return n
