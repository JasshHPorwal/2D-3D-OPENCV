import os, time, uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.api.routes.reconstruction import router
import pytesseract

@asynccontextmanager
async def lifespan(app: FastAPI):
    s=get_settings(); os.makedirs(s.UPLOAD_DIR, exist_ok=True); pytesseract.pytesseract.tesseract_cmd=s.TESSERACT_CMD
    yield

app=FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=get_settings().CORS_ORIGINS, allow_methods=['*'], allow_headers=['*'])

@app.middleware('http')
async def request_id(request: Request, call_next):
    rid=str(uuid.uuid4()); request.state.request_id=rid; st=time.perf_counter(); resp=await call_next(request); resp.headers['X-Request-ID']=rid; resp.headers['X-Process-Time']=f'{(time.perf_counter()-st)*1000:.2f}'; return resp

@app.exception_handler(Exception)
async def e500(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={'error':str(exc),'request_id':getattr(request.state,'request_id','unknown')})

app.include_router(router,prefix='/api')
