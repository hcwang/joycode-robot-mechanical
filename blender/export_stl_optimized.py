# 导出优化 STL 文件 - 水密检查
import bpy
import bmesh
from pathlib import Path

# 文件路径
BLEND_FILE = "/root/repos/joycode-robot-mechanical/blender/MD-001_Shell_V6.1.blend"
STL_OUTPUT = "/root/repos/joycode-robot-mechanical/stl/MD-001_Shell_V6.1_optimized.stl"

# 加载 Blender 文件
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

# 查找外壳对象
shell_obj = None
for obj in bpy.data.objects:
    if "Shell" in obj.name or obj.name == "Shell_Outer":
        shell_obj = obj
        break

if shell_obj is None:
    # 如果没有找到特定对象，使用活动对象或第一个网格对象
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            shell_obj = obj
            break

if shell_obj is None:
    print("错误：未找到可导出的网格对象")
    exit(1)

print(f"找到对象：{shell_obj.name}")

# 选择对象
bpy.ops.object.select_all(action='DESELECT')
shell_obj.select_set(True)
bpy.context.view_layer.objects.active = shell_obj

# 进入编辑模式进行网格修复
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')

# 移除重复顶点
bpy.ops.mesh.remove_doubles(threshold=0.0001)

# 填充孔洞（尝试使网格水密）
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.fill_holes(sides=4)

# 重新计算法线
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)

# 返回对象模式
bpy.ops.object.mode_set(mode='OBJECT')

# 应用所有变换
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 导出 STL - 使用二进制格式，包含法线
bpy.ops.export_mesh.stl(
    filepath=STL_OUTPUT,
    use_selection=True,
    use_mesh_modifiers=True,
    global_scale=1.0
)

print(f"STL 导出完成：{STL_OUTPUT}")

# 验证 STL 文件
import os
file_size = os.path.getsize(STL_OUTPUT)
print(f"STL 文件大小：{file_size} bytes")

# 简单的流形检查 - 检查顶点数和面数
mesh = shell_obj.data
print(f"顶点数：{len(mesh.vertices)}")
print(f"面数：{len(mesh.polygons)}")

# 欧拉公式检查：V - E + F = 2 (对于封闭流形)
# 每条边被两个面共享，所以 E = 3F/2 (对于三角形网格)
# V - 3F/2 + F = 2 => V - F/2 = 2
expected_euler = len(mesh.vertices) - len(mesh.edges) + len(mesh.polygons)
print(f"欧拉特征值：{expected_euler} (封闭流形应为 2)")

if expected_euler == 2:
    print("✓ 网格是水密的 (manifold)")
else:
    print(f"⚠ 网格可能不是完全水密的 (欧拉特征值={expected_euler})")

print("STL 导出和验证完成！")
