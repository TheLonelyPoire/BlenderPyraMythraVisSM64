bl_info = {
    "name": "BitFS Basis Visualizer",
    "description": "",
    "author": "tlp",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import math

import bpy
from bpy.props import FloatVectorProperty, PointerProperty, FloatProperty, EnumProperty

from mathutils import Euler, Matrix, Vector


# ===========================================================

# HELPER FUNCTIONS

# ===========================================================


def rgb_to_rgba(col):
    return (col[0], col[1], col[2], 1.0)


def yaw_to_rad(yaw):
    return yaw * math.pi / 32768


def get_platform_pos():
    if bpy.context.scene.panel_props.platform == 'Pyra':
       return (-1945, -3225, -715)
    else:
        return (-2866, -3225, -715)


def mario_to_blender(pt_lst_or_vec):
    offset = get_platform_pos()

    if type(pt_lst_or_vec) == tuple:
        return ((pt_lst_or_vec[0] - offset[0]) / 100, -(pt_lst_or_vec[2] - offset[2]) / 100, (pt_lst_or_vec[1] - offset[1]) / 100)
    elif type(pt_lst_or_vec) == list:
        new_pts = []
        for pt in pt_lst_or_vec:
            new_pts.append(((pt[0] - offset[0]) / 100, -(pt[2] - offset[2]) / 100, (pt[1] - offset[1]) / 100))
        return new_pts
    elif type(pt_lst_or_vec == Vector):
        return Vector(((pt_lst_or_vec[0] - offset[0]) / 100, -(pt_lst_or_vec[2] - offset[2]) / 100, (pt_lst_or_vec[1] - offset[1]) / 100))
    else:
        return None


def set_obj_pos(obj, new_position, apply_mario_conversion=True, offset_override=None):

    mb = obj.matrix_basis

    if apply_mario_conversion:
        offset = get_platform_pos() if offset_override == None else offset_override

        mb[0][3] = (new_position[0] - offset[0]) / 100
        mb[1][3] = -(new_position[2] - offset[2]) / 100
        mb[2][3] = (new_position[1] - offset[1]) / 100

    else:
        mb[0][3] = new_position[0]
        mb[1][3] = new_position[1]
        mb[2][3] = new_position[2]


def scale_position_markers(radius):
    marker_list = ["Mario", "MarioStep", "MarioExpected"]
    for name in marker_list:
        obj = bpy.context.scene.objects.get(name)
        obj.scale = (radius,radius,radius)


def spawn_pyra_mythra(name="PyraMythra", hide=False):
    
    verts = [(  0.0,   0.0,  0.0),
             ( 3.07, 3.06, 3.07),
             (-3.06, 3.06, 3.07),
             (-3.06, -3.07,  3.07),
             ( 3.07, -3.07,  3.07)]
        
    faces = [(0,2,1),
             (0,3,2),
             (0,1,4),
             (0,4,3),
             (1,2,3),
             (1,3,4)]
            
    edges = []

    mesh_data = bpy.data.meshes.new("pyramid_data")
    mesh_data.from_pydata(verts, edges, faces)

    mesh_obj = bpy.data.objects.new(name, mesh_data)

    bpy.context.collection.objects.link(mesh_obj)

    mesh_obj.hide_set(hide)
    
   
def spawn_basis_vecs(parent_name="PyraMythra", 
                     left_color=(1,0,0,1),
                     up_color=(0,1,0,1),
                     forward_color=(0,0,1,1),
                     radius=0.1,
                     length=2.5,
                     hide=False):
    
    platform = bpy.context.scene.objects.get(parent_name)

    up_material      = spawn_emissive_material(parent_name + "PlatformUpMaterial",      up_color, 1)
    left_material    = spawn_emissive_material(parent_name + "PlatformLeftMaterial",    left_color, 1)
    forward_material = spawn_emissive_material(parent_name + "PlatformForwardMaterial", forward_color, 1)

    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(0,0,3.07 + length/2))
    bpy.context.object.name = parent_name + "PlatformUp"
    bpy.context.object.data.materials.append(up_material)
    bpy.context.object.parent = platform
    bpy.context.object.hide_set(hide)

    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(length/2,0,3.07))
    bpy.context.object.name = parent_name + "PlatformLeft"
    bpy.context.object.rotation_euler[1] = math.pi/2
    bpy.context.object.data.materials.append(left_material)
    bpy.context.object.parent = platform 
    bpy.context.object.hide_set(hide)

    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(0,-length/2,3.07))
    bpy.context.object.name = parent_name + "PlatformForward"
    bpy.context.object.rotation_euler[0] = math.pi/2 
    bpy.context.object.data.materials.append(forward_material)
    bpy.context.object.parent = platform
    bpy.context.object.hide_set(hide)


