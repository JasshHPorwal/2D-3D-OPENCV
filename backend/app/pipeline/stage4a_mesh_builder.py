import trimesh, numpy as np
from app.models.schema import *

def build_mesh(spec: GeometrySpec):
    result=None
    for f in spec.features:
        mesh=None
        if f.type==FeatureType.BOX:
            mesh=trimesh.creation.box(extents=[f.dimensions_mm['x'],f.dimensions_mm['y'],f.dimensions_mm['z']])
        elif f.type==FeatureType.CYLINDER:
            mesh=trimesh.creation.cylinder(radius=f.dimensions_mm['radius'], height=f.dimensions_mm['height'], sections=64)
        if mesh is None: continue
        mesh.apply_translation(np.array(f.position_mm))
        if f.operation==CSGOperation.ADD:
            result=mesh if result is None else trimesh.boolean.union([result,mesh])
        else:
            if result is not None:
                try: result=trimesh.boolean.difference([result,mesh])
                except Exception: pass
    if result is None:
        result=trimesh.creation.box(extents=[spec.overall_width_mm,spec.overall_height_mm,spec.overall_depth_mm])
    trimesh.repair.fix_winding(result)
    return result
