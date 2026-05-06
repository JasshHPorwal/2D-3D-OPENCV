import re, cv2, numpy as np, pytesseract
from app.models.schema import DimensionAnnotation

def read_dimensions(view_crops: dict[str,np.ndarray]):
    dims, scales = {}, {}
    for vn,img in view_crops.items():
        g=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text=pytesseract.image_to_string(g, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789.Ø⌀φO')
        cleaned=text.strip()
        vals=re.sub(r'[^0-9.]','',cleaned)
        out=[]
        if vals:
            v=float(vals)
            out.append(DimensionAnnotation(value_mm=v, is_diameter=cleaned[:1] in ['Ø','⌀','φ','O'], position_px=(g.shape[1]/2,g.shape[0]/2), view=vn))
            scales[vn]=max(g.shape)/max(v,1)
        else:
            scales[vn]=5.9
        dims[vn]=out
    return dims, scales
