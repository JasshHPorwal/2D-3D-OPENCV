import os
from app.models.schema import MeshStats

def export_glb(mesh, job_id: str, upload_dir: str):
    d=os.path.join(upload_dir,job_id)
    os.makedirs(d,exist_ok=True)
    p=os.path.join(d,'model.glb')
    mesh.export(p,file_type='glb')
    e=mesh.bounding_box.extents
    stats=MeshStats(vertex_count=len(mesh.vertices), face_count=len(mesh.faces), bbox_x_mm=float(e[0]), bbox_y_mm=float(e[1]), bbox_z_mm=float(e[2]), is_watertight=bool(mesh.is_watertight), volume_mm3=float(mesh.volume) if mesh.is_watertight else None)
    return p,stats
