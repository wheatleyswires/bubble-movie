import math
import bpy
import mathutils

from random import random

# ---------------------------
# -- BUBBLE SORT ALGORITHM --
# ---------------------------

def bubble_sort(elements, sequence):
    """
    Sorts elements ascending, and records the sequence of comparisons and swaps.
    """
    do_repeat = True
    while do_repeat:
        do_repeat = False # Assume this is the last sweep
        for i in range(len(elements)-1):
            swap = elements[i] > elements[i+1]
            sequence.append((i, i+1, swap))
            if swap:
                a = elements[i]
                elements[i] = elements[i+1]
                elements[i+1] = a
                do_repeat = True # Needs at least one more sweep


# --------------------
# -- INITIALIZATION --
# --------------------

# Clear up the scene by removing the blocks before regenerating them.
for obj in bpy.context.scene.collection.objects:
    if obj.name.startswith("block-"):
        bpy.data.objects.remove(obj, do_unlink=True)
        
# Initialize the progress label
progress_label = bpy.context.scene.collection.objects.get("progress-label")
if progress_label is not None:
    bpy.data.objects.remove(progress_label, do_unlink=True)
bpy.app.handlers.frame_change_post.clear()
                
# Generate random size for NUM_BLOCKS, between MIN_SIZE and MAX_SIZE                
NUM_BLOCKS = 10                
MIN_SIZE = 1.0
MAX_SIZE = 8.0

# sizes = [ MIN_SIZE + random()*(MAX_SIZE - MIN_SIZE) for i in range(NUM_BLOCKS) ]
sizes = [ 5.27, 6.56, 7.39, 3.75, 1.72, 4.69, 1.98, 7.77, 4.8, 6.76 ]

print(sizes)

# Block coloring (RGBA)
NORMAL_COL = (1, 1, 1, 1) # white
CMP_COL = (1, .7, .2, 1)  # gold
MOVE_COL = (1, 0, 0, 1)   # red


def create_mat(name, rgba=NORMAL_COL):
    """
    Generates a material with difuse color, with the initial RGBA
    """
    mat = bpy.data.materials.get(name)
    if mat is not None:
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.new(type='ShaderNodeOutputMaterial')
    shader = nodes.new(type='ShaderNodeBsdfDiffuse')
    nodes["Principled BSDF"].inputs[0].default_value = rgba
    links.new(shader.outputs[0], output.inputs[0])
    return mat
    
    
# This array will hold all generated blocks
blocks = []

for i in range(NUM_BLOCKS):
    height = sizes[i]
    # Create a rectangular mesh
    verts = [ (-1, -1, 0), (-1, 1, 0), (1, 1, 0), (1, -1, 0),
              (-1, -1, height), (-1, 1, height), (1, 1, height), (1, -1, height) ]
    faces = [ (0, 1, 2, 3), (0, 1, 5, 4), (5, 6, 2, 1), 
              (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7) ]
    mesh = bpy.data.meshes.new("block-mesh-" + str(i))
    mesh.from_pydata(verts, [], faces)
    # Create block object from the mesh
    block = bpy.data.objects.new("block-" + str(i), mesh)
    block.location += mathutils.Vector((0, 3*i, 0))
    # Color the bloc
    mat = create_mat("block-mat-" + str(i))
    block.data.materials.append(mat)
    # Record and show block on the scene
    blocks.append(block)
    bpy.context.scene.collection.objects.link(block)

# Create the progress label
bpy.ops.object.text_add(location=(4, 0, 0.1), rotation=(0,0,math.pi/2))
progress_label = bpy.context.object
progress_label.select_set(False)
progress_label.name = "progress-label"
progress_label.data.body = ""
progress_label_mat = create_mat("progress-label-mat", (0,0,0,1))
progress_label.data.materials.append(progress_label_mat )
progress_label_timeline = []


# Materials for rendering animation
master_normal_mat = create_mat("master-normal-mat", NORMAL_COL)
master_cmp_mat    = create_mat("master-cmp-mat", CMP_COL)
master_move_mat   = create_mat("master-move-mat", MOVE_COL)

# List of colors
block_color_timeline = []
for block in blocks:
    block_color_timeline.append((0, block, NORMAL_COL, master_normal_mat))



# ---------------
# -- ANIMATION --
# ---------------
   
# Skip this many frames before starting to move
frame_num = 25


def block_keyframe_insert(block):
    """
    Records block's location and color for the current frame.
    """
    block.keyframe_insert(data_path = "location", index = -1)
    block.data.materials[0].keyframe_insert(data_path="diffuse_color", index=-1)
    
    
def block_change_color(block, rgba, render_mat):
    """
    Changes block's color.
    """
    block.data.materials[0].diffuse_color = rgba
    block_color_timeline.append((frame_num, block, rgba, render_mat))

 
# Record the starting situation of all blocks (at frame 0)
bpy.context.scene.frame_set(0)
for block in blocks:
    block_keyframe_insert(block)
    