def spawn_fire_sea():
    verts = [(-81.92,  81.92, 2.08),
             (-81.92, -81.92, 2.08),
             ( 81.92, -81.92, 2.08),
             ( 81.92,  81.92, 2.08)]
    
    faces = [(0,1,3),
             (1,2,3)]

    edges = []

    mesh_data = bpy.data.meshes.new("fire_sea_data")
    mesh_data.from_pydata(verts, edges, faces)

    mesh_obj = bpy.data.objects.new("FireSea", mesh_data)

    bpy.context.collection.objects.link(mesh_obj)

    sea_mat = spawn_emissive_material("FireSeaMaterial", (1.0, 0.02, 0, 0.75), 2)

    mesh_obj.data.materials.append(sea_mat)


def spawn_pos_marker(name : str, color=(0.5,0.5,0.5,1), strength=1, radius=1, loc=(0,-3225,-715)):

    marker_mat = spawn_emissive_material(name + "Mat", color, strength)

    bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, location=Vector(mario_to_blender(loc)))
    bpy.context.object.name = name
    bpy.context.object.data.materials.append(marker_mat)


# Create new emissive material if it doesn't yet exist, and sets the color/strength properties to those specified (modified from https://vividfax.github.io/2021/01/14/blender-materials.html)
def spawn_emissive_material(name, col, strength):
    mat = bpy.data.materials.get(name)
    
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.links.clear()
    mat.node_tree.nodes.clear()
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Diffuse Shader
    shader = nodes.new(type='ShaderNodeEmission')
    shader.inputs["Color"].default_value = col
    shader.inputs["Strength"].default_value = strength

    # Overall Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')

    links.new(shader.outputs["Emission"], output.inputs[0])

    return mat


def linear_mtxf_mul_vec3f(m, v):
    dst = Vector((0,0,0))
    for i in range(3):
        dst[i] = m[0][i] * v[0] + m[1][i] * v[1] + m[2][i] * v[2]
    return dst


def linear_mtxf_transpose_mul_vec3f(m, v):
    dst = Vector((0,0,0))
    for i in range(3):
        dst[i] = m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2]
    return dst


def get_basis(up_dir, yaw):
    lateral_dir = Vector((math.sin(yaw), 0, math.cos(yaw)))
    up_dir_n = up_dir.normalized()

    left_dir = up_dir_n.cross(lateral_dir)
    left_dir_n = left_dir.normalized()

    forward_dir = left_dir_n.cross(up_dir_n)
    forward_dir_n = forward_dir.normalized()

    return left_dir_n, up_dir_n, forward_dir_n


def mtxf_align_terrain_normal(up_dir, yaw=0):
    left_dir_n, up_dir_n, forward_dir_n = get_basis(up_dir, yaw)

    if bpy.context.scene.panel_props.platform == 'Pyra':
        pos = (-1945, -3225, -715)
    else:
        pos = (-2866, -3225, -715)

    dest = Matrix()
    b_dest = Matrix()

    dest[0][0] = left_dir_n[0]
    dest[0][1] = left_dir_n[1]
    dest[0][2] = left_dir_n[2]
    dest[3][0] = pos[0]

    dest[1][0] = up_dir_n[0]
    dest[1][1] = up_dir_n[1]
    dest[1][2] = up_dir_n[2]
    dest[3][1] = pos[1]

    dest[2][0] = forward_dir_n[0]
    dest[2][1] = forward_dir_n[1]
    dest[2][2] = forward_dir_n[2]
    dest[3][2] = pos[2]

    dest[0][3] = 0.0
    dest[1][3] = 0.0
    dest[2][3] = 0.0
    dest[3][3] = 1.0


    b_dest[0][0] = left_dir_n[0]
    b_dest[0][1] = -left_dir_n[2]
    b_dest[0][2] = left_dir_n[1]
    b_dest[3][0] = 0

    b_dest[1][0] = -forward_dir_n[0]
    b_dest[1][1] = forward_dir_n[2]
    b_dest[1][2] = -forward_dir_n[1]
    b_dest[3][1] = 0

    b_dest[2][0] = up_dir_n[0]
    b_dest[2][1] = -up_dir_n[2]
    b_dest[2][2] = up_dir_n[1]
    b_dest[3][2] = 0

    b_dest[0][3] = 0.0
    b_dest[1][3] = 0.0
    b_dest[2][3] = 0.0
    b_dest[3][3] = 1.0

    return dest, b_dest.transposed()


