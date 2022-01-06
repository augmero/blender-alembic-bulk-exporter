import bpy

bl_info = {
    "name": "augmero - alembic exporter",
    "description": "batch exports alembics",
    "author": "augmero",
    "version": (0, 2),
    "blender": (3, 0, 0),
    "tracker_url": "https://twitter.com/augmero_nsfw",
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
startFrame = 3
endFrame = 850
path = bpy.path.abspath("//")


# DOESN'T DESELECT HIDDEN THINGS (or objects in excluded collections) FOR SOME REASON
def deselect():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    # bpy.ops.object.select_all(action='DESELECT')


deselect()


def exclude_collection(pCollection, name):
    for collection in pCollection.children:
        if collection.name.lower() == name.lower():
            print("COLLECTION FOUND| " + name + " |COLLECTION FOUND, excluding")
            collection.exclude = True
        elif collection.children:
            exclude_collection(collection, name)


def include_collection(pCollection, name):
    for collection in pCollection.children:
        if collection.name.lower() == name.lower():
            print("COLLECTION FOUND| " + name + " |COLLECTION FOUND, including")
            collection.exclude = False
        elif collection.children:
            include_collection(collection, name)


vl_collections = bpy.context.scene.view_layers["View Layer"].layer_collection
# include_collection(vl_collections,"z_mercy ass")


def baker(objectNames, fileName):
    deselect()
    # Make sure the object is in viewport to bake
    for name in objectNames:
        include_collection(vl_collections, name)
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
        include_collection(vl_collections, name)


class BakeObj:
    def __init__(self, in1, in2):
        self.objName = in1
        self.fileName = in2


# This is the important one to change
# First string is the name of the object (AND COLLECTION) in blender
# IMPORTANT, HAVE OBJECTS SEPARATED INTO COLLECTIONS OF THE SAME NAME SO THEY CAN BE EXCLUDED FOR PERFORMANCE
# Second string is whatever you want to call the file that will be exported
bakeList = [
    #    BakeObj('dva_body zva', 'dva zva baked'),
    #    BakeObj('dva_body zRestShape', 'dva zRestShape'),
    BakeObj("z_dva arms", "dva arms baked"),
    BakeObj("z_mercy torso", "mercy torso alembic"),
    BakeObj("z_mercy belly", "mercy belly alembic"),
    BakeObj("z_dva lower collider", "dva lower collider baked"),
    BakeObj("z_mercy ass", "mercy ass baked"),
    #    BakeObj('mercy torso zRestShape', 'mercy torso zRestShape'),
]

# first hide all collections to be baked
for bake in bakeList:
    exclude_collection(vl_collections, bake.objName)

for bake in bakeList:
    baker([bake.objName], bake.fileName)

# show all collections that were baked
for bake in bakeList:
    include_collection(vl_collections, bake.objName)


deselect()

