from app.models.schema import *

def build(parsed_views: dict[str, ParsedView]) -> GeometrySpec:
    front=parsed_views.get('front')
    side=parsed_views.get('side')
    top=parsed_views.get('top')
    w=front.region.bbox[2]/front.px_per_mm if front else (top.region.bbox[2]/top.px_per_mm if top else 50)
    h=front.region.bbox[3]/front.px_per_mm if front else (side.region.bbox[3]/side.px_per_mm if side else 50)
    d=side.region.bbox[2]/side.px_per_mm if side else (top.region.bbox[3]/top.px_per_mm if top else 50)
    feats=[GeometricFeature(type=FeatureType.BOX, operation=CSGOperation.ADD, position_mm=(0,0,0), dimensions_mm={'x':w,'y':h,'z':d}, label='Base solid')]
    src=front or top or side
    if src:
        for c in src.circles:
            r=c.radius_px/src.px_per_mm
            feats.append(GeometricFeature(type=FeatureType.CYLINDER, operation=CSGOperation.SUBTRACT, axis='Y', position_mm=(0,0,0), dimensions_mm={'radius':r,'height':d}, label=f'Hole Ø{r*2:.0f}mm'))
    return GeometrySpec(overall_width_mm=w, overall_height_mm=h, overall_depth_mm=d, features=[f for f in feats if f.operation==CSGOperation.ADD]+[f for f in feats if f.operation==CSGOperation.SUBTRACT])
