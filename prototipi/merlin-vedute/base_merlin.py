"""Merlin 1D: ricostruzione visiva esterna, Blender 2.93 LTS.

Non e' un modello CAD SpaceX. Profilo, raccordi e dettagli non quotati
sono approssimazioni artistiche. Riferimenti nel blocco FONTI del .blend.
Esecuzione: blender.exe -b --factory-startup --python crea_merlin.py
"""
import bpy
import math
import os
import json
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.environ.get('MERLIN_PREVIEW', '0') == '1'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.collections):
    if block.name != 'Collection' and block.users == 0:
        bpy.data.collections.remove(block)
base = bpy.data.collections.get('Collection')
base.name = '01 · Ugello e camera'
COL = base
def collection(name):
    global COL
    COL = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(COL)
    return COL
def move(obj, name, mat=None):
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COL.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj
def metal(name, color, rough=.3, metallic=1., texture=True):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    n=m.node_tree.nodes; l=m.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=rough
    if texture:
        noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=190
        noise.inputs['Detail'].default_value=2
        bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12
        bump.inputs['Distance'].default_value=.0012
        l.new(noise.outputs['Fac'],bump.inputs['Height'])
        l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m
steel=metal('Acciaio · satinato',(.39,.45,.49),.27)
bright=metal('Alluminio · raccordi',(.63,.69,.72),.22)
dark=metal('Lega di nichel · camicia ugello',(.085,.103,.12),.38)
nozzle=metal('Ugello · nichel satinato',(.24,.28,.32),.32)
inside=metal('Interno ugello · metallo brunito',(.045,.038,.033),.53)
black=metal('Grafite · protezioni',(.018,.025,.031),.53,.4)
gold=metal('Schermatura termica · bronzo',(.27,.18,.085),.44)
copper=metal('Metallo termicamente alterato',(.19,.105,.058),.43)
blue=metal('Raccordi · blu scuro',(.035,.095,.15),.28)
rubber=metal('Cablaggi · nero',(.012,.017,.021),.55,0,False)

def cylinder(name, radius, depth, loc, mat=steel, axis=(0,0,1), verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc)
    o=move(bpy.context.object,name,mat)
    o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    bevel=o.modifiers.new('Spigoli lavorati','BEVEL'); bevel.width=min(.008,depth*.12,radius*.08);bevel.segments=2
    return o
def tube(name, points, radius, mat=steel, smooth=True):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'
    cu.resolution_u=18; cu.bevel_depth=radius;cu.bevel_resolution=4
    if smooth:
        sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
        for p,co in zip(sp.bezier_points,points):
            p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    else:
        sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
        for p,co in zip(sp.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,cu);COL.objects.link(o);cu.materials.append(mat)
    return o
def torus(name, major, minor, loc, mat=steel, axis=(0,0,1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=96,minor_segments=12,location=loc)
    o=move(bpy.context.object,name,mat);o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    return o
def sphere(name,loc,scale,mat=steel):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,location=loc)
    o=move(bpy.context.object,name,mat);o.scale=scale;return o
def box(name, loc, scale,mat=steel):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=move(bpy.context.object,name,mat);o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    b=o.modifiers.new('Raggi di bordo','BEVEL');b.width=.012;b.segments=3
    return o
def strut(name,a,b,r,mat=steel):
    d=Vector(b)-Vector(a)
    return cylinder(name,r,d.length,(Vector(a)+Vector(b))/2,mat,d)
def ringbolts(name,center,r,count=16,axis='Z',size=.012,mat=bright):
    for i in range(count):
        t=2*math.pi*i/count
        if axis=='Z':loc=(center[0]+r*math.cos(t),center[1]+r*math.sin(t),center[2]);v=(0,0,1)
        elif axis=='Y':loc=(center[0]+r*math.cos(t),center[1],center[2]+r*math.sin(t));v=(0,1,0)
        else:loc=(center[0],center[1]+r*math.cos(t),center[2]+r*math.sin(t));v=(1,0,0)
        cylinder(name+' · %02d'%i,size,size*.75,loc,mat,v,6)
def flange(name,loc,r,axis=(0,0,1),bolts=12):
    cylinder(name,r,.027,loc,steel,axis)
    ax='Z' if axis==(0,0,1) else 'Y' if axis==(0,1,0) else 'X'
    c=Vector(loc)+Vector(axis)*.017
    ringbolts(name+' bullone',c,r*.83,bolts,ax,.008)