def approach_by_increment(goal, src, inc):
    if src <= goal:
        if goal - src < inc:
            new_val = goal
        else:
            new_val = src + inc
    elif goal - src > -inc:
        new_val = goal
    else:
        new_val = src - inc
    
    return new_val


def bhv_tilting_inverted_pyramid_loop(transform, 
                                      platform_normal, 
                                      mario_position, 
                                      mario_platform_is_pyramid=True, 
                                      o_tilting_pyramid_mario_on_platform=True):
    mario_on_platform = False
    platform_pos = get_platform_pos()
    mario_position_v = Vector((mario_position[0], mario_position[1], mario_position[2]))

    if (mario_platform_is_pyramid): # Normally this checks whether mario's platform is the pyramid, here we just set this to true always
        dist = Vector((mario_position[0] - platform_pos[0], mario_position[1] - platform_pos[1], mario_position[2] - platform_pos[2]))
        pos_before_rotation = linear_mtxf_mul_vec3f(transform, dist)

        dx = dist[0]
        dy = 500
        dz = dist[2]
        d = math.sqrt(dx *dx + dy * dy + dz * dz)

        if d != 0:
            d = 1.0 / d
            dx *= d
            dy *= d
            dz *= d

        else:
            dx = 0.0
            dy = 1.0
            dz = 0.0

        if o_tilting_pyramid_mario_on_platform:
            mario_on_platform = True

        o_tilting_pyramid_mario_on_platform = True

    else:
        dx = 0.0
        dy = 1.0
        dz = 0.0 
        o_tilting_pyramid_mario_on_platform = False

    platform_normal[0] = approach_by_increment(dx, platform_normal[0], 0.01)
    platform_normal[1] = approach_by_increment(dy, platform_normal[1], 0.01)
    platform_normal[2] = approach_by_increment(dz, platform_normal[2], 0.01)

    new_transform, b_new_transform = mtxf_align_terrain_normal(platform_normal)
    new_mario_position = mario_position

    if mario_on_platform:
        pos_after_rotation = linear_mtxf_mul_vec3f(new_transform, dist)
        new_mario_position = mario_position_v + (pos_after_rotation - pos_before_rotation)

    
    return platform_normal, new_transform, b_new_transform, new_mario_position, (dx,dy,dz), pos_before_rotation, pos_after_rotation, 


def update_scene(self, context):
    
    # Update starting normal based on panel value
    prop_normal = context.scene.panel_props.normal
    new_normal = Vector((prop_normal[0], prop_normal[1], prop_normal[2]))

    new_transform, b_new_transform = mtxf_align_terrain_normal(new_normal)
    platform = bpy.context.scene.objects.get("PyraMythra")
    platform.matrix_basis = b_new_transform

    # Update starting mario position based on panel value
    new_position = context.scene.panel_props.mario_position

    mario = bpy.context.scene.objects.get("Mario")
    set_obj_pos(mario, new_position)

    # Run one step of platform movement and update remaining visualizer objects
    step_normal, step_transform, b_step_transform, step_mario_position, (dx, dy, dz), step_before_pos, step_after_pos = bhv_tilting_inverted_pyramid_loop(new_transform, new_normal, new_position)
    step_platform = bpy.context.scene.objects.get("PyraMythraStep")
    step_platform.matrix_basis = b_step_transform

    mario_step = bpy.context.scene.objects.get("MarioStep")
    set_obj_pos(mario_step, step_mario_position)

    offset = get_platform_pos()
    dist = Vector((new_position[0] - offset[0], new_position[1] - offset[1], new_position[2] - offset[2]))
    print("Dist: ", dist)
    local = linear_mtxf_transpose_mul_vec3f(new_transform, dist)
    print("Local: ", local)
    mario_expected_position = linear_mtxf_mul_vec3f(step_transform, local) + Vector(offset)
    print("Expected Step: ", mario_expected_position)
    mario_expected_step = bpy.context.scene.objects.get("MarioExpected")
    set_obj_pos(mario_expected_step, mario_expected_position)

    scale_position_markers(context.scene.panel_props.radius)

    context.scene.panel_props.dx = dx
    context.scene.panel_props.dy = dy
    context.scene.panel_props.dz = dz
    context.scene.panel_props.step_normal = step_normal
    context.scene.panel_props.pos_before_rotation = (step_before_pos[0], step_before_pos[1], step_before_pos[2])
    context.scene.panel_props.pos_after_rotation = (step_after_pos[0], step_after_pos[1], step_after_pos[2])
    context.scene.panel_props.step_mario_position = (step_mario_position[0], step_mario_position[1], step_mario_position[2])
    context.scene.panel_props.displacement = step_after_pos[1] - step_before_pos[1]
    context.scene.panel_props.expected_mario_position = (mario_expected_position[0], mario_expected_position[1], mario_expected_position[2])
    context.scene.panel_props.expected_displacement = mario_expected_position[1] - new_position[1]


