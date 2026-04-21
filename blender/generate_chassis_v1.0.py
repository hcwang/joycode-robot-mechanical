# MD-003 万向轮底盘 V1.0 - Blender 生成脚本
# 匠心 (结构工程师) - 2026-04-20
# 尺寸：直径 150mm，高度 50mm
# 万向轮：40mm 万向轮 x3，120 度均布
# 电机：N20 减速电机 x3

import bpy
import math
import bmesh

# 清除默认场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ==================== 参数定义 ====================
CHASSIS_DIAMETER = 150.0
CHASSIS_HEIGHT = 50.0
CHASSIS_THICKNESS = 4.0

SHELL_LENGTH = 95.0
SHELL_WIDTH = 75.0
SHELL_MOUNT_OFFSET = 5.0

WHEEL_MOUNT_RADIUS = 60.0
WHEEL_COUNT = 3

MOTOR_WIDTH = 12.0
MOTOR_SHAFT_DIAMETER = 3.0
MOTOR_MOUNT_HOLE_SPACING = 10.0
MOTOR_MOUNT_HOLE_RADIUS = 1.25

BATTERY_LENGTH = 65.0
BATTERY_WIDTH = 45.0
BATTERY_HEIGHT = 25.0
BATTERY_CLIP_WIDTH = 5.0
BATTERY_CLIP_HEIGHT = 8.0

CENTER_X = CHASSIS_DIAMETER / 2
CENTER_Y = CHASSIS_DIAMETER / 2
CENTER_Z = CHASSIS_HEIGHT / 2

DARK_GRAY = (0.2, 0.2, 0.2, 1.0)

def create_cylinder_mesh(location, radius, depth, vertices=32):
    """创建圆柱体网格对象"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        location=location,
        vertices=vertices
    )
    return bpy.context.active_object

def create_box_mesh(location, scale):
    """创建长方体网格对象"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = scale
    return obj

def apply_boolean_difference(target, cutter, modifier_name):
    """应用布尔差集运算"""
    mod = target.modifiers.new(name=modifier_name, type='BOOLEAN')
    mod.object = cutter
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=modifier_name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def join_objects(target, source):
    """将源对象合并到目标对象"""
    bpy.context.view_layer.objects.active = target
    source.select_set(True)
    target.select_set(True)
    bpy.ops.object.join()

# ==================== 创建底盘主体 ====================
chassis = create_cylinder_mesh(
    location=(CENTER_X, CENTER_Y, CENTER_Z),
    radius=CHASSIS_DIAMETER / 2,
    depth=CHASSIS_HEIGHT,
    vertices=64
)
chassis.name = "Chassis_Base"

# ==================== 创建外壳安装平台 ====================
platform = create_box_mesh(
    location=(CENTER_X, CENTER_Y, CHASSIS_HEIGHT - 2.5),
    scale=((SHELL_LENGTH / 2 + SHELL_MOUNT_OFFSET), 
           (SHELL_WIDTH / 2 + SHELL_MOUNT_OFFSET), 
           5.0)
)
platform.name = "Shell_Mount_Platform"
join_objects(chassis, platform)

# ==================== 创建外壳安装孔 ====================
SHELL_MOUNT_HOLES = [
    (CENTER_X - SHELL_LENGTH/2 + 8.5, CENTER_Y - SHELL_WIDTH/2 + 8.5),
    (CENTER_X + SHELL_LENGTH/2 - 8.5, CENTER_Y - SHELL_WIDTH/2 + 8.5),
    (CENTER_X - SHELL_LENGTH/2 + 8.5, CENTER_Y + SHELL_WIDTH/2 - 8.5),
    (CENTER_X + SHELL_LENGTH/2 - 8.5, CENTER_Y + SHELL_WIDTH/2 - 8.5),
]
MOUNT_HOLE_RADIUS = 1.75

