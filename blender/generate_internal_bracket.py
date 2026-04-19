# 生成内部组件支架 - 电池支架 + 摄像头支架
import bpy
import math
from pathlib import Path

# 清理场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============== 电池支架设计 ==============
# 18650 电池尺寸：直径 18mm，长度 65mm
BATTERY_DIAMETER = 18.0
BATTERY_LENGTH = 65.0
WALL_THICKNESS = 2.0
CLIP_THICKNESS = 1.5

def create_battery_holder():
    """创建双 18650 电池支架"""
    
    # 电池间距（两个电池并排，留间隙）
    battery_spacing = BATTERY_DIAMETER + 5.0
    
    # 创建底座
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 0)
    )
    base = bpy.context.active_object
    base.name = "BatteryHolder_Base"
    base.scale = (
        BATTERY_LENGTH + WALL_THICKNESS * 2,
        battery_spacing * 2 + WALL_THICKNESS * 2,
        WALL_THICKNESS
    )
    
    # 创建左侧电池槽
    bpy.ops.mesh.primitive_cylinder_add(
        radius=(BATTERY_DIAMETER + WALL_THICKNESS) / 2,
        depth=BATTERY_LENGTH + WALL_THICKNESS,
        location=(0, -battery_spacing/2, (BATTERY_LENGTH + WALL_THICKNESS) / 2),
        rotation=(math.pi/2, 0, 0)
    )
    left_slot = bpy.context.active_object
    left_slot.name = "BatteryHolder_LeftSlot"
    
    # 创建右侧电池槽
    bpy.ops.mesh.primitive_cylinder_add(
        radius=(BATTERY_DIAMETER + WALL_THICKNESS) / 2,
        depth=BATTERY_LENGTH + WALL_THICKNESS,
        location=(0, battery_spacing/2, (BATTERY_LENGTH + WALL_THICKNESS) / 2),
        rotation=(math.pi/2, 0, 0)
    )
    right_slot = bpy.context.active_object
    right_slot.name = "BatteryHolder_RightSlot"
    
    # 使用布尔运算创建槽
    bpy.ops.object.select_all(action='DESELECT')
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    
    # 左侧槽布尔
    bpy.ops.object.modifier_add(type='BOOLEAN')
    base.modifiers["Boolean"].operation = 'UNION'
    base.modifiers["Boolean"].object = left_slot
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    # 删除临时对象
    bpy.data.objects.remove(left_slot, do_unlink=True)
    
    # 重新选择底座
    bpy.ops.object.select_all(action='DESELECT')
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    
    # 右侧槽布尔
    bpy.ops.object.modifier_add(type='BOOLEAN')
    base.modifiers["Boolean"].operation = 'UNION'
    base.modifiers["Boolean"].object = right_slot
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    bpy.data.objects.remove(right_slot, do_unlink=True)
    
    # 创建卡扣（4 个角）
    clip_positions = [
        (-BATTERY_LENGTH/2 - 2, -battery_spacing - 3, WALL_THICKNESS),
        (BATTERY_LENGTH/2 + 2, -battery_spacing - 3, WALL_THICKNESS),
        (-BATTERY_LENGTH/2 - 2, battery_spacing + 3, WALL_THICKNESS),
        (BATTERY_LENGTH/2 + 2, battery_spacing + 3, WALL_THICKNESS),
    ]
    
    for i, pos in enumerate(clip_positions):
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=pos
        )
        clip = bpy.context.active_object
        clip.name = f"BatteryHolder_Clip_{i+1}"
        clip.scale = (8, 4, 6)
        
        # 添加卡扣钩
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(pos[0], pos[1] + (2 if pos[1] < 0 else -2), pos[2] + 3)
        )
        hook = bpy.context.active_object
        hook.name = f"BatteryHolder_Hook_{i+1}"
        hook.scale = (8, 2, 3)
        
        # 合并卡扣和钩
        bpy.ops.object.select_all(action='DESELECT')
        clip.select_set(True)
        hook.select_set(True)
        bpy.context.view_layer.objects.active = clip
        bpy.ops.object.join()
    
    # 添加中间隔板
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, WALL_THICKNESS + BATTERY_LENGTH/2)
    )
    divider = bpy.context.active_object
    divider.name = "BatteryHolder_Divider"
    divider.scale = (BATTERY_LENGTH + WALL_THICKNESS * 2, WALL_THICKNESS, BATTERY_LENGTH)
    divider.rotation_euler = (math.pi/2, 0, 0)
    
    # 合并所有部件
    bpy.ops.object.select_all(action='DESELECT')
    base.select_set(True)
    for obj in bpy.data.objects:
        if "BatteryHolder" in obj.name and obj != base:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    base.name = "BatteryHolder"
    return base