# Sort sizes and record the sequence of all comparisons and switches
sequence = []
bubble_sort(sizes, sequence)


# Animate the sequence of comparisons and swaps
num_steps = len(sequence)

print("Sequence length is %d" % (num_steps,))


for step in range(num_steps):
    (i1, i2, swap) = sequence[step]
    
    # The two compared blocks
    b1 = blocks[i1]
    b2 = blocks[i2]
    # Record positions and colors at the current frame
    bpy.context.scene.frame_set(frame_num)
    block_keyframe_insert(b1)
    block_keyframe_insert(b2)
    # Update the progress label
    progress_label_timeline.append((frame_num+1, 
        "%d/%d (%d%%)" % (step+1, num_steps, int(100*(step+1)/num_steps))))  

    if swap:
        # Swap the blocks in the blocks array
        blocks[i1] = b2
        blocks[i2] = b1

        # Compute the three-stages movement to swap the two blocks
        #
        #  Stage 1:            Stage 2:           Stage 3:
        #
        #   b1         b2       *<--------b2       b2           *
        #    |                                                  ^
        #    |                                                  |
        #    v                                                  |
        #    *                  b1-------->*                   b1
        #
        loc1 = b1.location
        loc2 = b2.location    
        t1 = [ (loc1.x+2, loc1.y, loc1.z), (loc1.x+2, loc2.y, loc1.z), (loc2.x, loc2.y, loc2.z) ]
        t2 = [ (loc2.x, loc2.y, loc2.z), (loc2.x, loc1.y, loc2.z), (loc1.x, loc1.y, loc1.z) ]

        # Time for stage 1 swap movement
        frame_num += 5
        bpy.context.scene.frame_set(frame_num)

        # Color the two blocks and move to the stage 1 point in the swap movement       
        block_change_color(b1, MOVE_COL, master_move_mat)        
        block_change_color(b2, CMP_COL, master_cmp_mat)
        b1.location = mathutils.Vector(t1[0])
        b2.location = mathutils.Vector(t2[0])
        block_keyframe_insert(b1)
        block_keyframe_insert(b2)
        
        # Time for stage 2 swap movement
        frame_num += 5
        bpy.context.scene.frame_set(frame_num)
        
        # Proceed to stage 2 point
        b1.location = mathutils.Vector(t1[1])        
        b2.location = mathutils.Vector(t2[1])
        block_keyframe_insert(b1)
        block_keyframe_insert(b2)
        
        # Time for stage 3 swap movement
        frame_num += 5
        bpy.context.scene.frame_set(frame_num)

        # Proceed to stage 3 point
        b1.location = mathutils.Vector(t1[2])        
        b2.location = mathutils.Vector(t2[2])
        block_keyframe_insert(b1)
        block_keyframe_insert(b2)
            
        # Immediatelly afterwards, restore the color to normal
        frame_num += 1
        bpy.context.scene.frame_set(frame_num)
        block_change_color(b1, NORMAL_COL, master_normal_mat)
        block_change_color(b2, NORMAL_COL, master_normal_mat)
        block_keyframe_insert(b1)
        block_keyframe_insert(b2)

        # Give some time before the next step in the sequence
        # to avoid jittery moves if the same block continues moving.
        frame_num += 4
        
    else: # not swapping
        
        # Recolor nodes for a short time
        frame_num += 3
        bpy.context.scene.frame_set(frame_num)

        block_change_color(b1, CMP_COL, master_cmp_mat)
        block_change_color(b2, CMP_COL, master_cmp_mat)
        block_keyframe_insert(b1)
        block_keyframe_insert(b2)

        # Then restore the normal coloring
        frame_num += 3
        bpy.context.scene.frame_set(frame_num)
        
        block_change_color(b1, NORMAL_COL, master_normal_mat)
        block_change_color(b2, NORMAL_COL, master_normal_mat)
        block_keyframe_insert(b1)
        block_keyframe_insert(b2)
        
    # end of the animation loop body

# Reset colors for all blocks
for block in blocks:
    block.data.materials[0].diffuse_color  = NORMAL_COL
    block.active_material = master_normal_mat

# Update progress label text from the timeline
def update_progress_label(self):
    """
    Update progress label based on the frame.
    """
    frame_no = bpy.context.scene.frame_current
    current_label = ""
    for (label_frame, label) in progress_label_timeline:
        if label_frame > frame_no: break
        current_label = label
    progress_label.data.body = current_label
    # Update block colors
    bcd = {}
    for (change_frame, block, rgba, render_mat) in block_color_timeline:
        if change_frame <= frame_no:
            bcd[block.name] = (block, render_mat)
    for block_name in bcd:
        (block, render_mat) = bcd[block_name]
        block.active_material = render_mat

bpy.app.handlers.frame_change_post.append(update_progress_label)

# Go back to the start frame
bpy.context.scene.frame_set(0)