for i, (x, y) in enumerate(SHELL_MOUNT_HOLES):
    hole = create_cylinder_mesh(
        location=(x, y, CENTER_Z),
        radius=MOUNT_HOLE_RADIUS,
        depth=CHASSIS_HEIGHT + 1
    )
    apply_boolean_difference(chassis, hole, f"Shell_Hole_{i+1}")

# ==================== 创建万向轮安装位 ====================
for i in range(WHEEL_COUNT):
    angle = math.radians(i * 120)
    wheel_x = CENTER_X + WHEEL_MOUNT_RADIUS * math.cos(angle)
    wheel_y = CENTER_Y + WHEEL_MOUNT_RADIUS * math.sin(angle)
    
    # 创建万向轮安装座
    wheel_mount = create_cylinder_mesh(
        location=(wheel_x, wheel_y, 7.5),
        radius=12.0,
        depth=15.0
    )
    join_objects(chassis, wheel_mount)
    
    # 创建电机安装孔
    motor_hole_x = wheel_x + 8.0 * math.cos(angle)
    motor_hole_y = wheel_y + 8.0 * math.sin(angle)
    
    motor_hole = create_cylinder_mesh(
        location=(motor_hole_x, motor_hole_y, 6.0),
        radius=MOTOR_WIDTH / 2 + 0.5,
        depth=12.0
    )
    apply_boolean_difference(chassis, motor_hole, f"Motor_Hole_{i+1}")
    
    # 创建电机固定螺丝孔 x2
    for j in range(2):
        hole_offset = (j - 0.5) * MOTOR_MOUNT_HOLE_SPACING
        screw_x = motor_hole_x + hole_offset * math.sin(angle)
        screw_y = motor_hole_y - hole_offset * math.cos(angle)
        
        screw_hole = create_cylinder_mesh(
            location=(screw_x, screw_y, CHASSIS_THICKNESS / 2),
            radius=MOTOR_MOUNT_HOLE_RADIUS,
            depth=CHASSIS_THICKNESS + 0.5
        )
        apply_boolean_difference(chassis, screw_hole, f"Motor_Screw_{i+1}_{j+1}")
    
    # 创建轮轴孔
    axle_hole = create_cylinder_mesh(
        location=(wheel_x, wheel_y, 7.5),
        radius=MOTOR_SHAFT_DIAMETER / 2 + 0.1,
        depth=25.0
    )
    axle_hole.rotation_euler = (0, math.radians(90), 0)
    apply_boolean_difference(chassis, axle_hole, f"Wheel_Axle_{i+1}")

# ==================== 创建电池仓 ====================
battery_x = CENTER_X
battery_y = CENTER_Y - 15.0
battery_z = CHASSIS_THICKNESS + BATTERY_HEIGHT / 2

battery_cavity = create_box_mesh(
    location=(battery_x, battery_y, battery_z - 2.0),
    scale=(BATTERY_LENGTH / 2, BATTERY_WIDTH / 2, BATTERY_HEIGHT / 2)
)
battery_cavity.name = "Battery_Cavity"
apply_boolean_difference(chassis, battery_cavity, "Battery_Cavity")

# 创建电池仓卡扣
clip_positions = [
    (battery_x - BATTERY_LENGTH/2 + 5.0, battery_y - BATTERY_WIDTH/2 + 5.0),
    (battery_x + BATTERY_LENGTH/2 - 5.0, battery_y - BATTERY_WIDTH/2 + 5.0),
    (battery_x - BATTERY_LENGTH/2 + 5.0, battery_y + BATTERY_WIDTH/2 - 5.0),
    (battery_x + BATTERY_LENGTH/2 - 5.0, battery_y + BATTERY_WIDTH/2 - 5.0),
]

for i, (cx, cy) in enumerate(clip_positions):
    clip = create_box_mesh(
        location=(cx, cy, battery_z + BATTERY_CLIP_HEIGHT / 2),
        scale=(BATTERY_CLIP_WIDTH / 2, BATTERY_CLIP_WIDTH / 2, BATTERY_CLIP_HEIGHT / 2)
    )
    join_objects(chassis, clip)