# ===========================================================

# CLASSES

# ===========================================================


class PyraMythraPanelProperties(bpy.types.PropertyGroup):

    platform : EnumProperty(name="Platform", 
                            description="The platform which is being visualized (used for coordinate conversions).",
                            items = [('Pyra', "Pyra", "Pyra"), 
                                     ('Mythra', "Mythra", "Mythra")],
                            default='Pyra',
                            update=update_scene)


    normal : FloatVectorProperty(name='Platform Normal', 
                                 description='The normal of the pyramid platform.', 
                                 size=3, 
                                 default=(0,1,0), 
                                 update=update_scene)
    
    mario_position : FloatVectorProperty(name='Mario Pre-Displacement Position', 
                                 description='The position Mario is at before the PU platform displacement.', 
                                 size=3, 
                                 default=(0,-3225,-715), 
                                 update=update_scene)
    
    radius : FloatProperty(name='Position Marker Radius',
                           description='The radius of the sphere used to show positions.',
                           default=1,
                           min=0,
                           update=update_scene)
    
    dx : FloatProperty(name="dx", description="The value of the variable dx.", default=0)
    dy : FloatProperty(name="dy", description="The value of the variable dy.", default=0)
    dz : FloatProperty(name="dz", description="The value of the variable dz.", default=0)

    step_normal : FloatVectorProperty(name="Post-Step Normal",
                                 description='The normal of platform after the platform movement step is performed.',
                                 size=3,
                                 default=(0,1,0))

    pos_before_rotation : FloatVectorProperty(name="posBeforeRotation",
                                 description='The value of the variable posBeforeRotation.',
                                 size=3,
                                 default=(0,-3225,-715))
    
    pos_after_rotation : FloatVectorProperty(name="posAfterRotation",
                                 description='The value of the variable posAfterRotation.',
                                 size=3,
                                 default=(0,-3225,-715))
    
    step_mario_position : FloatVectorProperty(name='Mario Post-Displacement Position', 
                                 description='The position Mario is at after the PU platform displacement.', 
                                 size=3, 
                                 default=(0,-3225,-715))

    displacement : FloatProperty(name="Vertical Displacement",
                                 description='The amount of vertical displacement the platform applies to Mario.',
                                 default=0.0)
    
    expected_mario_position : FloatVectorProperty(name='Expected Mario Position', 
                                 description='The position Mario would be at after the PU platform displacement if transforms were applied correctly.', 
                                 size=3, 
                                 default=(0,-3225,-715))

    expected_displacement : FloatProperty(name="Expected Vertical Displacement",
                                 description='The amount of vertical displacement the platform would apply to Mario if transforms were applied correctly.',
                                 default=0.0)


