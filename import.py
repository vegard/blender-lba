# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
# Copyright (C) 2016  Vegard Nossum <vegard.nossum@gmail.com>

bl_info = {
    'name': 'LBA model importer',
    'author': 'Vegard Nossum <vegard.nossum@gmail.com>',
    'version': (0, 0, 1),
    'location': 'File > Import-Export',
    'description': 'Import Little Big Adventure 3D models and animations',
    'category': 'Import-Export',
}

import bpy
import bpy_extras.io_utils
import io
import math
import struct

class HQRReader(object):
    """
    Read compressed and uncompressed files from an LBA .HQR archive.
    """

    def __init__(self, path):
        self.path = path

    def __getitem__(self, index):
        with open(self.path, 'rb') as f:
            def u8():
                return struct.unpack('<B', f.read(1))[0]
            def u16():
                return struct.unpack('<H', f.read(2))[0]
            def u32():
                return struct.unpack('<I', f.read(4))[0]

            f.seek(4 * index)
            offset = u32()
            f.seek(offset)

            size_full = u32()
            size_compressed = u32()
            compression_type = u16()

            if compression_type == 0:
                # No compression
                return io.BytesIO(f.read(size_compressed))

            decompressed = bytearray()
            while True:
                flags = u8()
                for i in range(8):
                    if (flags >> i) & 1:
                        decompressed.append(u8())
                        if len(decompressed) == size_full:
                            return io.BytesIO(decompressed)
                    else:
                        header = u16()
                        offset = 1 + (header >> 4)
                        length = 1 + compression_type + (header & 15)

                        for i in range(length):
                            decompressed.append(decompressed[-offset])

                        if len(decompressed) >= size_full:
                            return io.BytesIO(decompressed[:size_full])

def read_lba_palette(f):
    def u8():
        return struct.unpack('<B', f.read(1))[0]

    colors = []
    for i in range(256):
        r = u8()
        g = u8()
        b = u8()

        colors.append((r, g, b))

    return colors

class LBABone(object):
    def __init__(self):
        pass

class LBAPolygon(object):
    def __init__(self):
        pass

class LBAModel(object):
    def __init__(self):
        pass

def read_lba_model(f):
    def skip(n):
        f.read(n)
    def u8():
        return struct.unpack('<B', f.read(1))[0]
    def u16():
        return struct.unpack('<H', f.read(2))[0]
    def u16_div(n):
        x = u16()
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x // n
    def s16_div(n):
        x = s16()
        if x == -1:
            return x
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x // n
    def s16():
        return struct.unpack('<h', f.read(2))[0]
    def u32():
        return struct.unpack('<I', f.read(4))[0]

    flags = u16()

    # unknown
    skip(2 * 12)

    vertices = []
    for i in range(u16()):
        x = s16()
        y = s16()
        z = s16()
        vertices.append((x, y, z))

    bones = []
    for i in range(u16()):
        bone = LBABone()
        bone.first_point = u16_div(6)
        bone.nr_points = u16()
        bone.parent_point = u16_div(6)
        bone.parent_bone = s16_div(38)
        bone.bone_type = u16()
        # unknown
        bone.z = s16()
        bone.y = s16()
        bone.x = s16()
        nr_normals = u16()
        skip(2)
        skip(4)
        skip(4)
        skip(4)
        skip(4)
        skip(2)

        bones.append(bone)

    normals = []
    for i in range(u16()):
        x = s16()
        y = s16()
        z = s16()
        # unknown
        w = s16()

        normals.append((x, y, z, w))

    polygons = []
    for i in range(u16()):
        render_type = u8()
        nr_vertices = u8()
        color_index = u8()
        # unknown
        skip(1)

        polygon_vertices = []

        if render_type >= 9:
            # each vertex has a normal
            for j in range(nr_vertices):
                normal = u16()
                v = u16_div(6)
                polygon_vertices.append((v, normal))
        elif render_type >= 7:
            # one normal for the whole polygon
            normal = u16()
            for j in range(nr_vertices):
                v = u16_div(6)
                polygon_vertices.append((v, normal))
        else:
            # no normal (?)
            for j in range(nr_vertices):
                v = u16_div(6)
                polygon_vertices.append((v, ))

        polygon = LBAPolygon()
        polygon.render_type = render_type
        polygon.color_index = color_index
        polygon.vertices = polygon_vertices
        polygons.append(polygon)

    lines = []
    for i in range(u16()):
        data = u32()
        v1 = u16_div(6)
        v2 = u16_div(6)

        lines.append((v1, v2))

    circles = []
    for i in range(u16()):
        # unknown
        skip(1)
        color = u8()
        # unknown
        skip(2)
        size = u16()
        v = u16_div(6)

        circles.append((v, color, size))

    lba_model = LBAModel()
    lba_model.vertices = vertices
    lba_model.bones = bones
    lba_model.normals = normals
    lba_model.polygons = polygons
    lba_model.lines = lines
    lba_model.circles = circles
    return lba_model

