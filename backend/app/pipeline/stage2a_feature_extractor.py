import cv2, numpy as np
from app.models.schema import DetectedLine, DetectedCircle, LineType

def extract(view_crops: dict[str, np.ndarray]):
    lines_out, circles_out = {}, {}
    for vn, img in view_crops.items():
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        med = float(np.median(g))
        e = cv2.Canny(g, int(max(0, med * 0.66)), int(min(255, med * 1.33)))
        h, w = g.shape
        seg = cv2.HoughLinesP(e, 1, np.pi/180, 25, minLineLength=int((h*h+w*w)**0.5*0.03), maxLineGap=8)
        lines=[]
        if seg is not None:
            for s in seg[:,0]:
                lines.append(DetectedLine(x1=float(s[0]),y1=float(s[1]),x2=float(s[2]),y2=float(s[3]),line_type=LineType.SOLID))
        circles=[]
        cc = cv2.HoughCircles(cv2.GaussianBlur(g,(5,5),1.5), cv2.HOUGH_GRADIENT, 1.2, min(h,w)*0.08, param1=50, param2=20, minRadius=max(3,int(min(h,w)*0.01)), maxRadius=int(min(h,w)*0.45))
        if cc is not None:
            for c in np.round(cc[0]).astype(int):
                circles.append(DetectedCircle(cx=float(c[0]), cy=float(c[1]), radius_px=float(c[2]), line_type=LineType.SOLID, view=vn))
        lines_out[vn]=lines
        circles_out[vn]=circles
    return lines_out, circles_out