# Profilo artistico continuo; la fonte pubblica non fornisce quote costruttive.
# (z,r) dalla bocca al collettore superiore.
profile=[(.17,.46),(.24,.448),(.35,.426),(.47,.398),(.60,.36),(.73,.317),(.86,.268),(.98,.216),(1.08,.173),(1.16,.141),(1.22,.124),(1.27,.121),(1.32,.13),(1.38,.164),(1.45,.195),(1.53,.207),(1.68,.207),(1.78,.207)]
def interp_profile(samples=240):
    # Interpolazione Hermite monotona, senza dipendenze esterne.
    out=[]
    for i in range(len(profile)-1):
        z0,r0=profile[i];z1,r1=profile[i+1]
        m0=(r1-profile[max(0,i-1)][1])/(z1-profile[max(0,i-1)][0])
        m1=(profile[min(len(profile)-1,i+2)][1]-r0)/(profile[min(len(profile)-1,i+2)][0]-z0)
        steps=max(3,round(samples*(z1-z0)/(profile[-1][0]-profile[0][0])))
        for k in range(steps):
            t=k/steps;h=z1-z0
            r=(2*t**3-3*t*t+1)*r0+(t**3-2*t*t+t)*h*m0+(-2*t**3+3*t*t)*r1+(t**3-t*t)*h*m1
            out.append((z0+t*h,r))
    out.append(profile[-1]);return out
prof=interp_profile()
verts=[];faces=[];segments=192
for z,r in prof:
    for j in range(segments):
        a=2*math.pi*j/segments
        verts.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(prof)-1):
    for j in range(segments):
        a=k*segments+j;b=k*segments+(j+1)%segments
        faces.append((a,b,b+segments,a+segments))
mesh=bpy.data.meshes.new('Superficie di rivoluzione');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('Ugello rigenerativo e camera · profilo continuo',mesh);COL.objects.link(o)
o.data.materials.append(nozzle);o.data.materials.append(inside)
solid=o.modifiers.new('Parete cava e bordo aperto','SOLIDIFY');solid.thickness=.009;solid.material_offset=1;solid.material_offset_rim=0
for p in mesh.polygons:p.use_smooth=True
for i in range(144):
    a=2*math.pi*i/144
    points=[((r+.0015)*math.cos(a),(r+.0015)*math.sin(a),z) for z,r in prof[::4]]
    tube('Nervatura esterna %03d'%i,points,.00145,nozzle,False)
torus('Labbro uscita',.460,.007,(0,0,.171),steel)
torus('Saldatura inferiore',.450,.0028,(0,0,.235),copper)
torus('Collettore rigenerativo',.375,.018,(0,0,.55),steel)
torus('Collare gola',.139,.012,(0,0,1.155),steel)
torus('Fascia camera superiore',.210,.015,(0,0,1.69),bright)
flange('Flangia testa camera',(0,0,1.79),.241,bolts=24)
cylinder('Testa iniettore · involucro esterno',.213,.12,(0,0,1.855),steel)
torus('Tenuta testa',.214,.008,(0,0,1.91),dark)
ringbolts('Prigionieri testa',(0,0,1.929),.190,20,size=.009)
cylinder('Domo superiore',.172,.09,(0,0,1.96),dark)
sphere('Domo testa iniettore',(0,0,2.005),(.172,.172,.067),steel)

collection('02 · Turbopompa e generatore di gas')
# Corpi coassiali: pompa LOX, pompa combustibile e turbina, albero comune Y.
px=.36;pz=2.07
strut('Albero comune · asse visivo',(px,-.25,pz),(px,.39,pz),.046,dark)
for name,y,r,d,mat in [('Pompa LOX',-.17,.181,.18,steel),('Pompa RP-1',.055,.145,.16,bright),('Turbina',.26,.167,.12,gold)]:
    cylinder(name+' · corpo',r,d,(px,y,pz),mat,(0,1,0))
    sphere(name+' · calotta',(px,y-d*.45,pz),(r*.94,d*.30,r*.94),mat)
    torus(name+' · giunzione',r,.012,(px,y-d*.50,pz),steel,(0,1,0))
    ringbolts(name+' · prigioniero',(px,y-d*.52-.012,pz),r*.85,16,'Y',.008)
    for j in range(6):
        t=2*math.pi*j/6
        tube(name+' · rinforzo %d'%j,[(px+(r-.01)*math.cos(t),y-d*.4,pz+(r-.01)*math.sin(t)),(px+(r+.007)*math.cos(t),y,pz+(r+.007)*math.sin(t)),(px+(r-.01)*math.cos(t),y+d*.4,pz+(r-.01)*math.sin(t))],.009,mat)
