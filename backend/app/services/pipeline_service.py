import asyncio, os, time
from uuid import uuid4
from app.core.config import get_settings
from app.models.schema import *
from app.pipeline import stage1_input_preprocessor as s1, stage2a_feature_extractor as s2a, stage2b_correspondence_engine as s2b, stage3a_dimension_reader as s3a, stage3b_geometry_builder as s3b, stage4a_mesh_builder as s4a, stage4b_renderer_exporter as s4b, stage5_validator as s5

_jobs: dict[str, ReconstructionResult] = {}

def get_job(job_id:str): return _jobs.get(job_id)

async def run_pipeline_async(image_bytes: bytes) -> ReconstructionResult:
    st=[]; settings=get_settings(); job_id=uuid4().hex[:12]; os.makedirs(os.path.join(settings.UPLOAD_DIR, job_id), exist_ok=True)
    loop=asyncio.get_running_loop()
    try:
        t=time.perf_counter(); crops=await loop.run_in_executor(None, s1.process, image_bytes, job_id, settings.UPLOAD_DIR); st.append(StageResult(stage='Stage 1',success=True,duration_ms=(time.perf_counter()-t)*1000))
        t=time.perf_counter(); lines,circles=await loop.run_in_executor(None, s2a.extract, crops); st.append(StageResult(stage='Stage 2',success=True,duration_ms=(time.perf_counter()-t)*1000))
        t=time.perf_counter(); dims,ppm=await loop.run_in_executor(None, s3a.read_dimensions, crops); _=await loop.run_in_executor(None, s2b.match, lines,circles,ppm); st.append(StageResult(stage='Stage 3',success=True,duration_ms=(time.perf_counter()-t)*1000))
        parsed={k:ParsedView(view_name=k, region=ViewRegion(name=k,bbox=(0,0,v.shape[1],v.shape[0])), lines=lines.get(k,[]), circles=circles.get(k,[]), dimensions=dims.get(k,[]), px_per_mm=ppm.get(k,5.9)) for k,v in crops.items()}
        t=time.perf_counter(); spec=await loop.run_in_executor(None, s3b.build, parsed); mesh=await loop.run_in_executor(None, s4a.build_mesh, spec); st.append(StageResult(stage='Stage 4',success=True,duration_ms=(time.perf_counter()-t)*1000))
        t=time.perf_counter(); glb,stats=await loop.run_in_executor(None, s4b.export_glb, mesh, job_id, settings.UPLOAD_DIR); report=await loop.run_in_executor(None, s5.validate, mesh, spec, st); st.append(StageResult(stage='Stage 5',success=report.passed,duration_ms=(time.perf_counter()-t)*1000,error=';'.join(report.errors) if report.errors else None))
        status='COMPLETED' if report.passed and not report.warnings else ('COMPLETED_WITH_WARNINGS' if report.passed else 'FAILED_VALIDATION')
        res=ReconstructionResult(job_id=job_id,status=status,glb_path=glb,stages=st,mesh_stats=stats,geometry_spec=spec)
    except Exception as e:
        st.append(StageResult(stage='FAILED',success=False,duration_ms=0,error=str(e)))
        res=ReconstructionResult(job_id=job_id,status='FAILED',stages=st)
    _jobs[job_id]=res
    return res
