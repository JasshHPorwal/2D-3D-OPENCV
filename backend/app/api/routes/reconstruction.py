from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pytesseract, open3d
from app.core.config import get_settings
from app.services.pipeline_service import run_pipeline_async, get_job

router=APIRouter()

@router.post('/reconstruct')
async def reconstruct(drawing: UploadFile = File(...)):
    if drawing.content_type not in {'image/png','image/jpeg'}: raise HTTPException(400,'Unsupported file type')
    b=await drawing.read(); s=get_settings()
    if len(b) > s.MAX_UPLOAD_MB*1024*1024: raise HTTPException(400,'File too large')
    return await run_pipeline_async(b)

@router.get('/jobs/{job_id}')
def job(job_id:str):
    j=get_job(job_id)
    if not j: raise HTTPException(404,'Not found')
    return j

@router.get('/jobs/{job_id}/model.glb')
def model(job_id:str):
    j=get_job(job_id)
    if not j or not j.glb_path: raise HTTPException(404,'Not found')
    return FileResponse(j.glb_path, media_type='model/gltf-binary', filename='model.glb')

@router.get('/health')
def health():
    return {'status':'ok','tesseract':str(pytesseract.get_tesseract_version()),'open3d':open3d.__version__,'pipeline_stages':5}