flange('Ingresso assiale LOX',(px,-.318,pz),.092,(0,1,0),12)
tube('Bocca aspirazione LOX',[(px,-.32,pz),(px,-.42,pz+.02),(px,-.45,pz+.22),(px,-.43,pz+.39)],.068,steel)
flange('Interfaccia LOX',(px,-.43,pz+.39),.096,bolts=12)
tube('Mandata LOX verso testa',[(.50,-.14,2.10),(.60,-.15,2.22),(.48,-.21,2.34),(.19,-.23,2.32),(.08,-.17,2.12),(.02,-.08,1.98)],.042,bright)
flange('Giunto mandata',(.235,-.23,2.322),.068,(1,0,0),10)
tube('Ingresso combustibile',[(.34,.03,2.16),(.45,.10,2.34),(.33,.18,2.47),(.17,.20,2.47)],.039,steel)
flange('Interfaccia RP-1',(.17,.20,2.47),.067,(1,0,0),10)
cylinder('Generatore di gas · involucro',.074,.25,(-.22,.14,2.03),gold,axis=(0,0,1))
sphere('Generatore di gas · calotta',(-.22,.14,2.165),(.074,.074,.04),gold)
flange('Generatore di gas · chiusura',(-.22,.14,1.90),.089,bolts=10)
tube('Gas motore verso turbina',[(-.22,.14,1.99),(-.19,.30,1.98),(.03,.40,2.07),(.31,.38,2.07)],.033,gold)

collection('03 · Condotti, valvole e cablaggi')
# Scarico aperto turbina, distinto dal flusso principale.
exhaust=[(.40,.34,2.05),(.53,.40,1.94),(.52,.38,1.66),(.49,.34,1.30),(.48,.29,.92),(.51,.23,.63),(.54,.21,.44)]
tube('Scarico turbina separato',exhaust,.043,dark)
for z,x,y in [(1.63,.519,.378),(1.27,.49,.335),(.89,.482,.28)]:
    torus('Fascetta scarico',.045,.006,(x,y,z),steel)
torus('Bordo scarico turbina',.043,.004,(.54,.21,.44),steel)
# Le linee esterne illustrano l'architettura; percorso non certificato.
coolant=[(.40,.03,1.98),(.49,-.10,1.85),(.45,-.28,1.65),(.34,-.36,1.30),(.28,-.40,.94),(.23,-.39,.66),(.14,-.34,.55)]
tube('Alimentazione camicia rigenerativa',coolant,.038,bright)
for i in range(2):
    flange('Giunto circuito rigenerativo %d'%i,[(.46,-.265,1.68),(.25,-.396,.75)][i],.056,bolts=8)
tube('Uscita camicia verso testa',[(-.15,-.14,1.56),(-.25,-.21,1.66),(-.26,-.26,1.86),(-.15,-.21,1.92)],.026,steel)
for loc in [(-.27,-.18,2.10),(.55,-.05,1.89)]:
    cylinder('Corpo valvola',.058,.12,loc,steel)
    cylinder('Attuatore valvola',.038,.10,(loc[0],loc[1],loc[2]+.10),black)
    flange('Chiusura valvola',(loc[0],loc[1],loc[2]+.065),.067,bolts=8)
for j in range(7):
    x=-.18+j*.021
    tube('Linea ausiliaria %02d'%j,[(x,-.14,2.08),(x-.13,-.25,2.12),(x-.19,-.30,1.96),(x-.18,-.30,1.76),(x-.11,-.25,1.65)],.0045,steel)
for j in range(4):
    tube('Cablaggio sensori %d'%j,[(-.26-j*.008,.03,2.17),(-.35-j*.009,-.10,2.01),(-.34-j*.01,-.20,1.85),(-.29-j*.01,-.20,1.55),(-.22-j*.01,-.19,1.45)],.004,rubber)
for a in [0.1,1.6,3.2,4.8]:
    x,y=.217*math.cos(a),.217*math.sin(a)
    cylinder('Boss sensore camera',.018,.045,(x,y,1.65),steel,(math.cos(a),math.sin(a),0))
    tube('Linea strumentazione',[(x,y,1.65),(x*1.2,y*1.2,1.77),(x*1.1,y*1.1,1.89)],.0032,steel)