# ============== 摄像头支架设计 ==============
def create_camera_mount():
    """创建可调节角度的摄像头支架"""
    
    # 底座
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 0)
    )
    cam_base = bpy.context.active_object
    cam_base.name = "CameraMount_Base"
    cam_base.scale = (40, 30, 3)
    
    # 铰链座（左右各一个）
    hinge_positions = [(-15, 0, 3), (15, 0, 3)]
    hinges = []
    
    for i, pos in enumerate(hinge_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=4,
            depth=6,
            location=pos,
            rotation=(math.pi/2, 0, 0)
        )
        hinge = bpy.context.active_object
        hinge.name = f"CameraMount_Hinge_{i+1}"
        hinges.append(hinge)
        
        # 添加 M2 螺丝孔
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.1,  # M2 螺丝孔径
            depth=10,
            location=(pos[0], pos[1], pos[2] + 3),
            rotation=(math.pi/2, 0, 0)
        )
        screw_hole = bpy.context.active_object
        screw_hole.name = f"CameraMount_ScrewHole_{i+1}"
        
        # 布尔减除螺丝孔
        bpy.ops.object.select_all(action='DESELECT')
        hinge.select_set(True)
        bpy.context.view_layer.objects.active = hinge
        bpy.ops.object.modifier_add(type='BOOLEAN')
        hinge.modifiers["Boolean"].operation = 'DIFFERENCE'
        hinge.modifiers["Boolean"].object = screw_hole
        bpy.ops.object.modifier_apply(modifier="Boolean")
        bpy.data.objects.remove(screw_hole, do_unlink=True)
    
    # 合并底座和铰链座
    bpy.ops.object.select_all(action='DESELECT')
    cam_base.select_set(True)
    for h in hinges:
        h.select_set(True)
    bpy.context.view_layer.objects.active = cam_base
    bpy.ops.object.join()
    cam_base.name = "CameraMount_Base"
    
    # 创建可旋转的摄像头平台
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 15)
    )
    cam_platform = bpy.context.active_object
    cam_platform.name = "CameraMount_Platform"
    cam_platform.scale = (35, 25, 4)
    
    # 添加铰链轴
    bpy.ops.mesh.primitive_cylinder_add(
        radius=3,
        depth=35,
        location=(0, 0, 15),
        rotation=(math.pi/2, 0, 0)
    )
    axle = bpy.context.active_object
    axle.name = "CameraMount_Axle"
    
    # 合并平台和轴
    bpy.ops.object.select_all(action='DESELECT')
    cam_platform.select_set(True)
    axle.select_set(True)
    bpy.context.view_layer.objects.active = cam_platform
    bpy.ops.object.join()
    cam_platform.name = "CameraMount_Platform"
    
    # 添加摄像头安装孔（4 个 M2 孔）
    cam_mount_holes = [
        (-12, -8, 2),
        (12, -8, 2),
        (-12, 8, 2),
        (12, 8, 2)
    ]
    
    for i, pos in enumerate(cam_mount_holes):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.1,
            depth=10,
            location=(pos[0], pos[1], 15 + pos[2])
        )
        hole = bpy.context.active_object
        hole.name = f"CamMount_Hole_{i+1}"
        
        # 布尔减除
        bpy.ops.object.select_all(action='DESELECT')
        cam_platform.select_set(True)
        bpy.context.view_layer.objects.active = cam_platform
        bpy.ops.object.modifier_add(type='BOOLEAN')
        cam_platform.modifiers["Boolean"].operation = 'DIFFERENCE'
        cam_platform.modifiers["Boolean"].object = hole
        bpy.ops.object.modifier_apply(modifier="Boolean")
        bpy.data.objects.remove(hole, do_unlink=True)
    
    # 添加角度调节限位（±15°）
    # 创建限位块
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, -18, 10)
    )
    stopper = bpy.context.active_object
    stopper.name = "CameraMount_Stopper"
    stopper.scale = (20, 5, 8)
    
    # 合并到底座
    bpy.ops.object.select_all(action='DESELECT')
    cam_base.select_set(True)
    stopper.select_set(True)
    bpy.context.view_layer.objects.active = cam_base
    bpy.ops.object.join()
    
    return cam_base, cam_platform

