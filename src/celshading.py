bl_info = {
    "name": "Creative",
    "author": "Shaocr",
    "version": "1.0.0",
    "function": "CelShading",
    "location": "3D View > Tools"
}
DefaultMaterialName = "CelShadingMaterial"
Second_mix_color2 = (0.5,0.4,0.4,1)


# ------------------------------------------------------------------------
#    import packages
# ------------------------------------------------------------------------
import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Operator
# ------------------------------------------------------------------------



class BuildNodeTreeforObject(bpy.types.Operator):
    bl_idname = "object.celshading"        # Unique identifier for buttons and menu items to reference.
    bl_label = "AddCelMaterial"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}
    def __init__(self):
        #change blender's mode of way of rendering to GLSL
        bpy.data.scenes["Scene"].game_settings.material_mode='GLSL'

        # get obj
        self.obj = bpy.context.active_object

        # merge obj's name and the default material's name
        self.material_name = DefaultMaterialName+'_'+self.obj.name

        # if material does not exists,then create a new one
        self.mat = (bpy.data.materials.get(self.material_name) or
            bpy.data.materials.new(self.material_name))

        # enable material's TreeNode
        self.mat.use_nodes = True

        # get material's nodetree
        self.nodes = self.mat.node_tree.nodes
        self.links = self.mat.node_tree.links
    def Build(self):

        # change the setting of node of material
        self.mat.diffuse_color = (1, 1, 1)
        self.mat.diffuse_intensity = 1
        self.mat.specular_intensity = 0
        
        # assign material to the material node
        # get input node and fix its location
        input = self.nodes['Material']
        input.material = self.mat
        input.location = (600,120)
        
        #get output node and fix its location
        output = self.nodes['Output']
        output.location = (1400,160)
        
        #Add colorramp 
        ColorRamp_node = self.nodes.new('ShaderNodeValToRGB')
        ColorRamp_node.color_ramp.elements[0].position = 0.18
        ColorRamp_node.color_ramp.elements[0].color=(1,1,1,1)
        ColorRamp_node.color_ramp.elements[1].position = 0.181
        ColorRamp_node.color_ramp.elements[1].color=(0,0,0,1)
        ColorRamp_node.location = (800,120)
        
        #Add mix node
        mix_node = self.nodes.new('ShaderNodeMixRGB')
        mix_node.location = (1200,160)
        mix_node.blend_type = 'MULTIPLY'
        mix_node.inputs[2].default_value=(0.5,0.200,0.151,1)
        
        #Add Geometry node
        geometry_node = self.nodes.new('ShaderNodeGeometry')
        geometry_node.location = (800,-100)
        
        #Add HueSaturation node
        HueSaturation_node = self.nodes.new('ShaderNodeHueSaturation')
        HueSaturation_node.location = (1000,-100)
        HueSaturation_node.inputs[1].default_value=2
        
        #link
        self.links.new(input.outputs['Color'],ColorRamp_node.inputs['Fac'])
        self.links.new(ColorRamp_node.outputs['Color'],mix_node.inputs['Fac'])
        self.links.new(mix_node.outputs['Color'],output.inputs['Color'])
        self.links.new(geometry_node.outputs['Vertex Color'],HueSaturation_node.inputs['Color'])
        self.links.new(HueSaturation_node.outputs['Color'],mix_node.inputs['Color1'])

    def execute(self,context):
        #self.__init__()
        self.Build()
        
        #if material_slot does not exist create one 
        if len(self.obj.material_slots) == 0:
            bpy.ops.object.material_slot_add()
        #get Material
        self.obj.material_slots[0].material=self.mat
        return {'FINISHED'}



class ShadowSettng(bpy.types.Operator):
    bl_idname = "shadowsetting.button"
    bl_label = "ShadowSetting"
    bl_options = {'REGISTER', 'UNDO'}
    Intensity= bpy.props.FloatProperty(name="intensity", default=0.18,min=0, max=1)
    Saturation = bpy.props.FloatProperty(name='Saturation', default=2, min=0, max=2)
    Color = bpy.props.FloatVectorProperty(name="ColorSelect",
                                          description="Returns a vector of length 4",
                                          default=Second_mix_color2,
                                          min=0.0,
                                          max=1.0,
                                          subtype='COLOR',
                                          size=4)
    def __init__(self):
        self.obj = None
    def init(self,context):
        # get current active obj
        self.obj = context.active_object

        # get obj's mat
        self.mat = bpy.data.materials.get(DefaultMaterialName + '_' + self.obj.name)

        # get material's nodes
        self.nodes = self.mat.node_tree.nodes

        # get ColorRamp_node
        self.ColorRamp_node = self.nodes['ColorRamp']

        # get min_node
        self.mix_node = self.nodes['Mix']

        # get Saturation node
        self.Saturation_node = self.nodes['Hue Saturation Value']

        self.ColorRamp_node.color_ramp.elements[0].position = self.Intensity
        self.ColorRamp_node.color_ramp.elements[1].position = self.Intensity + 0.001
        self.mix_node.inputs[2].default_value = self.Color
        self.Saturation_node.inputs[1].default_value = self.Saturation
    def execute(self, context):
        if context.active_object != self.obj:
            self.init(context)
        self.ColorRamp_node.color_ramp.elements[0].position = self.Intensity
        self.ColorRamp_node.color_ramp.elements[1].position = self.Intensity+0.001
        self.mix_node.inputs[2].default_value=self.Color
        self.Saturation_node.inputs[1].default_value = self.Saturation
        return {'FINISHED'}



class AddShadeless(bpy.types.Operator):
    bl_idname = "addshadeless.button"
    bl_label = "AddShadeless"
    bl_options = {'REGISTER', 'UNDO'}
    def __init__(self):
        # get current active obj
        self.obj = bpy.context.active_object

        # get number of material_slot
        self.len_material_slot = len(self.obj.material_slots)

        # Add new material_slot for object which is actived
        bpy.ops.object.material_slot_add()

        #create new material for material_slot
        self.mat = bpy.data.materials.new(self.obj.name+str(self.len_material_slot))
    def execute(self,context):
        self.obj.material_slots[self.len_material_slot].material = self.mat
        self.mat.use_shadeless = True
        return {'FINISHED'}
class InitializeSceneNode(bpy.types.Operator):
    bl_idname = "InitalizeSceneNode.button"
    bl_label = "InitSceneNode"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self):
        pass
# ------------------------------------------------------------------------
#    Menus
# ------------------------------------------------------------------------

class OBJECT_MT_CustomMenu(bpy.types.Menu):
    bl_idname = "object.custom_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator(BuildNodeTreeforObject.bl_idname)


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_idname = "object.custom_panel"
    bl_label = "Creative"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "creative"
    bl_context = "objectmode"



    def draw(self, context):
        layout = self.layout
        scene = context.scene
        #mytool = scene.my_tool
        layout.label("Setting")
        layout.operator(BuildNodeTreeforObject.bl_idname)
        layout.operator(AddShadeless.bl_idname)
        layout.operator(ShadowSettng.bl_idname)
        #layout.operator(ShadowColor.bl_idname)
        #layout.separator()

def menu_func(self, context):
    self.layout.operator(ShadowSettng.bl_idname)
# store keymaps here to access after registration
addon_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(ShadowSettng.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
        kmi.properties.Intensity = 0.18
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_module(__name__)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.types.VIEW3D_MT_object.remove(menu_func)
# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
