import cv2, numpy as np
from app.pipeline.stage2a_feature_extractor import extract

def test_circles():
    img=np.full((300,300,3),255,np.uint8)
    cv2.circle(img,(50,50),15,(0,0,0),2);cv2.circle(img,(150,150),30,(0,0,0),2);cv2.circle(img,(250,80),8,(0,0,0),2)
    _, circles = extract({'front':img})
    assert len(circles['front'])>=2