# ==================== 创建减重孔 ====================
for i in range(6):
    angle = math.radians(i * 60 + 30)
    hole_radius = 45.0
    hole_x = CENTER_X + hole_radius * math.cos(angle)
    hole_y = CENTER_Y + hole_radius * math.sin(angle)
    
    weight_hole = create_cylinder_mesh(
        location=(hole_x, hole_y, CHASSIS_THICKNESS / 2),
        radius=8.0,
        depth=CHASSIS_THICKNESS + 0.5
    )
    apply_boolean_difference(chassis, weight_hole, f"Weight_Reduction_{i+1}")

# ==================== 添加倒角 ====================
bpy.context.view_layer.objects.active = chassis
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT')

bevel_mod = chassis.modifiers.new(name="Edge_Bevel", type='BEVEL')
bevel_mod.width = 1.0
bevel_mod.segments = 3
bevel_mod.limit_method = 'ANGLE'
bevel_mod.angle_limit = math.radians(30)
bpy.ops.object.modifier_apply(modifier="Edge_Bevel")

# ==================== 设置材质 ====================
mat = bpy.data.materials.new(name="Dark_Gray")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = DARK_GRAY
bsdf.inputs["Roughness"].default_value = 0.5
bsdf.inputs["Metallic"].default_value = 0.2

if chassis.data.materials:
    chassis.data.materials[0] = mat
else:
    chassis.data.materials.append(mat)

# ==================== 设置渲染 ====================
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.eevee.taa_render_samples = 32
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.image_settings.file_format = 'PNG'

# 设置相机
bpy.ops.object.camera_add(
    location=(CENTER_X + 150, CENTER_Y - 150, CENTER_Z + 100)
)
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(45))
bpy.context.scene.camera = camera

# 设置灯光
bpy.ops.object.light_add(type='AREA', location=(CENTER_X + 100, CENTER_Y - 100, CENTER_Z + 150))
light1 = bpy.context.active_object
light1.data.energy = 500
light1.data.size = 50

bpy.ops.object.light_add(type='AREA', location=(CENTER_X - 100, CENTER_Y + 50, CENTER_Z + 100))
light2 = bpy.context.active_object
light2.data.energy = 300
light2.data.size = 30

# ==================== 输出文件 ====================
# 保存 Blender 文件
bpy.ops.wm.save_mainfile(filepath="/root/repos/joycode-robot-mechanical/blender/MD-003_Chassis_V1.0.blend")
print("Saved: MD-003_Chassis_V1.0.blend")

# 导出 STL - 确保选择底盘对象
bpy.ops.object.select_all(action='DESELECT')
chassis.select_set(True)
bpy.context.view_layer.objects.active = chassis

bpy.ops.export_mesh.stl(
    filepath="/root/repos/joycode-robot-mechanical/stl/MD-003_Chassis_V1.0.stl",
    use_selection=True
)
print("Exported: MD-003_Chassis_V1.0.stl")

# 渲染多视角图
camera_positions = [
    ("Isometric", (CENTER_X + 150, CENTER_Y - 150, CENTER_Z + 100), (math.radians(60), 0, math.radians(45))),
    ("Top_View", (CENTER_X, CENTER_Y, CENTER_Z + 200), (0, 0, 0)),
    ("Front_View", (CENTER_X, CENTER_Y - 200, CENTER_Z), (math.radians(90), 0, 0)),
    ("Side_View", (CENTER_X + 200, CENTER_Y, CENTER_Z), (math.radians(90), 0, math.radians(90))),
]

for view_name, cam_pos, cam_rot in camera_positions:
    camera.location = cam_pos
    camera.rotation_euler = cam_rot
    bpy.context.scene.render.filepath = f"/root/repos/joycode-robot-mechanical/renders/MD-003_Chassis_V1.0_{view_name}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: MD-003_Chassis_V1.0_{view_name}.png")

print("\n=== MD-003 万向轮底盘 V1.0 生成完成! ===")
