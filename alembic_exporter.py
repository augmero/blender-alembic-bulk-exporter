import bpy

bl_info = {
    "name": "augmero - alembic exporter",
    "description": "batch exports alembics",
    "author": "augmero",
    "version": (0, 3),
    "blender": (3, 5, 1),
    "tracker_url": "https://twitter.com/augmero_nsfw",
    "doc_url": "https://github.com/augmero/blender-alembic-bulk-exporter",
    "support": "TESTING",
    "category": "Import-Export",
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
# startFrame = scene.frame_start
# endFrame = scene.frame_end
# comment out or remove the above 3 lines and set start and end frame manually if you want
startFrame = 10
endFrame = 300
path = bpy.path.abspath("//")


class BakeObj:
    def __init__(self, in1, in2):
        self.objName = in1
        self.fileName = in2


# This is the important one to change
# First string is the name of the object (AND COLLECTION) in blender
# IMPORTANT, HAVE OBJECTS SEPARATED INTO COLLECTIONS OF THE SAME NAME SO THEY CAN BE EXCLUDED FOR PERFORMANCE
# Example in blender would be like this
#   z_plane
#       z_plane
# Second string in this list is whatever you want to call the file that will be exported
bakeList = [
    BakeObj('z_plane', 'z_plane'),
]


# DOESN'T DESELECT HIDDEN THINGS (or objects in excluded collections) FOR SOME REASON
def deselect():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    # bpy.ops.object.select_all(action='DESELECT')


deselect()


vl_collections = bpy.context.scene.view_layers["ViewLayer"].layer_collection


def set_collection_exclude(p_collection, name, exclude):
    for collection in p_collection.children:
        if collection.name.lower() == name.lower():
            print(f"COLLECTION FOUND| {name} |COLLECTION FOUND, setting exclude to {exclude}")
            collection.exclude = exclude
        elif collection.children:
            set_collection_exclude(collection, name, exclude)


def baker(objectNames, fileName):
    deselect()
    # Make sure the object is in viewport to bake
    for name in objectNames:
        set_collection_exclude(vl_collections, name, False)
        bpy.data.objects[name].select_set(True)

    bpy.ops.wm.alembic_export(
        filepath=path + fileName + ".abc",
        selected=True,
        start=startFrame,
        end=endFrame,
        global_scale=100,
        evaluation_mode="VIEWPORT",
        apply_subdiv=True,
    )

    # Clean up after yourself
    for name in objectNames:
        bpy.data.objects[name].select_set(False)
        set_collection_exclude(vl_collections, name, True)


# first hide all collections to be baked
for bake in bakeList:
    set_collection_exclude(vl_collections, bake.objName, True)

# export each alembic
for bake in bakeList:
    baker([bake.objName], bake.fileName)

# show all collections that were baked
for bake in bakeList:
    set_collection_exclude(vl_collections, bake.objName, False)


deselect()
