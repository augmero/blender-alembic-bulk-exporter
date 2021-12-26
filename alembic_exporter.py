import bpy

bl_info = {
    "name": "augmero - alembic exporter",
    "description": "batch exports alembics",
    "author": "augmero",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "tracker_url": "https://twitter.com/augmero_nsfw",
    "support": "TESTING",
    "category": "Import-Export"
}  

# NOTES, READ BEFORE RUNNING THIS
# Save your progress before running 
#   Blender doesn't update UI while scripts are running so if it's going for too long you may have to give up and restart blender to figure out why it was taking so long
# Performance: exclude heavy collections to make the export run faster

# Possible causes for errors:
#   Something was selected, I usually select one of my exports and then deselect to make sure it's clear
#   Typo in the names of the exports
#   blender doesn't like the mesh for some reason (try exporting from the normal UI and see if you get the same error)

# This script uses manual data entry, not very user friendly I know
# Important things to enter in:
    # bakeList for all of the objects you want to bake and the filenames to export

# If the alembic animation doesn't look quite right and you're using constraints, there's some blender jank I ran into at one point that I don't think they are fixing https://developer.blender.org/T71986

# https://docs.blender.org/api/current/bpy.ops.wm.html?#bpy.ops.wm.alembic_export


scene = bpy.context.scene
startFrame = scene.frame_start
endFrame = scene.frame_end
# comment out or remove the above 3 lines and set start and end frame manually if you want
#startFrame = 3
#endFrame = 550
path = bpy.path.abspath("//")


# DOESN'T DESELECT HIDDEN THINGS (or objects in excluded collections) FOR SOME REASON
def deselect():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    # bpy.ops.object.select_all(action='DESELECT')


def baker(objectNames, fileName):
    deselect()
    # Make sure the object is in viewport to bake
    for name in objectNames:
        bpy.data.objects[bake.objName].hide_viewport = False
        bpy.data.objects[bake.objName].hide_render = False
        bpy.data.objects[name].select_set(True)

    bpy.ops.wm.alembic_export(filepath=path+fileName+'.abc', selected=True,
                              start=startFrame, end=endFrame, global_scale=10, evaluation_mode='VIEWPORT')

    # Clean up after yourself
    for name in objectNames:
        bpy.data.objects[name].select_set(False)
        bpy.data.objects[bake.objName].hide_viewport = True
        bpy.data.objects[bake.objName].hide_render = True


class BakeObj():
    def __init__(self, in1, in2):
        self.objName = in1
        self.fileName = in2

# This is the important one to change
# First string is the name of the object in blender
# Second string is whatever you want to call the file that will be exported
bakeList = [
    BakeObj('cage rm applied', 'cage baked'),
    BakeObj('hands manifold', 'hands baked'),
    BakeObj('BONES_RIBCAGE', 'ribcage baked'),
    BakeObj('BONES_PELVIS', 'pelvis baked'),
    BakeObj('floor collider', 'floor collider'),
]

# first hide_viewport and hide_render for all bakes
for bake in bakeList:
    bpy.data.objects[bake.objName].hide_viewport = True
    bpy.data.objects[bake.objName].hide_render = True

for bake in bakeList:
    baker([bake.objName], bake.fileName)

# reset hide_viewport and hide_render for all bakes
for bake in bakeList:
    bpy.data.objects[bake.objName].hide_viewport = False
    bpy.data.objects[bake.objName].hide_render = False

deselect()
