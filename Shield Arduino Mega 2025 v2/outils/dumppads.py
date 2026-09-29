import pcbnew, sys
b=pcbnew.LoadBoard(sys.argv[1])
refs=sys.argv[2].split(',') if len(sys.argv)>2 else None
for fp in sorted(b.GetFootprints(), key=lambda f:f.GetReference()):
    if refs and fp.GetReference() not in refs: continue
    bb=fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if hasattr(fp,'GetCourtyard') else None
    print(fp.GetReference(), 'crtyd', (round(pcbnew.ToMM(bb.GetLeft()),2),round(pcbnew.ToMM(bb.GetRight()),2),round(pcbnew.ToMM(bb.GetTop()),2),round(pcbnew.ToMM(bb.GetBottom()),2)) if bb else '')
    for p in fp.Pads():
        pos=p.GetPosition(); sz=p.GetSize()
        # taille orientee
        ang=p.GetOrientationDegrees()
        w,h=pcbnew.ToMM(sz.x),pcbnew.ToMM(sz.y)
        if round(ang)%180==90: w,h=h,w
        print('   %s %-10s (%.3f, %.3f) %.2fx%.2f'%(p.GetNumber(), p.GetNetname(), pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y), w, h))
