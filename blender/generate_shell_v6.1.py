# MD-001 外壳 V6.1 - Blender 生成脚本 (更新版)
# 匠心 (结构工程师) - 2026-04-17
# 配色方案：科技蓝 #0066CC
# 更新：修复 STL 导出，调整安装孔位基于 board_dimensions.md

import bpy
import math

# 清除默认场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ==================== 参数定义 ====================
# 外壳尺寸 (mm)
SHELL_LENGTH = 95.0    # 长度 (主板 85mm + 间隙)
SHELL_WIDTH = 75.0     # 宽度 (主板 65mm + 间隙)
SHELL_HEIGHT = 25.0    # 高度
WALL_THICKNESS = 2.5   # 壁厚
BOTTOM_THICKNESS = 2.0 # 底厚

# 主板安装孔位置 (基于 board_dimensions.md V1.2)
# 主板尺寸：85×65mm，安装孔距边 3.5mm
# 外壳内腔：85×65mm (留出 1mm 间隙)
# 安装孔位置计算：外壳边距 5mm + 主板孔位
MOUNT_HOLES = [
    (8.5, 8.5),      # H1 - 左下角 (5mm 边距 + 3.5mm 孔位)
    (86.5, 8.5),     # H2 - 右下角 (5mm 边距 + 81.5mm 孔位)
    (8.5, 66.5),     # H3 - 左上角 (5mm 边距 + 61.5mm 孔位)
    (86.5, 66.5),    # H4 - 右上角
]
MOUNT_HOLE_RADIUS = 1.75  # M2.5 螺丝孔半径

# 接口开孔位置 (V6.1 更新 - 根据主板实际位置调整)
USB_C_POS = (47.5, 1.5, 8.0)      # 底部中央 (主板 85/2=42.5 + 5mm 边距)
USB_C_SIZE = (9.0, 2.0, 3.0)

POWER_POS = (93.5, 37.5, 10.0)    # 右侧 (主板 65/2=32.5 + 5mm 边距)
POWER_SIZE = (2.0, 5.5, 2.5)

SPEAKER_POS = (47.5, 73.5, 20.0)  # 顶部
SPEAKER_RADIUS = 3.0

# 科技蓝颜色
TECH_BLUE = (0.0, 0.4, 0.8, 1.0)  # #0066CC 归一化

# ==================== 创建外壳主体 ====================
# 创建外盒
bpy.ops.mesh.primitive_cube_add(size=1, location=(SHELL_LENGTH/2, SHELL_WIDTH/2, SHELL_HEIGHT/2))
outer_box = bpy.context.active_object
outer_box.name = "Shell_Outer"
outer_box.scale = (SHELL_LENGTH/2, SHELL_WIDTH/2, SHELL_HEIGHT/2)

# 创建内腔 (布尔减运算)
inner_length = SHELL_LENGTH - 2 * WALL_THICKNESS
inner_width = SHELL_WIDTH - 2 * WALL_THICKNESS
inner_height = SHELL_HEIGHT - BOTTOM_THICKNESS
bpy.ops.mesh.primitive_cube_add(size=1, location=(SHELL_LENGTH/2, SHELL_WIDTH/2, inner_height/2 + BOTTOM_THICKNESS))
inner_box = bpy.context.active_object
inner_box.name = "Shell_Inner_Cutter"
inner_box.scale = (inner_length/2, inner_width/2, inner_height/2)

# 布尔修改器 - 创建空腔
bool_mod = outer_box.modifiers.new(name="Cavity", type='BOOLEAN')
bool_mod.object = inner_box
bool_mod.operation = 'DIFFERENCE'

# 应用布尔修改器
bpy.context.view_layer.objects.active = outer_box
bpy.ops.object.modifier_apply(modifier="Cavity")

# 删除内腔对象
bpy.data.objects.remove(inner_box, do_unlink=True)

# ==================== 创建安装柱和螺丝孔 ====================
for i, (x, y) in enumerate(MOUNT_HOLES):
    # 安装柱
    bpy.ops.mesh.primitive_cylinder_add(radius=4.0, depth=SHELL_HEIGHT - BOTTOM_THICKNESS, 
                                         location=(x, y, SHELL_HEIGHT/2))
    mount_post = bpy.context.active_object
    mount_post.name = f"Mount_Post_{i+1}"
    
    # 将安装柱合并到外壳
    bpy.context.view_layer.objects.active = outer_box
    mount_post.select_set(True)
    outer_box.select_set(True)
    bpy.ops.object.join()
    
    # 创建螺丝孔
    bpy.ops.mesh.primitive_cylinder_add(radius=MOUNT_HOLE_RADIUS, depth=SHELL_HEIGHT,
                                         location=(x, y, SHELL_HEIGHT/2))
    hole = bpy.context.active_object
    hole.name = f"Mount_Hole_{i+1}"
    
    # 布尔减运算创建孔
    bool_mod = outer_box.modifiers.new(name=f"Hole_{i+1}", type='BOOLEAN')
    bool_mod.object = hole
    bool_mod.operation = 'DIFFERENCE'
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    # 删除孔对象
    bpy.data.objects.remove(hole, do_unlink=True)

