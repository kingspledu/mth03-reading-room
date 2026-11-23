"""Detect continuous light gutters and crop inside the actual panel boundaries."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

def axis_bands(array, axis, count=4):
    neutral=(array.min(axis=2)>205)&((array.max(axis=2).astype(float)-array.min(axis=2))<35)
    scores=neutral.mean(axis=axis)
    length=len(scores)
    # Generated rows can have unequal heights. Prefer actual uninterrupted
    # white gutters across the full axis over assumptions about quarter marks.
    runs=[]
    begin=None
    for i,value in enumerate(scores):
        if value >= .98 and begin is None: begin=i
        if value < .98 and begin is not None:
            if begin>2 and i<length-2 and i-begin>=2: runs.append((begin,i))
            begin=None
    if len(runs)==count-1:
        return runs
    bands=[]
    for index in range(1,count):
        lo=int(length*(index/count-.065))
        hi=int(length*(index/count+.065))
        position=lo+int(np.argmax(scores[lo:hi]))
        confidence=float(scores[position])
        if confidence<.65:
            raise ValueError(f'Uncertain gutter at {index}: {confidence:.3f}; manual boundary review required')
        left=right=position
        threshold=max(.6,confidence*.82)
        while left>lo and scores[left-1]>=threshold: left-=1
        while right+1<hi and scores[right+1]>=threshold: right+=1
        bands.append((left,right+1))
    return bands

def crop_grid(source, targets, audit_path):
    with Image.open(source) as original:
        image=original.convert('RGB')
    array=np.asarray(image)
    vertical=[]
    horizontal=axis_bands(array,1)
    ys=[(2,horizontal[0][0]-2)]+[(horizontal[i-1][1]+2,horizontal[i][0]-2) for i in range(1,3)]+[(horizontal[2][1]+2,image.height-2)]
    row_vertical=[axis_bands(array[y0:y1],0) for y0,y1 in ys]
    overlay=image.copy()
    draw=ImageDraw.Draw(overlay)
    records=[]
    for index,target in enumerate(targets):
        y0,y1=ys[index//4]
        bands=row_vertical[index//4]
        col=index%4
        x0=2 if col==0 else bands[col-1][1]+2
        x1=image.width-2 if col==3 else bands[col][0]-2
        # Remove only continuous near-white edge strips, including the sheet's
        # outer frame. Never trim based on isolated light objects in the art.
        def blank(strip):
            return float(((strip.min(axis=2)>245)&((strip.max(axis=2)-strip.min(axis=2))<10)).mean()) >= .98
        while x0+1<x1 and blank(array[y0:y1,x0:x0+1]): x0+=1
        while x1-1>x0 and blank(array[y0:y1,x1-1:x1]): x1-=1
        while y0+1<y1 and blank(array[y0:y0+1,x0:x1]): y0+=1
        while y1-1>y0 and blank(array[y1-1:y1,x0:x1]): y1-=1
        assert x1>x0 and y1>y0
        box=(x0,y0,x1,y1)
        Path(target).parent.mkdir(parents=True,exist_ok=True)
        image.crop(box).save(target,quality=94)
        draw.rectangle(box,outline='red',width=2)
        records.append({'target':str(target),'box':box,'size':[x1-x0,y1-y0]})
    audit_path=Path(audit_path)
    audit_path.parent.mkdir(parents=True,exist_ok=True)
    audit_path.write_text(json.dumps({'source':str(source),'vertical_gutters':vertical,'vertical_gutters_by_row':row_vertical,'horizontal_gutters':horizontal,'tiles':records},indent=2),encoding='utf-8')
    overlay.save(audit_path.with_suffix('.png'))
    return records
