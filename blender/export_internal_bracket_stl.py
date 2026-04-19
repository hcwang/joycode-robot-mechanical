# 导出内部支架 STL 文件
import bpy
import os

# 文件路径
BLEND_FILE = "/root/repos/joycode-robot-mechanical/blender/MD-002_Internal_Bracket.blend"
STL_OUTPUT_DIR = "/root/repos/joycode-robot-mechanical/stl/"

# 确保输出目录存在
os.makedirs(STL_OUTPUT_DIR, exist_ok=True)

# 加载 Blender 文件
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

print("导出内部支架 STL 文件...")

# 导出电池支架
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.name == "BatteryHolder":
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        break

bpy.ops.export_mesh.stl(
    filepath=os.path.join(STL_OUTPUT_DIR, "MD-002_Battery_Holder.stl"),
    use_selection=True,
    use_mesh_modifiers=True,
    global_scale=1.0
)
print("✓ 电池支架 STL 导出完成")

# 导出摄像头底座
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.name == "CameraMount_Base":
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        break

bpy.ops.export_mesh.stl(
    filepath=os.path.join(STL_OUTPUT_DIR, "MD-002_Camera_Mount_Base.stl"),
    use_selection=True,
    use_mesh_modifiers=True,
    global_scale=1.0
)
print("✓ 摄像头底座 STL 导出完成")

# 导出摄像头平台
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.name == "CameraMount_Platform":
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        break

bpy.ops.export_mesh.stl(
    filepath=os.path.join(STL_OUTPUT_DIR, "MD-002_Camera_Mount_Platform.stl"),
    use_selection=True,
    use_mesh_modifiers=True,
    global_scale=1.0
)
print("✓ 摄像头平台 STL 导出完成")

# 验证导出的文件
print("\n导出的 STL 文件:")
for f in os.listdir(STL_OUTPUT_DIR):
    if f.startswith("MD-002_"):
        filepath = os.path.join(STL_OUTPUT_DIR, f)
        size = os.path.getsize(filepath)
        print(f"  {f}: {size} bytes")

print("\nSTL 导出完成！")
