
import bpy
from bpy.props import IntProperty, PointerProperty


# --------------------------------------------------
# MARK: PROPERTIES
# --------------------------------------------------

class HouseGeneratorProperties(bpy.types.PropertyGroup):

    width_modules: IntProperty(
        name="Modules",
        description="Number of modules along the width",
        default=3,
        min=1,
        max=20
    )

    length_modules: IntProperty(
        name="Modules",
        description="Number of modules along the length",
        default=4,
        min=1,
        max=20
    )

    floors: IntProperty(
        name="Floors",
        description="Number of floors",
        default=2,
        min=1,
        max=10
    )


# --------------------------------------------------
# MARK: INTERFACE
# --------------------------------------------------

class VIEW3D_PT_house_generator(bpy.types.Panel):

    bl_label = "Make your choice"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "House Creator"
    bl_idname = "VIEW3D_PT_house_generator"

    def draw(self, context):
        layout = self.layout
        props = context.scene.house_generator

        layout.label(text="Width:")
        layout.prop(props, "width_modules")

        layout.label(text="Length:")
        layout.prop(props, "length_modules")

        layout.label(text="Floors:")
        layout.prop(props, "floors")

        layout.separator()

        layout.operator(
            "object.generate_house",
            text="RUN",
            icon="MOD_SOLIDIFY"
        )


# --------------------------------------------------
# MARK: HOUSE GEOMETRY
# --------------------------------------------------

MODULE_WIDTH = 4.0
FLOOR_HEIGHT = 3.0
WALL_THICKNESS = 0.2

HOUSE_COLLECTION_NAME = "Generated_House"

WINDOW_WIDTH = 1.4
WINDOW_HEIGHT = 1.6
FRAME_THICKNESS = 0.08
GLASS_THICKNESS = 0.04

WINDOW_COLLECTION_NAME = "Generated_Windows"


def create_box(name, dimensions, location, collection):
    """Create a box mesh with exact dimensions and location."""

    dx, dy, dz = dimensions

    vertices = [
        (-dx / 2, -dy / 2, -dz / 2),
        ( dx / 2, -dy / 2, -dz / 2),
        ( dx / 2,  dy / 2, -dz / 2),
        (-dx / 2,  dy / 2, -dz / 2),
        (-dx / 2, -dy / 2,  dz / 2),
        ( dx / 2, -dy / 2,  dz / 2),
        ( dx / 2,  dy / 2,  dz / 2),
        (-dx / 2,  dy / 2,  dz / 2),
    ]

    faces = [
        (0, 3, 2, 1),  # Bottom
        (4, 5, 6, 7),  # Top
        (0, 1, 5, 4),  # Front
        (1, 2, 6, 5),  # Right
        (2, 3, 7, 6),  # Back
        (3, 0, 4, 7),  # Left
    ]

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location

    return obj


# --------------------------------------------------
# MARK: WALL MODULE WITH WINDOW OPENING
# --------------------------------------------------

def create_wall_module(
    name,
    center,
    module_width,
    floor_height,
    thickness,
    horizontal_axis,
    collection
):
    """Create four wall sections around a centered window opening."""

    window_width = min(
        WINDOW_WIDTH,
        module_width - 0.2
    )
    window_height = min(
        WINDOW_HEIGHT,
        floor_height - 0.2
    )

    side_width = (module_width - window_width) / 2
    bottom_height = (floor_height - window_height) / 2

    cx, cy, cz = center

    # Horizontal positions of the left and right wall sections.
    horizontal_offsets = [
        -(window_width / 2 + side_width / 2),
        +(window_width / 2 + side_width / 2)
    ]

    # Vertical positions of the lower and upper wall sections.
    vertical_offsets = [
        -(window_height / 2 + bottom_height / 2),
        +(window_height / 2 + bottom_height / 2)
    ]

    # Left and right wall sections span the full floor height.
    for i, offset in enumerate(horizontal_offsets):

        if horizontal_axis == "X":
            dimensions = (side_width, thickness, floor_height)
            location = (cx + offset, cy, cz)
        else:
            dimensions = (thickness, side_width, floor_height)
            location = (cx, cy + offset, cz)

        create_box(
            f"{name}_Side_{i + 1}",
            dimensions,
            location,
            collection
        )

    # Bottom and top sections span only the window width.
    for i, offset in enumerate(vertical_offsets):

        if horizontal_axis == "X":
            dimensions = (window_width, thickness, bottom_height)
        else:
            dimensions = (thickness, window_width, bottom_height)

        location = (cx, cy, cz + offset)

        create_box(
            f"{name}_Horizontal_{i + 1}",
            dimensions,
            location,
            collection
        )


