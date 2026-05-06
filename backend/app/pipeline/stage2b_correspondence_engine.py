from app.models.schema import CorrespondenceGroup

def match(lines, circles, px_per_mm):
    groups=[]
    f = circles.get('front',[])
    s = circles.get('side',[])
    tol=2.0
    for i,fc in enumerate(f):
        fy=fc.cy/max(px_per_mm.get('front',1),1e-6)
        for j,sc in enumerate(s):
            sy=sc.cy/max(px_per_mm.get('side',1),1e-6)
            d=abs(fy-sy)
            if d<=tol:
                groups.append(CorrespondenceGroup(feature_ids_by_view={'front':[i],'side':[j]}, inferred_3d_position_mm=(fc.cx,fy,sc.cx), confidence=1-(d/tol)))
                break
    return groups
