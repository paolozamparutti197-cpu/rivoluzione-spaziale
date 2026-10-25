"""Vedute esterne dal modello Merlin 1D, Blender 2.93 LTS.

blender.exe -b MODELLO.blend --python renderizza_vedute.py -- CARTELLA_PNG
Non modifica il file .blend sorgente. Non genera sezioni interne.
"""
import bpy
import sys
import os
import json
from mathutils import Vector

assert bpy.app.version[:2] == (2,93), 'Usare Blender 2.93 LTS.'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=os.path.abspath(args[0] if args else os.path.join(os.path.dirname(__file__),'vedute_png'))
os.makedirs(out,exist_ok=True)
s=bpy.context.scene
for c in bpy.data.collections:
    if c.name.startswith('06'):
        c.hide_render=True
s.render.engine='CYCLES'
s.cycles.device='CPU'
s.cycles.samples=32
s.cycles.use_denoising=True
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.035
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA'
s.render.film_transparent=False
cam=s.camera
cam.data.type='ORTHO'
# Fill laterale per rendere leggibili i corpi pompa anche nella vista X.
ld=bpy.data.lights.new('Softbox vedute laterali','AREA')
ld.energy=180;ld.color=(.85,.92,1);ld.shape='DISK';ld.size=3
lo=bpy.data.objects.new('Softbox vedute laterali',ld)
s.collection.objects.link(lo);lo.location=(4,-1.5,3.4)
lo.rotation_euler=(Vector((0,0,1.5))-lo.location).to_track_quat('-Z','Y').to_euler()

views=[
    dict(id='insieme',label='Veduta a tre quarti',camera=[4.1,-6.6,3.4],target=[.04,0,1.34],scale=3.10,size=[1280,1600]),
    dict(id='frontale',label='Veduta frontale',camera=[0,-7,1.35],target=[.05,0,1.35],scale=2.90,size=[1280,1600]),
    dict(id='laterale',label='Veduta laterale',camera=[7,0,1.35],target=[.05,0,1.35],scale=2.90,size=[1280,1600]),
    dict(id='gruppo-superiore',label='Dettaglio del gruppo superiore',camera=[3.5,-5.5,3.3],target=[.10,0,2.00],scale=1.55,size=[1600,1200]),
]
manifest={'blender':bpy.app.version_string,'model_kind':'Ricostruzione visiva esterna, non CAD SpaceX','views':[]}
for v in views:
    cam.location=v['camera']
    cam.rotation_euler=(Vector(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=v['scale']
    s.render.resolution_x,s.render.resolution_y=v['size']
    s.render.filepath=os.path.join(out,'merlin-'+v['id']+'.png')
    print('INIZIO_VEDUTA',v['id'],flush=True)
    bpy.ops.render.render(write_still=True)
    manifest['views'].append(v)
    with open(os.path.join(out,'vedute.json'),'w',encoding='utf-8') as f:
        json.dump(manifest,f,ensure_ascii=False,indent=2)
    print('VEDUTA_COMPLETATA',v['id'],flush=True)
print('TUTTE_LE_VEDUTE_COMPLETATE',flush=True)