class SpawnPyramid(bpy.types.Operator):
    """Spawn Pyramid Into Scene"""
    bl_idname = "pyramythra.generate_platform"
    bl_label = "Spawn Scene"

    def execute(self, context):

        pyramythra = bpy.context.scene.objects.get("PyraMythra")
        if not pyramythra:
            spawn_pyra_mythra()
            spawn_basis_vecs()

        pyramythra_step = bpy.context.scene.objects.get("PyraMythraStep")
        if not pyramythra_step:
            spawn_pyra_mythra("PyraMythraStep", hide=True)
            spawn_basis_vecs(parent_name="PyraMythraStep", 
                             left_color=(1,0,1,1),
                             up_color=(1,1,0,1),
                             forward_color=(0,1,1,1),
                             hide=True)

        firesea = bpy.context.scene.objects.get("FireSea")
        if not firesea:
            spawn_fire_sea()

        mario = bpy.context.scene.objects.get("Mario")
        if not mario:
            spawn_pos_marker("Mario", color=(0.5, 0, 0, 1))

        mario_step = bpy.context.scene.objects.get("MarioStep")
        if not mario_step:
            spawn_pos_marker("MarioStep", color=(0.1, 0.6, 1.0, 1))
        
        mario_expected_step = bpy.context.scene.objects.get("MarioExpected")
        if not mario_expected_step:
            spawn_pos_marker("MarioExpected", color=(0.75, 0.25, 0, 1))

        return {'FINISHED'}
    

class PyraMythraPanel(bpy.types.Panel):
    bl_idname = "pyramythra.mainpanel"
    bl_label = "Pyra/Mythra Basis Visualizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SM64'
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        panel_props = scene.panel_props

        offset = get_platform_pos()

        col = layout.column(align=True)
        col.operator(SpawnPyramid.bl_idname, text=SpawnPyramid.bl_label, icon="SHADING_WIRE")

        layout.separator()

        row = layout.row(align=True)
        row.prop(panel_props, "platform")

        layout.separator()

        row = layout.row(align=True)
        row.prop(panel_props, "normal")

        layout.separator()

        row = layout.row(align=True)
        row.prop(panel_props, "mario_position")

        layout.separator()

        row = layout.row(align=True)
        row.prop(panel_props, "radius")

        layout.separator()

        row = layout.row(align=True)
        row.label(text=f"Platform to Mario Vector: ({context.scene.panel_props.mario_position[0] - offset[0]}, {context.scene.panel_props.mario_position[1] - offset[1]}, {context.scene.panel_props.mario_position[2] - offset[2]})")

        layout.separator()

        row = layout.row(align=True)
        row.label(text=f"dx: {context.scene.panel_props.dx}   dy: {context.scene.panel_props.dy}  dz: {context.scene.panel_props.dz}")

        layout.separator()

        col = layout.column(align=True)
        col.label(text=f"Post-Step Platform Normal: ({context.scene.panel_props.step_normal[0]}, {context.scene.panel_props.step_normal[1]}, {context.scene.panel_props.step_normal[2]})")
        col.label(text=f"posBeforeRotation: ({context.scene.panel_props.pos_before_rotation[0]}, {context.scene.panel_props.pos_before_rotation[1]}, {context.scene.panel_props.pos_before_rotation[2]})")
        col.label(text=f"posAfterRotation: ({context.scene.panel_props.pos_after_rotation[0]}, {context.scene.panel_props.pos_after_rotation[1]}, {context.scene.panel_props.pos_after_rotation[2]}) ")

        layout.separator()

        col = layout.column(align=True)
        col.label(text=f"Mario Post-Displacement Position: ({context.scene.panel_props.step_mario_position[0]}, {context.scene.panel_props.step_mario_position[1]}, {context.scene.panel_props.step_mario_position[2]}) ")
        col.label(text=f"Vertical Displacement: {context.scene.panel_props.displacement}")

        layout.separator()

        col = layout.column(align=True)
        col.label(text=f"Mario Post-Displacement Expected Position: ({context.scene.panel_props.expected_mario_position[0]}, {context.scene.panel_props.expected_mario_position[1]}, {context.scene.panel_props.expected_mario_position[2]}) ")
        col.label(text=f"Expected Vertical Displacement: {context.scene.panel_props.expected_displacement}")


# ===========================================================

# REGISTERING

# =========================================================== 


classes = [
    PyraMythraPanel,
    SpawnPyramid,
    PyraMythraPanelProperties
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls) 

    bpy.types.Scene.panel_props = PointerProperty(type=PyraMythraPanelProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.panel_props
        
        
if __name__ == "__main__":
    register()

