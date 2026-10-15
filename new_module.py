import bpy

class MyAwesomOperator(bpy.types.Operator):
    bl_idname = "object.my_awesome_operator"
    bl_label = "My Awesome Operator"
    bl_description = "Does nothing"
    bl_options = {"REGISTER", "UNDO"}
    
    
    my_input_value: bpy.props.FloatProperty(name="Value")

    def execute(self, context):

        print(self.my_input_value)  
        
        if bpy.app.version >= (5, 2, 0):
            print("we are using 5.2.0 or above")
        else:
            print("This Blender version is below 5.2.0")         
            
        return {"FINISHED"}
  
  
class MyAwesomPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hello World"
    bl_label =  "My Awesome Panel"
      
    def draw(self, context):
        layout = self.layout
          
        layout.label(text="Kolla här!", icon="BLENDER")
        layout.operator("object.object.my_awesome_operator", icon="INFO")
        
        layout.prop(context.scene, "my_prop")
          
          
          
classes = [MyAwesomOperator, MyAwesomPanel]          
basic_register, basic_unregister = bpy.utils.register_classes_factory(classes)

def register():
    basic_register()
    bpy.types.Scene.my_prop = bpy.props.StringProperty(
        name="MyProp", 
        description="En himla bra beskrivning",     
        subtype="FILE_PATH" # "DIR_PATH"
        )
    
def unregister():
    basic_unregister()
    del bpy.types.Scene.my_prop    
