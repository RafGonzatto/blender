import bpy
import math
import mathutils

# Remove all lights
for light in list(bpy.data.lights):
    bpy.data.lights.remove(light, do_unlink=True)

# Ensure camera exists
cam = bpy.data.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new(name='Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    bpy.context.collection.objects.link(cam)

# Collect scene objects to determine center
mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type in {'MESH','CURVE','SURFACE','META','FONT'}]
if not mesh_objs:
    center = mathutils.Vector((0.0,0.0,0.0))
    radius = 1.0
else:
    min_co = mathutils.Vector((1e10,1e10,1e10))
    max_co = mathutils.Vector((-1e10,-1e10,-1e10))
    for obj in mesh_objs:
        for v in obj.bound_box:
            world_v = obj.matrix_world @ mathutils.Vector(v)
            min_co.x = min(min_co.x, world_v.x)
            min_co.y = min(min_co.y, world_v.y)
            min_co.z = min(min_co.z, world_v.z)
            max_co.x = max(max_co.x, world_v.x)
            max_co.y = max(max_co.y, world_v.y)
            max_co.z = max(max_co.z, world_v.z)
    center = (min_co + max_co) / 2
    radius = max(max_co - min_co) / 2

# Create focus empty
focus = bpy.data.objects.get('FocusTarget')
if focus is None:
    focus = bpy.data.objects.new('FocusTarget', None)
    focus.location = center
    bpy.context.collection.objects.link(focus)
else:
    focus.location = center

# Position camera
cam.location = center + mathutils.Vector((0, -radius*3, radius))
cam.data.lens = 50

# Track to constraint
track = cam.constraints.get('TrackTo')
if track is None:
    track = cam.constraints.new(type='TRACK_TO')
track.target = focus
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# Lights
collection = bpy.context.collection

# Key light
key_light = bpy.data.lights.new(name='Key_Light', type='AREA')
key_light.energy = 1000
key_obj = bpy.data.objects.new('Key_Light', key_light)
key_obj.location = center + mathutils.Vector((radius, -radius, radius))
key_obj.rotation_euler = (math.radians(-45), 0, math.radians(45))
collection.objects.link(key_obj)

# Fill light
fill_light = bpy.data.lights.new(name='Fill_Light', type='POINT')
fill_light.energy = 300
fill_obj = bpy.data.objects.new('Fill_Light', fill_light)
fill_obj.location = center + mathutils.Vector((-radius, -radius, radius*0.5))
collection.objects.link(fill_obj)

# Rim light
rim_light = bpy.data.lights.new(name='Rim_Light', type='AREA')
rim_light.energy = 800
rim_light.color = (0.6, 0.6, 1.0)
rim_obj = bpy.data.objects.new('Rim_Light', rim_light)
rim_obj.location = center + mathutils.Vector((0, radius, radius))
rim_obj.rotation_euler = (math.radians(45), 0, math.radians(180))
collection.objects.link(rim_obj)

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
# Use GPU if available
prefs = bpy.context.preferences
if hasattr(prefs, 'addons') and 'cycles' in prefs.addons:
    cycles_prefs = prefs.addons['cycles'].preferences
    cycles_prefs.compute_device_type = 'CUDA'
    scene.cycles.device = 'GPU'
else:
    scene.cycles.device = 'CPU'
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.cycles.use_denoising = True
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False

# Volume scatter
scene.world.use_nodes = True
nodes = scene.world.node_tree.nodes
links = scene.world.node_tree.links
vol_node = nodes.new('ShaderNodeVolumeScatter')
vol_node.location = (-200,0)
vol_node.inputs['Density'].default_value = 0.02
links.new(vol_node.outputs['Volume'], nodes['World Output'].inputs['Volume'])

# Save file
bpy.ops.wm.save_mainfile()
