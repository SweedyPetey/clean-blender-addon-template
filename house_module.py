import bpy
import bmesh
import math

# ——————————————————————————————————————————————————————————————————————
# MARK: INTERFACE
# ——————————————————————————————————————————————————————————————————————


class VIEW3D_PT_multi_extrude_panel(bpy.types.Panel):  # {MODULE_NAME}_PT_{panel_name}
    # MODULE_NAME: simple_module -> SIMPLE (_module is excluded)
    # The class name doubles as the panel's bl_idname, so it must be unique across all add-ons
    #bl_label = "Simple Panel"
    bl_label = "Make your choice"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_category = "Hello World"
    bl_category = "House Creator"
    bl_idname = "VIEW3D_PT_multi_extrude_panel"

    def draw(self, context):
        layout = self.layout

        #layout.operator("object.simple_operator")
        op = layout.operator("mesh.multi_extrude", text="Extrude", icon="MOD_SOLIDIFY")
        
        layout.label(text="Width:")
        layout.prop(op, "steps_y")
        layout.prop(op, "amount_y")
        
        layout.label(text="Length:")
        layout.prop(op, "steps_x")
        layout.prop(op, "amount_x")


# ——————————————————————————————————————————————————————————————————————
# MARK: OPERATORS
# ——————————————————————————————————————————————————————————————————————


class MESH_OT_multi_extrude(bpy.types.Operator):  # {CATEGORY}_OT_{operator_name}
    #bl_idname = "object.simple_operator"  # {category}.{operator_name}
    bl_idname = "mesh.multi_extrude"
    #bl_label = "Simple Operator"
    bl_label = "MODIFY"
    bl_description = "A short description of what the operator does"
    bl_options = {"REGISTER", "UNDO"}
    
    steps_y: bpy.props.IntProperty(name="Column width Y", default=4, min=0)
    amount_y: bpy.props.FloatProperty(name="Bredd per steg Y", default=4.0)
    
    steps_x: bpy.props.IntProperty(name="Column Length X", default=4, min=0)
    amount_x: bpy.props.FloatProperty(name="Längd per steg X", default=4.0)
    
    def execute(self, context):

            
        if "Empty" in bpy.data.objects:
            empty = bpy.data.objects["Empty"]            
            
        else:
            empty = bpy.data.objects.new("Empty", None) 
            empty.empty_display_type = 'PLAIN_AXES'
            
            bpy.context.collection.objects.link(empty)    

    

        # Remove mesh Cube.
        if "Cube" in bpy.data.meshes:
            mesh = bpy.data.meshes["Cube"]
            print("removing mesh", mesh)
            bpy.data.meshes.remove(mesh)
        # Check if plane exists
        if "Plane" in bpy.data.objects:
            plane_obj = bpy.data.meshes["Plane"]
            mesh = plane_obj.data
        # Create plane            
        else:
            bpy.ops.mesh.primitive_plane_add(size=4.0, location=(4, 2, 2))
            plane_obj = bpy.context.active_object
            plane_obj.rotation_euler[1] = math.radians(90)
            mesh = plane_obj.data 
            
                # Print all objects.
        for obj in bpy.data.objects:
            print(obj.name)    
           # Print all scene names in a list.
        print(bpy.data.scenes.keys())
        
        if context.active_object is None or context.active_object.type != 'MESH':
            self.report({'WARNING'}, "Chose mesh object!")
            return {'CANCELLED'}
        
        old_mode = context.active_object.mode
        if old_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
            

        bm = bmesh.from_edit_mesh(mesh)

        # hitta kanten med högst medel-Y
        start_edge = max(
            bm.edges,
            key=lambda e: (e.verts[0].co.y + e.verts[1].co.y) / 2
        )
        
        ret = bmesh.ops.extrude_edge_only(
            bm,
            edges=[start_edge]
        )

        new_verts = [
            g for g in ret["geom"]
            if isinstance(g, bmesh.types.BMVert)
        ]

        bmesh.ops.translate(
            bm,
            verts=new_verts,
            vec=(0, self.amount_y, 0)
        )
        new_edges = [
            g for g in ret["geom"]
            if isinstance(g, bmesh.types.BMEdge)
        ]

        front_edge = None

        for e in new_edges:
            if all(v in new_verts for v in e.verts):
                front_edge = e
                break  
            
        ret2 = bmesh.ops.extrude_edge_only(
            bm,
            edges=[front_edge]
        )

        new_verts2 = [
            g for g in ret2["geom"]
            if isinstance(g, bmesh.types.BMVert)
        ]

        bmesh.ops.translate(
            bm,
            verts=new_verts2,
            vec=(-self.amount_x, 0, 0)
        )
        
        print("Faces:", len(bm.faces))
        print("Edges:", len(bm.edges))
        print("Selected Edges:", len([e for e in bm.edges if e.select]))                  

#        for _ in range(self.steps_y):
#            bpy.ops.mesh.extrude_edges_move(
#                #MESH_OT_extrude_region={},
#                TRANSFORM_OT_translate={"value": (0, self.amount_y, 0)}
#            )
#  
#            
#        for _ in range(self.steps_x):
#            bpy.ops.mesh.extrude_edges_move(
#                #MESH_OT_extrude_region={},
#                TRANSFORM_OT_translate={"value": (-self.amount_x, 0, 0)}
#            )            
#            
        bpy.ops.object.mode_set(mode=old_mode)               
        return {"FINISHED"}


# ——————————————————————————————————————————————————————————————————————
# MARK: REGISTRATION
# ——————————————————————————————————————————————————————————————————————




classes = [
    MESH_OT_multi_extrude,
    VIEW3D_PT_multi_extrude_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