# ==================== 创建接口开孔 (V6.1 调整位置) ====================
# USB-C 开孔
bpy.ops.mesh.primitive_cube_add(size=1, location=USB_C_POS)
usb_hole = bpy.context.active_object
usb_hole.name = "USB_C_Hole"
usb_hole.scale = (USB_C_SIZE[0]/2, USB_C_SIZE[1]/2, USB_C_SIZE[2]/2)

bool_mod = outer_box.modifiers.new(name="USB_C_Hole", type='BOOLEAN')
bool_mod.object = usb_hole
bool_mod.operation = 'DIFFERENCE'
bpy.ops.object.modifier_apply(modifier="USB_C_Hole")
bpy.data.objects.remove(usb_hole, do_unlink=True)

# 电源接口开孔
bpy.ops.mesh.primitive_cube_add(size=1, location=POWER_POS)
power_hole = bpy.context.active_object
power_hole.name = "Power_Hole"
power_hole.scale = (POWER_SIZE[0]/2, POWER_SIZE[1]/2, POWER_SIZE[2]/2)

bool_mod = outer_box.modifiers.new(name="Power_Hole", type='BOOLEAN')
bool_mod.object = power_hole
bool_mod.operation = 'DIFFERENCE'
bpy.ops.object.modifier_apply(modifier="Power_Hole")
bpy.data.objects.remove(power_hole, do_unlink=True)

# 扬声器开孔
bpy.ops.mesh.primitive_cylinder_add(radius=SPEAKER_RADIUS, depth=WALL_THICKNESS,
                                     location=SPEAKER_POS)
speaker_hole = bpy.context.active_object
speaker_hole.name = "Speaker_Hole"

bool_mod = outer_box.modifiers.new(name="Speaker_Hole", type='BOOLEAN')
bool_mod.object = speaker_hole
bool_mod.operation = 'DIFFERENCE'
bpy.ops.object.modifier_apply(modifier="Speaker_Hole")
bpy.data.objects.remove(speaker_hole, do_unlink=True)

# ==================== 设置材质 - 科技蓝 ====================
mat = bpy.data.materials.new(name="Tech_Blue")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = TECH_BLUE
bsdf.inputs["Roughness"].default_value = 0.3
bsdf.inputs["Metallic"].default_value = 0.1

if outer_box.data.materials:
    outer_box.data.materials[0] = mat
else:
    outer_box.data.materials.append(mat)

# ==================== 设置渲染 ====================
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.image_settings.file_format = 'PNG'

# 设置相机
bpy.ops.object.camera_add(location=(SHELL_LENGTH, -SHELL_WIDTH*1.5, SHELL_HEIGHT*1.2))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(15))
bpy.context.scene.camera = camera

# 设置灯光
bpy.ops.object.light_add(type='AREA', location=(SHELL_LENGTH/2, -SHELL_WIDTH, SHELL_HEIGHT*2))
light1 = bpy.context.active_object
light1.data.energy = 500
light1.data.size = 50

bpy.ops.object.light_add(type='AREA', location=(-SHELL_LENGTH/2, SHELL_WIDTH*0.5, SHELL_HEIGHT*1.5))
light2 = bpy.context.active_object
light2.data.energy = 300
light2.data.size = 30

# ==================== 输出文件 ====================
# 保存 Blender 文件
bpy.ops.wm.save_mainfile(filepath="/root/repos/joycode-robot-mechanical/blender/MD-001_Shell_V6.1.blend")

# 确保对象有网格数据后再导出 STL
bpy.context.view_layer.objects.active = outer_box
bpy.ops.object.mode_set(mode='OBJECT')

# 导出 STL
bpy.ops.export_mesh.stl(filepath="/root/repos/joycode-robot-mechanical/stl/MD-001_Shell_V6.1.stl", 
                        use_selection=True)

# 渲染产品图
bpy.context.scene.render.filepath = "/root/repos/joycode-robot-mechanical/renders/MD-001_Shell_V6.1_Render.png"
bpy.ops.render.render(write_still=True)

print("MD-001 外壳 V6.1 生成完成!")
print(f"- Blender 文件：blender/MD-001_Shell_V6.1.blend")
print(f"- STL 文件：stl/MD-001_Shell_V6.1.stl")
print(f"- 渲染图：renders/MD-001_Shell_V6.1_Render.png")
