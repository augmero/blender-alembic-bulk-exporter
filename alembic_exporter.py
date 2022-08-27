import bpy

bl_info = {
    "name": "augmero - alembic exporter",
    "description": "batch exports alembics",
    "author": "augmero",
    "version": (0, 3),
    "blender": (3, 0, 0),
    "tracker_url": "https://augmero.github.io",
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
#   Alembic export doesn't like the rig and mesh parent/child relationship, clear parent and then add the armature back

# This script uses manual data entry, not very user friendly I know
# Important things to enter in:
# bakeList for all of the objects you want to bake and the filenames to export

# If the alembic animation doesn't look quite right and you're using constraints, there's some blender jank I ran into at one point that I don't think they are fixing https://developer.blender.org/T71986

# https://docs.blender.org/api/current/bpy.ops.wm.html?#bpy.ops.wm.alembic_export


scene = bpy.context.scene
# startFrame = scene.frame_start
# endFrame = scene.frame_end
# comment out or remove the above 3 lines and set start and end frame manually if you want
startFrame = 2
endFrame = 120
path = bpy.path.abspath("//")


class BakeObj:
    def __init__(self, in1, in2):
        self.obj_name = in1
        self.file_name = in2


# This is the important one to change
# First string is the name of the object (AND COLLECTION) in blender
# IMPORTANT, HAVE OBJECTS SEPARATED INTO COLLECTIONS OF THE SAME NAME SO THEY CAN BE EXCLUDED FOR PERFORMANCE
# Second string is whatever you want to call the file that will be exported
bakeList = [
    # BakeObj('z_bra', 'bra baked'),
    # BakeObj('z_bone', 'bone baked'),
    # BakeObj('z_tissue', 'tissue baked'),
    # BakeObj('z_hands', 'hands baked'),
    BakeObj('z_rhand', 'rhand baked'),
    # BakeObj('z_waist', 'waist baked'),
]


# DOESN'T DESELECT HIDDEN THINGS (or objects in excluded collections) FOR SOME REASON
def deselect():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


deselect()

vl_collections = bpy.context.scene.view_layers["ViewLayer"].layer_collection


def retrieve_layer_collection_BFS(layer_collection, collection_name):
    layers = [l for l in layer_collection.children]
    while len(layers) > 0:
        layer = layers.pop(0)
        if layer.name == collection_name:
            print(f'BFS FOUND {collection_name}\n')
            return layer
        if layer.children and len(layer.children) > 0:
            layers += layer.children
    print(f'BFS DID NOT FIND {collection_name}\n')
    return None


def bake_object(object_name, file_name):
    deselect()
    object = bpy.data.objects.get(object_name)
    if not object:
        print(f'Object {object_name} doesn\'t exist, this should never happen')
        return
    object.select_set(True)

    bpy.ops.wm.alembic_export(
        filepath=path + file_name + ".abc",
        selected=True,
        visible_objects_only=True,
        start=startFrame,
        end=endFrame,
        global_scale=100,
        evaluation_mode="VIEWPORT",
        apply_subdiv=True,
        export_hair=False,
        export_particles=False
    )

    # Clean up after yourself
    object.select_set(False)


layer_collections = {}

# find collections mentioned in bake list
for bake in bakeList:
    find_collection = retrieve_layer_collection_BFS(vl_collections, bake.obj_name)
    if find_collection:
        find_collection.exclude = False
        object = bpy.data.objects.get(bake.obj_name)
        if object:
            layer_collections[bake.obj_name] = find_collection
            find_collection.exclude = True
        else:
            print(f'Object {bake.obj_name} not found')

# bake valid objects
for bake in bakeList:
    collection = layer_collections.get(bake.obj_name)
    collection.exclude = False
    object = bpy.data.objects.get(bake.obj_name)
    if collection and object:
        bake_object(bake.obj_name, bake.file_name)
    collection.exclude = True

# include all collection in bake list
for collection in layer_collections.values():
    collection.exclude = False

deselect()