class LBAKeyFrame(object):
    def __init__(self):
        pass

class LBAAnimation(object):
    def __init__(self):
        pass

def read_lba_anim(f):
    def skip(n):
        f.read(n)
    def u8():
        return struct.unpack('<B', f.read(1))[0]
    def u16():
        return struct.unpack('<H', f.read(2))[0]
    def u16_div(n):
        x = u16()
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x / n
    def s16_div(n):
        x = s16()
        if x == -1:
            return x
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x // n
    def s16():
        return struct.unpack('<h', f.read(2))[0]
    def u32():
        return struct.unpack('<I', f.read(4))[0]

    nr_keyframes = u16()
    nr_bones = u16()
    loop_start = u16()
    # unknown
    _2 = u16()

    keyframes = []
    for i in range(nr_keyframes):
        delay = u16()
        # unknown
        _1 = s16()
        _2 = u16()
        _3 = s16()

        bones = []
        for j in range(nr_bones):
            flags = u16()
            x = 2 * math.pi * s16() / 0x400
            y = 2 * math.pi * s16() / 0x400
            z = 2 * math.pi * s16() / 0x400

            bones.append((flags, x, y, z))

        keyframe = LBAKeyFrame()
        keyframe.delay = delay
        keyframe.bones = bones
        keyframes.append(keyframe)

    lba_anim = LBAAnimation()
    lba_anim.keyframes = keyframes
    lba_anim.loop_start = loop_start
    return lba_anim