# ============== 创建 18650 电池模型（用于渲染） ==============
def create_battery_model():
    """创建 18650 电池模型用于渲染展示"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=BATTERY_DIAMETER / 2,
        depth=BATTERY_LENGTH,
        location=(0, 0, 0),
        rotation=(math.pi/2, 0, 0)
    )
    battery = bpy.context.active_object
    battery.name = "Battery_18650"
    
    # 添加电池正极
    bpy.ops.mesh.primitive_cylinder_add(
        radius=3,
        depth=2,
        location=(BATTERY_LENGTH/2 + 1, 0, 0),
        rotation=(math.pi/2, 0, 0)
    )
    positive = bpy.context.active_object
    positive.name = "Battery_Positive"
    
    return battery, positive

# ============== 创建摄像头模型（用于渲染） ==============
def create_camera_model():
    """创建简化的摄像头模型用于渲染展示"""
    # 摄像头主体
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 0)
    )
    camera_body = bpy.context.active_object
    camera_body.name = "Camera_Module"
    camera_body.scale = (30, 25, 8)
    
    # 镜头
    bpy.ops.mesh.primitive_cylinder_add(
        radius=6,
        depth=5,
        location=(0, 0, 6)
    )
    lens = bpy.context.active_object
    lens.name = "Camera_Lens"
    
    return camera_body, lens

# ============== 主程序 ==============
print("开始创建内部组件支架...")

# 创建所有组件
battery_holder = create_battery_holder()
camera_base, camera_platform = create_camera_mount()
battery1, bat1_pos = create_battery_model()
battery2, bat2_pos = create_battery_model()
cam_body, cam_lens = create_camera_model()

# 定位电池到支架中
battery1.location = (0, -((BATTERY_DIAMETER + 5.0)/2), WALL_THICKNESS + BATTERY_DIAMETER/2)
battery1.rotation_euler = (math.pi/2, 0, 0)
bat1_pos.location = (battery1.location[0] + BATTERY_LENGTH/2 + 1, battery1.location[1], battery1.location[2])

battery2.location = (0, (BATTERY_DIAMETER + 5.0)/2, WALL_THICKNESS + BATTERY_DIAMETER/2)
battery2.rotation_euler = (math.pi/2, 0, 0)
bat2_pos.location = (battery2.location[0] + BATTERY_LENGTH/2 + 1, battery2.location[1], battery2.location[2])

# 定位摄像头到平台
cam_body.location = (0, 0, 15 + 6)
cam_lens.location = (0, 0, 15 + 11)

# 设置相机位置以便渲染
bpy.ops.object.camera_add(location=(80, -80, 60), rotation=(1.2, 0, 0.8))
cam = bpy.context.active_object
cam.name = "RenderCamera"
bpy.context.scene.camera = cam

# 设置灯光
bpy.ops.object.light_add(type='SUN', location=(50, 50, 100))
sun = bpy.context.active_object
sun.name = "MainLight"
sun.data.energy = 2.0

bpy.ops.object.light_add(type='AREA', location=(-50, -50, 50))
area = bpy.context.active_object
area.name = "FillLight"
area.data.energy = 1.0

print("内部组件支架创建完成！")
print(f"对象列表:")
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        print(f"  - {obj.name}: {len(obj.data.vertices)} 顶点")

# 保存 Blender 文件
BLEND_PATH = "/root/repos/joycode-robot-mechanical/blender/MD-002_Internal_Bracket.blend"
bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
print(f"\nBlender 文件已保存：{BLEND_PATH}")