box('Modulo controllo · involucro',(-.37,.15,2.19),(.14,.08,.21),black)
for z in [2.13,2.17,2.21,2.25]:
    box('Aletta modulo',(-.37,.103,z),(.12,.014,.008),steel)

collection('04 · Supporto cardanico e attuatori')
torus('Anello strutturale superiore',.215,.028,(0,0,2.38),steel)
torus('Anello interno snodo',.137,.025,(0,0,2.38),dark)
cylinder('Interfaccia centrale',.105,.13,(0,0,2.44),steel)
flange('Interfaccia struttura di spinta',(0,0,2.52),.149,bolts=16)
for a in [math.pi*.25,math.pi*.75,math.pi*1.25,math.pi*1.75]:
    p=(.225*math.cos(a),.225*math.sin(a),1.83)
    q=(.19*math.cos(a),.19*math.sin(a),2.37)
    strut('Tirante struttura',p,q,.024,steel)
    sphere('Snodo tirante',p,(.036,.036,.036),dark)
    sphere('Snodo superiore',q,(.034,.034,.034),steel)
for a in [3.65,5.55]:
    bot=(.20*math.cos(a),.20*math.sin(a),1.49)
    top=(.40*math.cos(a),.40*math.sin(a),2.08)
    mid=Vector(bot).lerp(Vector(top),.55)
    strut('Stelo attuatore TVC',bot,top,.016,bright)
    strut('Corpo attuatore TVC',mid,top,.032,steel)
    for co in [bot,top]:sphere('Testa snodata TVC',co,(.036,.036,.036),dark)
    tube('Linea attuatore',[(top[0],top[1],top[2]),(top[0]*1.1,top[1]*1.1,top[2]+.07),(-.22,-.18,2.16)],.006,black)

engine_cols=[c for c in bpy.data.collections if c.name[:2] in ['01','02','03','04']]
for c in engine_cols:
    c['NOTA']='Ricostruzione visiva. Quote e percorsi esterni approssimati; non CAD SpaceX.'
    for o in c.objects:o['ricostruzione_visiva']=True

collection('05 · Studio e illuminazione')
floor=metal('Studio · ardesia',(.016,.024,.034),.62,0,False)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0))
move(bpy.context.object,'Piano studio',floor)
def area(name,loc,power,color,size,target=(0,0,1.4),size_y=None):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color
    d.shape='RECTANGLE';d.size=size;d.size_y=size_y or size
    o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Key · softbox sinistra',(-3.4,-3.5,4.4),650,(.78,.87,1),3.0,size_y=4.5)
area('Rim · freddo', (2.2,2.7,3.6),950,(.54,.72,1),2.3,size_y=3.5)
area('Strip · bordo caldo',(-2.0,1.4,2.0),250,(1,.82,.61),1.0,size_y=3.0)
area('Fill · frontale',(.9,-4,2.0),200,(1,.98,.93),2.2,size_y=3.5)
area('Top',(.0,0,5),350,(.85,.91,1),2.2)
scene=bpy.context.scene
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.095,.13,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
cam_data=bpy.data.cameras.new('Camera · prospettiva principale')
cam=bpy.data.objects.new('Camera · prospettiva principale',cam_data);COL.objects.link(cam)
cam.location=(4.1,-6.6,3.4)
target=Vector((.04,0,1.34))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO';cam_data.ortho_scale=3.23;cam_data.lens=60
scene.camera=cam

collection('06 · Didascalie (disattivabili)')
white=metal('Grafica · ghiaccio',(.78,.84,.91),.7,0,False)
muted=metal('Grafica · grigio',(.32,.43,.55),.7,0,False)
accent=metal('Grafica · azzurro',(.32,.69,.95),.7,0,False)
for m in [white,muted,accent]:
    bs=m.node_tree.nodes.get('Principled BSDF')
    emission=bs.inputs.get('Emission Color') or bs.inputs.get('Emission')
    emission.default_value=m.diffuse_color
    if bs.inputs.get('Emission Strength'):
        bs.inputs['Emission Strength'].default_value=1
def label(name,body,x,y,size,mat):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.space_character=1.15
    o=bpy.data.objects.new(name,cu);COL.objects.link(o);cu.materials.append(mat)
    o.parent=cam;o.location=(x,y,-4);return o
label('Testata','PROPULSIONE / SPACEX',-1.32,1.43,.032,accent)
label('Titolo','MERLIN 1D',-1.32,1.29,.105,white)
label('Variante','SEA LEVEL',.82,1.41,.032,white)
label('Sottotitolo','FALCON 9 / FALCON HEAVY',-1.32,1.21,.028,white)
label('Nota fonti','RICOSTRUZIONE VISIVA / FONTI SPACEX',-1.32,1.16,.022,muted)

