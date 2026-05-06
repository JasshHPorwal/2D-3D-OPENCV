import cv2, numpy as np
from app.pipeline.stage1_input_preprocessor import process

def test_detect_views(tmp_path):
    img=np.full((1000,1400,3),255,np.uint8)
    cv2.rectangle(img,(100,100),(500,300),(0,0,0),-1)
    cv2.rectangle(img,(100,600),(500,900),(0,0,0),-1)
    cv2.rectangle(img,(800,600),(1200,900),(0,0,0),-1)
    ok,b=cv2.imencode('.png',img)
    crops=process(b.tobytes(),'t1',str(tmp_path))
    assert len(crops)>=2
