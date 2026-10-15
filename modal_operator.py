import bpy

class MyModalOperator(bpy.types.Operator):
    bl_idname = "view3d.my_modal"
    bl_label = "My Modal"
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
    
    
    def modal(self, context, event):
        if event.type == "MOUSEMOVE":
            print(event.mouse_x, event.mouse_y)
        elif event.type in {"ESC", "RIGHTMOUSE"}:
            return {"CANCELLED"}
        elif event.type in {"RET", "LEFTMOUSE"}:
            return {"FINISHED"}
        
        return {"RUNNING_MODAL"}
    
classes = [MyModalOperator]    

register, unregister = bpy.utils.register_classes_factory(classes)