class LBABodyImporter(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import a Little Big Adventure (LBA) body"""

    bl_idname = 'object.lbabody'
    bl_label = 'Import LBA body'

    filename_ext = '.hqr'
    filter_glob = bpy.props.StringProperty(
        default='*.hqr;*.HQR',
        options={'HIDDEN'},
    )

    entry = bpy.props.IntProperty(
        name='Entry number',
        subtype='UNSIGNED',
    )

    def execute(self, context):
        scn = context.scene

        lba_model = read_lba_model(HQRReader(self.filepath)[self.entry])

        #
        # Create armature
        #

        amt = bpy.data.armatures.new('Armature')
        amt.show_names = True

        rig = bpy.data.objects.new('Rig', amt)
        rig.location = scn.cursor_location

        scn.objects.link(rig)
        scn.objects.active = rig
        scn.update()

        #bpy.ops.object.editmode_toggle()
        bpy.ops.object.mode_set(mode='EDIT')

        model_bones = {}
        for i, lba_bone in enumerate(lba_model.bones):
            bone = amt.edit_bones.new('Bone {}'.format(i))

            # Must give bone a non-zero length, otherwise it will be
            # invalid and disappear.
            bone.head = (0, 0, 0)
            bone.tail = (0, 1, 0)

            if lba_bone.parent_bone != -1:
                bone.parent = model_bones[lba_bone.parent_bone]

            model_bones[i] = bone

        bpy.ops.object.mode_set(mode='OBJECT')

        #
        # Create mesh
        #

        me = bpy.data.meshes.new('Mesh')
        ob = bpy.data.objects.new('Body', me)
        ob.location = scn.cursor_location

        scn.objects.link(ob)
        scn.objects.active = ob
        scn.update()

        me.from_pydata(lba_model.vertices, [], [tuple(y[0] for y in polygon.vertices) for polygon in lba_model.polygons])
        # XXX: calc_edges=True necessary?
        me.update(calc_edges=True)

        #
        # Assign materials (colours)
        #

        # NOTE: You have to actually load the LBA palette in a separate step
        # afterwards.
        for i, polygon in enumerate(lba_model.polygons):
            me.polygons[i].material_index = polygon.color_index

        #
        # Skin mesh (add vertices to bones)
        #

        # Create one vertex group per bone
        for i, lba_bone in enumerate(lba_model.bones):
            grp = ob.vertex_groups.new('Bone {}'.format(i))
            grp.add(list(range(lba_bone.first_point, lba_bone.first_point + lba_bone.nr_points)), 1.0, 'REPLACE')

        # Give mesh object an armature modifier, using vertex groups but
        # not envelopes
        mod = ob.modifiers.new('Armature modifier', 'ARMATURE')
        mod.object = rig
        mod.use_bone_envelopes = False
        mod.use_vertex_groups = True

        #
        # Move bones into place
        #

        scn.objects.active = rig
        bpy.ops.object.mode_set(mode='POSE')

        for i, lba_bone in enumerate(lba_model.bones):
            bone = rig.pose.bones['Bone {}'.format(i)]
            # TODO: which one is it? they look all the same to me.
            #bone.rotation_mode = 'XYZ'
            #bone.rotation_mode = 'XZY'
            #bone.rotation_mode = 'YXZ'
            #bone.rotation_mode = 'YZX'
            #bone.rotation_mode = 'ZXY'
            bone.rotation_mode = 'ZYX'

            if lba_bone.parent_bone != -1:
                parent = rig.pose.bones['Bone {}'.format(lba_bone.parent_bone)]

                x1, y1, z1 = lba_model.vertices[lba_bone.parent_point]
                bone.location = (x1, y1, z1)
                scn.update()

        scale = 1. / (1 << 7)
        rig.pose.bones['Bone 0'].scale = (scale, scale, scale)

        #
        # Done
        #

        scn.objects.active = ob
        bpy.ops.object.mode_set(mode='OBJECT')
        ob.select = True
        bpy.ops.object.shade_smooth()

        #bpy.ops.view3d.viewnumpad(type='TOP')
        #bpy.ops.view3d.view_persportho()
        return {'FINISHED'}

class LBAPaletteImporter(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import a Little Big Adventure (LBA) palette"""

    bl_idname = 'object.lbapalette'
    bl_label = 'Import LBA palette'

    filename_ext = '.hqr'
    filter_glob = bpy.props.StringProperty(
        default='*.hqr;*.HQR',
        options={'HIDDEN'},
    )

    entry = bpy.props.IntProperty(
        name='Entry number',
        subtype='UNSIGNED',
    )

    def execute(self, context):
        scn = context.scene
        ob = scn.objects.active
        me = ob.data

        lba_palette = read_lba_palette(HQRReader(self.filepath)[self.entry])
        for i, lba_color in enumerate(lba_palette):
            mat = bpy.data.materials.new('Color {}'.format(i))
            mat.diffuse_color = (lba_color[0] / 255., lba_color[1] / 255., lba_color[2] / 255.)
            me.materials.append(mat)

        return {'FINISHED'}

class LBAAnimationImporter(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import a Little Big Adventure (LBA) animation"""

    bl_idname = 'object.lbaanimation'
    bl_label = 'Import LBA animation'

    filename_ext = '.hqr'
    filter_glob = bpy.props.StringProperty(
        default='*.hqr;*.HQR',
        options={'HIDDEN'},
    )

    entry = bpy.props.IntProperty(
        name='Entry number',
        subtype='UNSIGNED',
    )

    def execute(self, context):
        scn = context.scene
        ob = scn.objects.active

        #
        # Create action (load animation)
        #

        lba_anim = read_lba_anim(HQRReader(self.filepath)[self.entry])

        ac = bpy.data.actions.new('Action')
        ob.animation_data_create()
        ob.animation_data.action = ac

        # Blender doesn't support per-action (per-animation) loops,
        # what a shame!
        scn.frame_start = sum(lba_keyframe.delay
            for lba_keyframe in lba_anim.keyframes[:lba_anim.loop_start])
        scn.frame_end = sum(lba_keyframe.delay
            for lba_keyframe in lba_anim.keyframes)

        #for i, bone in enumerate(ob.pose.bones):
        for i in range(len(ob.pose.bones)):
            bone = ob.pose.bones['Bone {}'.format(i)]
            data_path = bone.path_from_id('rotation_euler')

            # [x, y, z]
            for k in range(3):
                rot = ac.fcurves.new(data_path, index=k)
                prev_v = 0

                # We need to add the first frame of the loop to the end in
                # order to get a smooth transition back
                time = 0
                for j, lba_keyframe in enumerate(lba_anim.keyframes + [lba_anim.keyframes[lba_anim.loop_start]]):
                    new_v = lba_keyframe.bones[i][1 + k]
                    if lba_keyframe.bones[i][0] == 0:
                        diff_v = new_v - prev_v
                        if diff_v < -math.pi:
                            diff_v += 2 * math.pi
                        elif diff_v > math.pi:
                            diff_v -= 2 * math.pi
                        computed_v = prev_v + diff_v
                    elif lba_keyframe.bones[i][0] == 1:
                        computed_v = new_v

                    keyframe = rot.keyframe_points.insert(time, computed_v)
                    #keyframe.interpolation = 'CONSTANT'
                    keyframe.interpolation = 'LINEAR'

                    time += lba_keyframe.delay

                    prev_v = computed_v

        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.paths_calculate()

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(LBABodyImporter.bl_idname, text='LBA Body (.HQR)')
    self.layout.operator(LBAPaletteImporter.bl_idname, text='LBA Palette (.HQR)')
    self.layout.operator(LBAAnimationImporter.bl_idname, text='LBA Animation (.HQR)')

def register():
    bpy.utils.register_class(LBABodyImporter)
    bpy.utils.register_class(LBAPaletteImporter)
    bpy.utils.register_class(LBAAnimationImporter)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_class(LBABodyImporter)
    bpy.utils.unregister_class(LBAPaletteImporter)
    bpy.utils.unregister_class(LBAAnimationImporter)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == '__main__':
    register()
