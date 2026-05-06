from app.models.schema import *

def validate(mesh, spec: GeometrySpec, stages: list[StageResult]) -> ValidationReport:
    errors=[]; warnings=[]
    if len(mesh.vertices)==0 or len(mesh.faces)==0: errors.append('Empty mesh')
    if not any(f.operation==CSGOperation.ADD for f in spec.features): errors.append('No ADD feature')
    if not mesh.is_watertight: warnings.append('Mesh is not watertight')
    return ValidationReport(passed=not errors, warnings=warnings, errors=errors, stage_summary=stages)