def create_house_collection(context):
    """Remove the previous generated house and create a new collection."""

    old_collection = bpy.data.collections.get(
        HOUSE_COLLECTION_NAME
    )

    if old_collection is not None:
        # Remove objects belonging to the previous generated house.
        for obj in list(old_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

        # Remove the old collection itself.
        bpy.data.collections.remove(old_collection)

    collection = bpy.data.collections.new(
        HOUSE_COLLECTION_NAME
    )

    context.scene.collection.children.link(collection)

    return collection




def create_house_walls(width_modules, length_modules, floors, collection):
    """Create modular walls with window openings on all facades."""

    width = width_modules * MODULE_WIDTH
    length = length_modules * MODULE_WIDTH
    thickness = WALL_THICKNESS

    front_y = -(length / 2 - thickness / 2)
    back_y = length / 2 - thickness / 2

    left_x = -(width / 2 - thickness / 2)
    right_x = width / 2 - thickness / 2

    for floor in range(floors):

        z = floor * FLOOR_HEIGHT + FLOOR_HEIGHT / 2

        # Front and back facades.
        for i in range(width_modules):

            x = -width / 2 + MODULE_WIDTH / 2 + i * MODULE_WIDTH

            create_wall_module(
                f"Wall_Front_F{floor + 1}_M{i + 1}",
                (x, front_y, z),
                MODULE_WIDTH,
                FLOOR_HEIGHT,
                thickness,
                "X",
                collection
            )

            create_wall_module(
                f"Wall_Back_F{floor + 1}_M{i + 1}",
                (x, back_y, z),
                MODULE_WIDTH,
                FLOOR_HEIGHT,
                thickness,
                "X",
                collection
            )

        # Side facades fit between the front and back walls.
        side_lengths = [MODULE_WIDTH] * length_modules

        if length_modules == 1:
            side_lengths[0] -= 2 * thickness
        else:
            side_lengths[0] -= thickness
            side_lengths[-1] -= thickness

        y_cursor = -length / 2 + thickness

        for i, module_length in enumerate(side_lengths):

            y = y_cursor + module_length / 2
            y_cursor += module_length

            create_wall_module(
                f"Wall_Left_F{floor + 1}_M{i + 1}",
                (left_x, y, z),
                module_length,
                FLOOR_HEIGHT,
                thickness,
                "Y",
                collection
            )

            create_wall_module(
                f"Wall_Right_F{floor + 1}_M{i + 1}",
                (right_x, y, z),
                module_length,
                FLOOR_HEIGHT,
                thickness,
                "Y",
                collection
            )


#Create materials for window frames and glass

def get_or_create_material(name, color, metallic=0.0, roughness=0.5):

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True

    bsdf = material.node_tree.nodes.get("Principled BSDF")

    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness

    return material


def create_window_collection(context):

    old_collection = bpy.data.collections.get(
        WINDOW_COLLECTION_NAME
    )

    if old_collection:
        for obj in list(old_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

        bpy.data.collections.remove(old_collection)

    collection = bpy.data.collections.new(
        WINDOW_COLLECTION_NAME
    )

    context.scene.collection.children.link(collection)

    return collection

#Make the windows!

def create_window(name, location, rotation_z, collection,
                  frame_material, glass_material):

    w = WINDOW_WIDTH
    h = WINDOW_HEIGHT
    t = FRAME_THICKNESS
    g = GLASS_THICKNESS

    # Frame parts: left, right, bottom and top.
    frame_parts = [
        ("Left",  (t, g, h), (-w / 2 + t / 2, 0, 0)),
        ("Right", (t, g, h), ( w / 2 - t / 2, 0, 0)),
        ("Bottom",(w, g, t), (0, 0, -h / 2 + t / 2)),
        ("Top",   (w, g, t), (0, 0,  h / 2 - t / 2)),
    ]

    for part_name, dimensions, offset in frame_parts:

        obj = create_box(
            f"{name}_Frame_{part_name}",
            dimensions,
            (0, 0, 0),
            collection
        )

        obj.location = location
        obj.rotation_euler.z = rotation_z

        # Offset in the window's local coordinate system.
        from mathutils import Vector
        local_offset = Vector(offset)
        obj.location += local_offset @ obj.rotation_euler.to_matrix()

        obj.data.materials.append(frame_material)

    # Glass pane, slightly behind the frame.
    glass = create_box(
        f"{name}_Glass",
        (w - 2 * t, g, h - 2 * t),
        location,
        collection
    )

    glass.rotation_euler.z = rotation_z
    glass.data.materials.append(glass_material)

#Place windows on facade



def create_house_windows(context, width_modules, length_modules, floors):

    collection = create_window_collection(context)

    frame_material = get_or_create_material(
        "Window_Frame_Dark",
        (0.08, 0.08, 0.09),
        metallic=0.3,
        roughness=0.35
    )

    glass_material = get_or_create_material(
        "Window_Glass_Blue",
        (0.12, 0.35, 0.48),
        metallic=0.1,
        roughness=0.2
    )

    width = width_modules * MODULE_WIDTH
    length = length_modules * MODULE_WIDTH
    half_t = WALL_THICKNESS / 2

    # Place windows at the center of each wall's thickness.
    front_y = -length / 2 + half_t
    back_y = length / 2 - half_t
    left_x = -width / 2 + half_t
    right_x = width / 2 - half_t

    for floor in range(floors):

        z = floor * FLOOR_HEIGHT + FLOOR_HEIGHT / 2

        # Front and back facades.
        for i in range(width_modules):

            x = -width / 2 + MODULE_WIDTH / 2 + i * MODULE_WIDTH

            create_window(
                f"Window_Front_F{floor + 1}_M{i + 1}",
                (x, front_y, z),
                0,
                collection,
                frame_material,
                glass_material
            )

            create_window(
                f"Window_Back_F{floor + 1}_M{i + 1}",
                (x, back_y, z),
                0,
                collection,
                frame_material,
                glass_material
            )

        # Side facades: match the wall module lengths exactly.
        side_lengths = [MODULE_WIDTH] * length_modules

        if length_modules == 1:
            side_lengths[0] -= 2 * WALL_THICKNESS
        else:
            side_lengths[0] -= WALL_THICKNESS
            side_lengths[-1] -= WALL_THICKNESS

        y_cursor = -length / 2 + WALL_THICKNESS

        for i, module_length in enumerate(side_lengths):

            y = y_cursor + module_length / 2
            y_cursor += module_length

            create_window(
                f"Window_Left_F{floor + 1}_M{i + 1}",
                (left_x, y, z),
                1.57079632679,
                collection,
                frame_material,
                glass_material
            )

            create_window(
                f"Window_Right_F{floor + 1}_M{i + 1}",
                (right_x, y, z),
                1.57079632679,
                collection,
                frame_material,
                glass_material
            )



# --------------------------------------------------
# MARK: OPERATORS
# --------------------------------------------------

class OBJECT_OT_generate_house(bpy.types.Operator):

    bl_idname = "object.generate_house"
    bl_label = "Generate House"
    bl_description = "Generate a modular house"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

        props = context.scene.house_generator

        width_modules = props.width_modules
        length_modules = props.length_modules
        floors = props.floors

        # Create a fresh collection for the generated house.
        collection = create_house_collection(context)

        # Generate the four walls.
        create_house_walls(
            width_modules,
            length_modules,
            floors,
            collection
        )

        # Report the resulting dimensions.
        width = width_modules * MODULE_WIDTH
        length = length_modules * MODULE_WIDTH
        height = floors * FLOOR_HEIGHT

        self.report(
            {"INFO"},
            f"House created: {width:g} x {length:g} x {height:g} m"
        )
        
        create_house_windows(context,width_modules,length_modules,floors)

        return {"FINISHED"}



# --------------------------------------------------
# MARK: REGISTRATION
# --------------------------------------------------

classes = [
    HouseGeneratorProperties,
    OBJECT_OT_generate_house,
    VIEW3D_PT_house_generator
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.house_generator = PointerProperty(
        type=HouseGeneratorProperties
    )


def unregister():

    if hasattr(bpy.types.Scene, "house_generator"):
        del bpy.types.Scene.house_generator

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    
    
    
    