FONTI='''MERLIN 1D / SEA LEVEL
Blender 2.93 LTS. Ricostruzione visiva esterna originale, 25 ottobre 2026.

FONTI UFFICIALI
1. SpaceX, Falcon User's Guide, 9 maggio 2025, sezione 2.3, pagine 8-9
   (pagine PDF 19-20).
   https://www.spacex.com/assets/media/falcon-users-guide-2025-05-09.pdf
   Conferma M1D, LOX/RP-1, generatore di gas, turbopompa con albero unico,
   camera e ugello raffreddati rigenerativamente e iniettore pintle.
2. SpaceX, Falcon 9, sezione Engines / Merlin, Sea level.
   https://www.spacex.com/vehicles/falcon-9/
   Conferma configurazione e spinta dichiarata 845 kN al livello del mare.
3. SpaceX CRS-4 Mission Press Kit, 2014, p. 15, fotografia dei Merlin 1D.
   Documento SpaceX ospitato sul sito NASA:
   https://www.nasa.gov/wp-content/uploads/2018/07/spacex_nasa_crs-4_presskit.pdf
   Usato esclusivamente come riferimento storico dell'aspetto esterno;
   i valori di prestazione del 2014 non sono usati per il motore attuale.

LIMITI DEL MODELLO
La documentazione pubblica non contiene disegni esecutivi, quote complete
o il percorso di tutte le linee. Profilo dell'ugello, ingombri, posizioni
dei corpi pompa, tiranti, valvole, raccordi e cablaggi sono approssimati.
Le nervature esterne suggeriscono la lavorazione della camicia: non sono
una ricostruzione verificata dei canali interni. Non sono modellati
giranti, iniettore interno o cinematica funzionante del cardano.
Scala di scena indicativa (metri), non metrologica. Materiali e colori
sono interpretazioni per l'illuminazione da studio.
Non e' un asset CAD ufficiale, un disegno costruttivo o un modello
certificato da SpaceX. Nessuna immagine di terzi incorporata nel render.

USO
La camera principale e le luci sono pronte. F12 renderizza.
Le collezioni 01-04 contengono il motore. 05: studio, luci e camera.
06: didascalie, disattivabili per ottenere un'immagine pulita.
La scena e' salvata con Cycles / CPU per portabilita'.
'''
txt=bpy.data.texts.new('LEGGIMI · FONTI E LIMITI');txt.write(FONTI)
with open(os.path.join(ROOT,'FONTI_E_NOTE.md'),'w',encoding='utf-8') as f:f.write(FONTI)
scene['Fonti ufficiali']='SpaceX Falcon User Guide 2025, §2.3; SpaceX Falcon 9 / Merlin; CRS-4 Press Kit p.15.'
scene['Tipo modello']='Ricostruzione visiva esterna approssimata, non CAD ufficiale.'
scene['Blender']=bpy.app.version_string
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'
scene.cycles.device='CPU';scene.cycles.samples=32 if PREVIEW else 64
scene.cycles.use_denoising=True
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.045 if PREVIEW else .025
scene.cycles.max_bounces=7;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=4
scene.render.resolution_x=2400;scene.render.resolution_y=2600
scene.render.resolution_percentage=35 if PREVIEW else 100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
scene.render.film_transparent=False
scene.view_settings.view_transform='Filmic' if bpy.app.version<(4,0,0) else 'AgX'
try:scene.view_settings.look='Medium High Contrast' if bpy.app.version<(4,0,0) else 'AgX - Medium High Contrast'
except:pass
scene.render.filepath=os.path.join(ROOT,'merlin_1d_anteprima.png' if PREVIEW else 'merlin_1d_render.png')
# In apertura: camera e materiali visibili, senza sovrapposizione delle luci.
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.region_3d.view_perspective='CAMERA'
            ar.spaces.active.overlay.show_overlays=False
            ar.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
blend_path=os.path.join(ROOT,'Merlin_1D_Blender_2.93.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print('MODELLO_SALVATO',blend_path,flush=True)
print('OGGETTI',len(bpy.data.objects),'VERSIONE',bpy.app.version_string,flush=True)
if os.environ.get('MERLIN_SKIP_RENDER') != '1':
    bpy.ops.render.render(write_still=True)
    print('RENDER_COMPLETATO',scene.render.filepath,flush=True)
